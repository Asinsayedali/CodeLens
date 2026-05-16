"""Project schemas for API requests and responses"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str
    repo_url: Optional[str] = None
    local_path: str


class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = None
    status: Optional[str] = None
    total_files: Optional[int] = None
    total_lines: Optional[int] = None
    last_analyzed: Optional[datetime] = None


class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: int
    language: Optional[str] = None
    total_files: int = 0
    total_lines: int = 0
    created_at: datetime
    last_analyzed: Optional[datetime] = None
    status: str
    
    class Config:
        from_attributes = True


class AnalyzeRequest(BaseModel):
    """Schema for analysis request"""
    path: str = Field(..., description="Local path or GitHub URL to analyze")
    name: Optional[str] = Field(None, description="Optional project name")


class AnalysisProgress(BaseModel):
    """Schema for analysis progress updates"""
    status: str
    message: str
    progress: int = Field(..., ge=0, le=100)
    current_file: Optional[str] = None

# Made with Bob
