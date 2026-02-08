from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum

class AnalysisStatus(str, Enum):
    PROCESSING = "PROCESSING"
    RESEARCHING = "RESEARCHING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class BugLocation(BaseModel):
    x: int
    y: int

class Bug(BaseModel):
    id: Optional[str] = None
    timestamp: float
    severity: str
    title: str
    description: str
    root_cause: Optional[str] = None
    injury_risk: Optional[str] = None
    recommendation: str
    confidence: Optional[float] = None
    location: Optional[BugLocation] = None

    class Config:
        extra = 'ignore'

class AnalysisResult(BaseModel):
    bugs: List[Bug]
    overall_assessment: Optional[str] = None
    spatial_temporal_summary: Optional[str] = None
    key_strengths: Optional[List[str]] = None
    priority_fixes: Optional[List[str]] = None

    class Config:
        extra = 'ignore'

class AnalysisBase(BaseModel):
    video_url: str
    category: str

    class Config:
        extra = 'ignore'

class AnalysisCreate(AnalysisBase):
    pass

class AnalysisResponse(AnalysisBase):
    id: UUID
    status: AnalysisStatus
    created_at: datetime
    results: Optional[Dict[str, Any]] = None
    research_results: Optional[Dict[str, Any]] = None
    coaching_program: Optional[Dict[str, Any]] = None
    additional_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
        extra = 'ignore'
