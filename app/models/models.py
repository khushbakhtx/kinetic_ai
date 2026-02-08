from sqlalchemy import Column, String, Enum, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum
from .database import Base

class AnalysisStatus(str, enum.Enum):
    PROCESSING = "PROCESSING"
    RESEARCHING = "RESEARCHING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_url = Column(String, nullable=False)
    category = Column(String, nullable=False)
    status = Column(Enum(AnalysisStatus), default=AnalysisStatus.PROCESSING)
    created_at = Column(DateTime, default=datetime.utcnow)
    results = Column(JSON, nullable=True) # Stage 1 Analysis
    research_results = Column(JSON, nullable=True) # Stage 2 Marathon Agent Research
    coaching_program = Column(JSON, nullable=True) # Stage 3 Generated Plan
    additional_metadata = Column(JSON, nullable=True)
