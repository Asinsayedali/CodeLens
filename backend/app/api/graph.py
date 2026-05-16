"""API endpoints for graph data"""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db, GraphNode, GraphEdge, Project
from app.schemas.graph import (
    GraphNodeResponse,
    GraphEdgeResponse,
    GraphData,
    ReactFlowGraphData,
    NodeDetailsResponse
)
from app.services.graph_serializer import GraphSerializer
from app.services.watsonx_client import watsonx_client

router = APIRouter()


class NodeQuestionRequest(BaseModel):
    question: str

class NodeAnswerResponse(BaseModel):
    answer: str
    files_used: List[str]


def _get_project_root(project: Project):
    """Returns (root_path, temp_dir_or_None). Tries local_path, then clones via git."""
    if project.local_path and Path(project.local_path).exists():
        return Path(project.local_path), None
    if project.repo_url:
        temp_dir = tempfile.mkdtemp(prefix='codelens_ask_')
        try:
            subprocess.run(
                ['git', 'clone', '--depth', '1', project.repo_url, temp_dir],
                check=True, capture_output=True, timeout=120,
            )
            return Path(temp_dir), temp_dir
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise RuntimeError(f"Failed to clone repository: {e}")
    return None, None

def _read_project_files(root: Path, file_paths: set) -> dict:
    """Read specific files from project root. Returns {rel_path: content}."""
    contents = {}
    for rel_path in file_paths:
        full_path = root / rel_path
        if full_path.exists() and full_path.is_file():
            try:
                contents[rel_path] = full_path.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                pass
    return contents

def _extract_code_window(content: str, line_number, window: int = 80) -> str:
    """Extract a window of lines around line_number (1-indexed)."""
    lines = content.split('\n')
    if not line_number:
        return '\n'.join(lines[:100])
    start = max(0, line_number - 1)
    end = min(len(lines), start + window)
    return '\n'.join(lines[start:end])

def _build_node_context(target, related: list, file_contents: dict) -> str:
    """Build focused code context: target node's code + related nodes' snippets."""
    parts = []
    if target.file_path and target.file_path in file_contents:
        code = _extract_code_window(file_contents[target.file_path], target.line_number, 80)
        parts.append(
            f"## `{target.name}` ({target.node_type}) in `{target.file_path}`:\n```\n{code}\n```"
        )
    seen = set()
    for rn in related[:8]:
        if not rn.file_path or rn.file_path not in file_contents:
            continue
        key = (rn.file_path, rn.line_number or 0)
        if key in seen:
            continue
        seen.add(key)
        code = _extract_code_window(file_contents[rn.file_path], rn.line_number, 40)
        parts.append(
            f"## `{rn.name}` ({rn.node_type}) in `{rn.file_path}`:\n```\n{code}\n```"
        )
    return '\n\n'.join(parts) or "No source code available."


@router.get("/{project_id}/graph", response_model=GraphData)
def get_project_graph(project_id: int, db: Session = Depends(get_db)):
    """Get the complete dependency graph for a project"""
    
    # Get all nodes for the project
    nodes = db.query(GraphNode).filter(GraphNode.project_id == project_id).all()
    
    if not nodes:
        raise HTTPException(status_code=404, detail="No graph data found for this project")
    
    # Get all edges for the project
    edges = db.query(GraphEdge).filter(GraphEdge.project_id == project_id).all()
    
    # Calculate stats
    node_types = {}
    for node in nodes:
        node_types[node.node_type] = node_types.get(node.node_type, 0) + 1
    
    edge_types = {}
    for edge in edges:
        edge_types[edge.edge_type] = edge_types.get(edge.edge_type, 0) + 1
    
    return GraphData(
        nodes=[GraphNodeResponse.model_validate(node) for node in nodes],
        edges=[GraphEdgeResponse.model_validate(edge) for edge in edges],
        stats={
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'node_types': node_types,
            'edge_types': edge_types
        }
    )


@router.get("/{project_id}/graph/react-flow", response_model=ReactFlowGraphData)
def get_react_flow_graph(
    project_id: int,
    layout: str = Query("hierarchical", description="Layout algorithm: 'hierarchical' or 'force'"),
    db: Session = Depends(get_db)
):
    """Get graph data in React Flow compatible format"""
    
    # Get all nodes for the project
    nodes = db.query(GraphNode).filter(GraphNode.project_id == project_id).all()
    
    if not nodes:
        raise HTTPException(status_code=404, detail="No graph data found for this project")
    
    # Get all edges for the project
    edges = db.query(GraphEdge).filter(GraphEdge.project_id == project_id).all()
    
    # Calculate stats
    node_types = {}
    for node in nodes:
        node_types[node.node_type] = node_types.get(node.node_type, 0) + 1
    
    edge_types = {}
    for edge in edges:
        edge_types[edge.edge_type] = edge_types.get(edge.edge_type, 0) + 1
    
    stats = {
        'total_nodes': len(nodes),
        'total_edges': len(edges),
        'node_types': node_types,
        'edge_types': edge_types
    }
    
    # Convert to React Flow format
    serializer = GraphSerializer()
    
    # Use hierarchical layout if requested
    if layout == "hierarchical":
        serializer.calculate_hierarchical_layout(
            [GraphNodeResponse.model_validate(n) for n in nodes],
            [GraphEdgeResponse.model_validate(e) for e in edges]
        )
    
    return serializer.serialize_to_react_flow(
        [GraphNodeResponse.model_validate(n) for n in nodes],
        [GraphEdgeResponse.model_validate(e) for e in edges],
        stats
    )


