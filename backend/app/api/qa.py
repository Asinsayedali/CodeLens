"""
Q&A API endpoints
"""
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database import get_db, Project
from app.services.qa_engine import qa_engine
from app.services.embedding_service import embedding_service
from app.services.repo_parser import RepoParser


router = APIRouter(prefix="/api/projects", tags=["qa"])


# ── Request / Response models ──────────────────────────────────────────────────

class QuestionRequest(BaseModel):
    question: str
    include_history: bool = True


class CodeSnippet(BaseModel):
    file_path: str
    code: str
    similarity: float


class QuestionResponse(BaseModel):
    answer: str
    code_snippets: List[CodeSnippet]
    confidence: float
    timestamp: str | None


class HistoryEntry(BaseModel):
    id: int
    question: str
    answer: str
    timestamp: str


class SuggestedQuestionsResponse(BaseModel):
    suggestions: List[str]


class EmbeddingGenerationResponse(BaseModel):
    message: str
    embeddings_created: int


# ── Helpers ────────────────────────────────────────────────────────────────────

SUPPORTED_EXTENSIONS = {'.py', '.js', '.ts', '.tsx', '.jsx'}
IGNORE_DIRS = {
    'node_modules', 'venv', 'env', '.venv', '__pycache__',
    '.git', '.idea', '.vscode', 'dist', 'build', 'target',
    '.pytest_cache', '.mypy_cache', 'coverage', '.next',
}


def _read_code_files(root: Path) -> dict:
    """Walk root and return {relative_path: content} for all supported files."""
    code_files = {}
    for file_path in root.rglob("*"):
        # Skip ignored directories
        if any(part in IGNORE_DIRS for part in file_path.parts):
            continue
        if file_path.is_file() and file_path.suffix in SUPPORTED_EXTENSIONS:
            try:
                relative = str(file_path.relative_to(root))
                code_files[relative] = file_path.read_text(encoding='utf-8', errors='ignore')
            except Exception as e:
                print(f"Warning: could not read {file_path}: {e}")
    return code_files


def _get_code_files(project: Project) -> tuple[dict, str | None]:
    """
    Return (code_files_dict, temp_dir_to_cleanup).
    Tries local_path first; re-clones from repo_url if the path is gone.
    Raises HTTPException if neither source is available.
    """
    local = Path(project.local_path) if project.local_path else None

    # ── Case 1: local path still exists ───────────────────────────────────────
    if local and local.exists():
        return _read_code_files(local), None

    # ── Case 2: local path gone → re-clone from repo_url ─────────────────────
    if project.repo_url:
        print(f"local_path gone, re-cloning from {project.repo_url} …")
        parser = RepoParser()
        try:
            cloned_path = parser.clone_repository(project.repo_url)
            code_files = _read_code_files(Path(cloned_path))
            return code_files, cloned_path   # caller must clean up
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Could not re-clone repository: {e}",
            )

    # ── Case 3: nothing we can do ─────────────────────────────────────────────
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=(
            "Project source files are no longer available on this machine "
            "and no repo URL is stored to re-clone them."
        ),
    )


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/{project_id}/qa", response_model=QuestionResponse)
async def ask_question(
    project_id: int,
    request: QuestionRequest,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    result = qa_engine.ask_question(
        db=db,
        project_id=project_id,
        question=request.question,
        include_history=request.include_history,
    )

    return QuestionResponse(
        answer=result['answer'],
        code_snippets=[CodeSnippet(**s) for s in result['code_snippets']],
        confidence=result['confidence'],
        timestamp=result['timestamp'],
    )


@router.get("/{project_id}/qa/history", response_model=List[HistoryEntry])
async def get_qa_history(
    project_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    history = qa_engine.get_conversation_history(db=db, project_id=project_id, limit=limit)
    return [HistoryEntry(**e) for e in history]


@router.get("/{project_id}/qa/suggestions", response_model=SuggestedQuestionsResponse)
async def get_suggested_questions(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    suggestions = qa_engine.get_suggested_questions(db=db, project_id=project_id)
    return SuggestedQuestionsResponse(suggestions=suggestions)


@router.post("/{project_id}/qa/embeddings", response_model=EmbeddingGenerationResponse)
async def generate_embeddings(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    temp_dir: str | None = None
    try:
        code_files, temp_dir = _get_code_files(project)

        if not code_files:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "No supported source files found in the repository "
                    f"(looked for {', '.join(sorted(SUPPORTED_EXTENSIONS))})."
                ),
            )

        count = embedding_service.generate_embeddings_for_project(
            db=db,
            project_id=project_id,
            code_files=code_files,
        )

        return EmbeddingGenerationResponse(
            message=f"Generated embeddings for {len(code_files)} files ({count} chunks).",
            embeddings_created=count,
        )

    finally:
        # Always clean up any re-cloned temp dir
        if temp_dir:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

# Made with Bob
