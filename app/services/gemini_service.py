import google.generativeai as genai
import os
from PIL import Image
from typing import List, Dict, Any
import json
from ..prompts.prompts import BASE_SYSTEM_PROMPT, CATEGORY_PROMPTS
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        # Upgraded to Gemini 3 Pro Preview for maximum analytical depth
        self.model = genai.GenerativeModel('gemini-3-pro-preview')

    async def analyze_video_frames(self, frame_paths: List[str], category: str) -> Dict[str, Any]:
        category_prompt = CATEGORY_PROMPTS.get(category, "General activity analysis.")
        prompt = f"{BASE_SYSTEM_PROMPT}\n\nCategory Specific Instructions:\n{category_prompt}"

        # Load images
        images = [Image.open(p) for p in frame_paths]

        # Call Gemini
        response = await asyncio.to_thread(self.model.generate_content, [prompt] + images)
        
        try:
            # Extract JSON from response
            text = response.text
            # Sometimes Gemini wraps JSON in code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            return json.loads(text)
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            print(f"Raw response: {response.text}")
            return {"bugs": [], "overall_assessment": "Error analyzing video.", "error": str(e)}

import asyncio
gemini_service = GeminiService()