@router.get("/{project_id}/graph/nodes", response_model=List[GraphNodeResponse])
def get_project_nodes(
    project_id: int,
    node_type: str | None = None,
    db: Session = Depends(get_db)
):
    """Get all nodes for a project, optionally filtered by type"""
    
    query = db.query(GraphNode).filter(GraphNode.project_id == project_id)
    
    if node_type:
        query = query.filter(GraphNode.node_type == node_type)
    
    nodes = query.all()
    
    return [GraphNodeResponse.model_validate(node) for node in nodes]


@router.post("/{project_id}/graph/node/{node_id:path}/ask")
async def ask_about_node(
    project_id: int,
    node_id: str,
    request: NodeQuestionRequest,
    db: Session = Depends(get_db),
):
    """Ask a question about a specific node using its actual source code as context."""
    node = db.query(GraphNode).filter(
        GraphNode.project_id == project_id,
        GraphNode.node_id == node_id
    ).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    incoming = db.query(GraphEdge).filter(
        GraphEdge.project_id == project_id,
        GraphEdge.target_node_id == node_id
    ).all()
    outgoing = db.query(GraphEdge).filter(
        GraphEdge.project_id == project_id,
        GraphEdge.source_node_id == node_id
    ).all()

    related_ids = {e.source_node_id for e in incoming} | {e.target_node_id for e in outgoing}
    related_nodes = db.query(GraphNode).filter(
        GraphNode.node_id.in_(related_ids)
    ).all() if related_ids else []

    file_paths = set()
    if node.file_path:
        file_paths.add(node.file_path)
    for rn in related_nodes:
        if rn.file_path:
            file_paths.add(rn.file_path)

    temp_dir = None
    try:
        root, temp_dir = _get_project_root(project)
        if not root:
            raise HTTPException(
                status_code=422,
                detail="Source files not available. No local path or repo URL stored."
            )
        file_contents = _read_project_files(root, file_paths)
        context = _build_node_context(node, related_nodes, file_contents)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert code analyst. Answer questions about a specific piece of code "
                    "using only the provided source code snippets. Be precise and reference actual "
                    "code. Explain what the code does, what parameters it takes, what it returns, "
                    "and how it relates to connected components. Output clean markdown."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Here is the source code for `{node.name}` ({node.node_type}) "
                    f"and its related code:\n\n{context}\n\n"
                    f"Question: {request.question}"
                )
            }
        ]

        try:
            answer = watsonx_client.chat(messages=messages, max_tokens=1024, temperature=0.2)
            if not answer or len(answer.strip()) < 10:
                raise ValueError("Empty answer from LLM")
        except Exception as e:
            answer = f"Could not generate answer: {e}"

        return NodeAnswerResponse(answer=answer, files_used=list(file_contents.keys()))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing node question: {e}")
    finally:
        if temp_dir:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass


@router.get("/{project_id}/graph/node/{node_id:path}/details", response_model=NodeDetailsResponse)
def get_node_details_extended(project_id: int, node_id: str, db: Session = Depends(get_db)):
    """Get extended details for a specific node including relationships"""
    
    # Get the node
    node = db.query(GraphNode).filter(
        GraphNode.project_id == project_id,
        GraphNode.node_id == node_id
    ).first()
    
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Get incoming edges
    incoming_edges = db.query(GraphEdge).filter(
        GraphEdge.project_id == project_id,
        GraphEdge.target_node_id == node_id
    ).all()
    
    # Get outgoing edges
    outgoing_edges = db.query(GraphEdge).filter(
        GraphEdge.project_id == project_id,
        GraphEdge.source_node_id == node_id
    ).all()
    
    # Get related nodes (nodes connected by incoming/outgoing edges)
    related_node_ids = set()
    for edge in incoming_edges:
        related_node_ids.add(edge.source_node_id)
    for edge in outgoing_edges:
        related_node_ids.add(edge.target_node_id)
    
    related_nodes = []
    if related_node_ids:
        related_nodes = db.query(GraphNode).filter(
            GraphNode.project_id == project_id,
            GraphNode.node_id.in_(related_node_ids)
        ).all()
    
    # Build metadata
    import json
    metadata = {}
    if node.node_metadata:
        try:
            metadata = json.loads(node.node_metadata)
        except json.JSONDecodeError:
            pass
    
    metadata['incoming_count'] = len(incoming_edges)
    metadata['outgoing_count'] = len(outgoing_edges)
    metadata['related_count'] = len(related_nodes)
    
    return NodeDetailsResponse(
        node=GraphNodeResponse.model_validate(node),
        incoming_edges=[GraphEdgeResponse.model_validate(e) for e in incoming_edges],
        outgoing_edges=[GraphEdgeResponse.model_validate(e) for e in outgoing_edges],
        related_nodes=[GraphNodeResponse.model_validate(n) for n in related_nodes],
        metadata=metadata
    )


@router.get("/{project_id}/graph/node/{node_id:path}", response_model=GraphNodeResponse)
def get_node_details(project_id: int, node_id: str, db: Session = Depends(get_db)):
    """Get details for a specific node"""

    node = db.query(GraphNode).filter(
        GraphNode.project_id == project_id,
        GraphNode.node_id == node_id
    ).first()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    return GraphNodeResponse.model_validate(node)


@router.get("/{project_id}/graph/edges", response_model=List[GraphEdgeResponse])
def get_project_edges(
    project_id: int,
    edge_type: str | None = None,
    db: Session = Depends(get_db)
):
    """Get all edges for a project, optionally filtered by type"""
    
    query = db.query(GraphEdge).filter(GraphEdge.project_id == project_id)
    
    if edge_type:
        query = query.filter(GraphEdge.edge_type == edge_type)
    
    edges = query.all()
    
    return [GraphEdgeResponse.model_validate(edge) for edge in edges]

# Made with Bob
