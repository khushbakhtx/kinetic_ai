from .storage_service import storage_service
from .video_service import video_service
from .gemini_service import gemini_service
from ..models.models import Analysis, AnalysisStatus
from ..models.database import AsyncSessionLocal
import os
import shutil
import tempfile
from sqlalchemy import update
from uuid import UUID
import asyncio

class AnalysisService:
    async def process_video_analysis(self, analysis_id: UUID, temp_video_path: str, category: str):
        temp_dir = tempfile.mkdtemp()
        try:
            # 1. Extract frames
            frames_dir = os.path.join(temp_dir, "frames")
            frame_paths = await video_service.extract_frames(temp_video_path, frames_dir)
            
            # 2. Analyze with Gemini (Phase 1: Reasoning & Cause-Effect)
            results = await gemini_service.analyze_video_frames(frame_paths, category)
            
            # 3. Update database with Phase 1 results
            async with AsyncSessionLocal() as db:
                stmt = update(Analysis).where(Analysis.id == analysis_id).values(
                    status=AnalysisStatus.RESEARCHING,
                    results=results
                )
                await db.execute(stmt)
                await db.commit()
            
            # 4. Trigger Phase 2: Marathon Agent Research
            from .research_service import research_service
            # We don't await this so it can run in the background for a long time
            asyncio.create_task(research_service.conduct_marathon_research(
                analysis_id, 
                results.get("bugs", []), 
                category
            ))
                
        except Exception as e:
            print(f"Error in background processing: {e}")
            async with AsyncSessionLocal() as db:
                stmt = update(Analysis).where(Analysis.id == analysis_id).values(
                    status=AnalysisStatus.FAILED
                )
                await db.execute(stmt)
                await db.commit()
        finally:
            # Cleanup
            shutil.rmtree(temp_dir)
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)

analysis_service = AnalysisService()
