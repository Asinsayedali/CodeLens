"""Documentation API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.database import get_db, Project, Documentation
from app.services.doc_generator import doc_generator
from app.services.watsonx_client import watsonx_client


router = APIRouter(prefix="/docs", tags=["documentation"])


# Request/Response Models
class DocGenerationRequest(BaseModel):
    """Request to generate documentation"""
    section: Optional[str] = None  # 'overview', 'getting_started', 'architecture', 'api', or None for all


class DocGenerationResponse(BaseModel):
    """Response for documentation generation"""
    status: str
    message: str
    documentation: Optional[Dict[str, str]] = None


class ConnectionTestResponse(BaseModel):
    """Response for connection test"""
    status: str
    model_id: Optional[str] = None
    project_id: Optional[str] = None
    test_response: Optional[str] = None
    error: Optional[str] = None


# Endpoints

@router.get("/test-connection", response_model=ConnectionTestResponse)
async def test_watsonx_connection():
    """
    Test connection to watsonx.ai
    
    Returns:
        Connection status and details
    """
    try:
        result = watsonx_client.test_connection()
        return ConnectionTestResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")


@router.post("/projects/{project_id}/generate", response_model=DocGenerationResponse)
async def generate_documentation(
    project_id: int,
    request: DocGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered documentation for a project
    
    Args:
        project_id: Project ID
        request: Documentation generation request
        background_tasks: FastAPI background tasks
        db: Database session
    
    Returns:
        Generated documentation
    """
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Generate documentation based on section
        if request.section == "overview":
            doc = doc_generator.generate_project_overview(project)
            documentation = {"overview": doc}
        
        elif request.section == "getting_started":
            doc = doc_generator.generate_getting_started(project)
            documentation = {"getting_started": doc}
        
        elif request.section == "architecture":
            doc = doc_generator.generate_architecture_docs(project)
            documentation = {"architecture": doc}
        
        elif request.section == "api":
            doc = doc_generator.generate_api_docs(project)
            documentation = {"api": doc}
        
        else:
            # Generate all sections
            documentation = doc_generator.generate_all_docs(project)
        
        # Store documentation in database
        _store_documentation(db, project.id, documentation)
        
        return DocGenerationResponse(
            status="success",
            message="Documentation generated successfully",
            documentation=documentation
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate documentation: {str(e)}")


@router.get("/projects/{project_id}", response_model=Dict[str, Any])
async def get_project_documentation(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get existing documentation for a project
    
    Args:
        project_id: Project ID
        db: Database session
    
    Returns:
        Project documentation
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get all documentation sections
    docs = db.query(Documentation).filter(
        Documentation.project_id == project_id
    ).order_by(Documentation.order_index).all()
    
    if not docs:
        raise HTTPException(
            status_code=404,
            detail="Documentation not generated yet. Use POST /docs/projects/{project_id}/generate to generate it."
        )
    
    # Convert to dictionary
    documentation = {doc.section_name: doc.content for doc in docs}
    
    return {
        "project_id": project.id,
        "project_name": project.name,
        "documentation": documentation,
        "generated_at": docs[0].created_at if docs else None
    }


@router.get("/projects/{project_id}/sections/{section}")
async def get_documentation_section(
    project_id: int,
    section: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific documentation section
    
    Args:
        project_id: Project ID
        section: Section name ('overview', 'getting_started', 'architecture', 'api')
        db: Database session
    
    Returns:
        Documentation section content
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get specific section
    doc = db.query(Documentation).filter(
        Documentation.project_id == project_id,
        Documentation.section_name == section
    ).first()
    
    if not doc:
        raise HTTPException(status_code=404, detail=f"Section '{section}' not found")
    
    return {
        "section": section,
        "content": doc.content
    }


@router.delete("/projects/{project_id}")
async def delete_documentation(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete documentation for a project
    
    Args:
        project_id: Project ID
        db: Database session
    
    Returns:
        Success message
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete all documentation for this project
    db.query(Documentation).filter(Documentation.project_id == project_id).delete()
    db.commit()
    
    return {"message": "Documentation deleted successfully"}


@router.post("/projects/{project_id}/regenerate/{section}")
async def regenerate_section(
    project_id: int,
    section: str,
    db: Session = Depends(get_db)
):
    """
    Regenerate a specific documentation section
    
    Args:
        project_id: Project ID
        section: Section to regenerate
        db: Database session
    
    Returns:
        Regenerated section
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Generate the specific section
        if section == "overview":
            content = doc_generator.generate_project_overview(project)
        elif section == "getting_started":
            content = doc_generator.generate_getting_started(project)
        elif section == "architecture":
            content = doc_generator.generate_architecture_docs(project)
        elif section == "api":
            content = doc_generator.generate_api_docs(project)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid section: {section}")
        
        # Update documentation
        if not project.documentation:
            project.documentation = {}
        project.documentation[section] = content
        db.commit()
        
        return {
            "section": section,
            "content": content,
            "message": "Section regenerated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to regenerate section: {str(e)}")


# Made with Bob

# Helper functions

def _store_documentation(db: Session, project_id: int, documentation: Dict[str, str]):
    """Store documentation sections in database"""
    # Delete existing documentation
    db.query(Documentation).filter(Documentation.project_id == project_id).delete()
    
    # Create new documentation entries
    section_order = {
        'overview': 1,
        'getting_started': 2,
        'architecture': 3,
        'api': 4,
    }
    
    for section_name, content in documentation.items():
        if content:  # Only store non-empty sections
            doc = Documentation(
                project_id=project_id,
                section_name=section_name,
                content=content,
                order_index=section_order.get(section_name, 99)
            )
            db.add(doc)
    
    db.commit()


def _get_section_order(section: str) -> int:
    """Get order index for a section"""
    order_map = {
        'overview': 1,
        'getting_started': 2,
        'architecture': 3,
        'api': 4,
    }
    return order_map.get(section, 99)
