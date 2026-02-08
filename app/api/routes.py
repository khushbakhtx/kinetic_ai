from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.database import get_db
from ..models.models import Analysis, AnalysisStatus
from ..models.schemas import AnalysisResponse, AnalysisCreate
from ..services.storage_service import storage_service
from ..services.analysis_service import analysis_service
import uuid
import os
import aiofiles

router = APIRouter()

@router.post("/upload", response_model=AnalysisResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    category: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # 1. Validate file
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # 2. Save file temporarily
    file_id = str(uuid.uuid4())
    temp_path = f"temp_{file_id}_{file.filename}"
    async with aiofiles.open(temp_path, "wb") as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # 3. Upload to R2
    # Note: In a production app, you might want to upload to R2 and then process.
    # For MVP, we'll keep it local for extraction then cleanup.
    video_url = await storage_service.upload_video(temp_path, f"videos/{file_id}_{file.filename}")
    
    # 4. Create database record
    new_analysis = Analysis(
        id=uuid.UUID(file_id),
        video_url=video_url,
        category=category,
        status=AnalysisStatus.PROCESSING
    )
    db.add(new_analysis)
    await db.commit()
    await db.refresh(new_analysis)
    
    # 5. Trigger background task
    background_tasks.add_task(analysis_service.process_video_analysis, new_analysis.id, temp_path, category)
    
    return new_analysis

@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Generate fresh presigned URL for playback if it's an R2 URL
    if analysis.video_url and "r2.cloudflarestorage.com" in analysis.video_url:
        # Extract object name from the stored URL
        # Format: endpoint/bucket/object_name
        parts = analysis.video_url.split("/")
        object_name = "/".join(parts[4:]) # Skip endpoint and bucket
        presigned_url = storage_service.get_presigned_url(object_name)
        if presigned_url:
            analysis.video_url = presigned_url
    
    return analysis

@router.get("/categories")
async def get_categories():
    return [
        {"id": "fitness", "name": "Fitness & Sports", "icon": "Dumbbell"},
        {"id": "cooking", "name": "Cooking", "icon": "ChefHat"},
        {"id": "speaking", "name": "Public Speaking", "icon": "Mic"},
        {"id": "diy", "name": "DIY & Repair", "icon": "Wrench"},
        {"id": "driving", "name": "Driving", "icon": "Car"},
        {"id": "music", "name": "Music Performance", "icon": "Music"},
        {"id": "dance", "name": "Dance", "icon": "Sparkles"},
        {"id": "general", "name": "General Activity", "icon": "Scan"}
    ]
