import google.generativeai as genai
import os
import json
from typing import Dict, Any, List
from ..models.models import Analysis, AnalysisStatus
from ..models.database import AsyncSessionLocal
from sqlalchemy import update
import asyncio

class ResearchService:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-3-pro-preview')

    async def conduct_marathon_research(self, analysis_id: str, bugs: List[Dict[str, Any]], category: str):
        """
        Phase 2: Marathon Agent - Performs deep research and program generation.
        """
        async with AsyncSessionLocal() as db:
            # Update status to RESEARCHING
            await db.execute(update(Analysis).where(Analysis.id == analysis_id).values(status=AnalysisStatus.RESEARCHING))
            await db.commit()

        # Build research prompt
        bug_summaries = [f"- {b['title']}: {b['root_cause']}" for b in bugs]
        prompt = f"""
        You are the Marathon Coaching Agent for Kinetic AI.
        Specific Issues Identified:
        {chr(10).join(bug_summaries)}
        
        Category: {category}
        
        TASK:
        1. Deeply analyze these failure patterns and physical/systemic inefficiencies.
        2. Conduct a simulated research into industry-standard documentation, scientific literature, and logical principles.
        3. Create a comprehensive 6-Week Mastery/Correction Program.
        
        Respond ONLY in JSON with this exact structure:
        {{
          "research_summary": {{
            "scientific_explanation": "Detailed biomechanical or logical explanation",
            "impact_analysis": "Why this causes injury or systemic failure",
            "correction_approach": "Evidence-based approach used for this program"
          }},
          "program": {{
            "title": "6-Week Mastery & Optimization Plan",
            "weeks": [
              {{
                "week_range": "Week 1-2",
                "focus": "Foundations & Mobility",
                "exercises": [
                  {{ 
                    "name": "Exercise/Task Name", 
                    "dosage": "3x10 or 30sec", 
                    "cue": "Specific tip",
                    "youtube_link": "https://www.youtube.com/results?search_query=..."
                  }}
                ]
              }}
            ]
          }},
          "checkpoints": [
            "Upload re-assessment video after Week 2",
            "Upload re-assessment video after Week 4"
          ],
          "success_metrics": [
            "Measurable metric 1",
            "Measurable metric 2"
          ]
        }}
        """

        # Call Gemini for the deep dive
        response = await asyncio.to_thread(self.model.generate_content, prompt)
        
        try:
            text = response.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            research_data = json.loads(text)
            
            async with AsyncSessionLocal() as db:
                await db.execute(update(Analysis).where(Analysis.id == analysis_id).values(
                    status=AnalysisStatus.COMPLETED,
                    research_results=research_data.get("research_summary"),
                    coaching_program={
                        "program": research_data.get("program"),
                        "checkpoints": research_data.get("checkpoints"),
                        "success_metrics": research_data.get("success_metrics")
                    }
                ))
                await db.commit()
                
        except Exception as e:
            print(f"Marathon Agent failed: {e}")
            async with AsyncSessionLocal() as db:
                await db.execute(update(Analysis).where(Analysis.id == analysis_id).values(status=AnalysisStatus.FAILED))
                await db.commit()

research_service = ResearchService()
