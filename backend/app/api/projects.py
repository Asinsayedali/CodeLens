"""API endpoints for project management"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.project import (
    ProjectResponse,
    ProjectCreate,
    AnalyzeRequest,
    AnalysisProgress
)
from app.services.analysis_service import AnalysisService

router = APIRouter()


@router.get("", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    """List all projects"""
    service = AnalysisService(db)
    projects = service.list_projects()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project"""
    service = AnalysisService(db)
    project = service.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


@router.post("/analyze", response_model=ProjectResponse)
def analyze_repository(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Analyze a repository (local path or GitHub URL)
    
    This endpoint starts the analysis process and returns immediately.
    The analysis runs in the background.
    """
    try:
        service = AnalysisService(db)
        project = service.analyze_repository(request.path, request.name)
        return project
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project and all its data"""
    service = AnalysisService(db)
    success = service.delete_project(project_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"message": "Project deleted successfully"}

# Made with Bob
