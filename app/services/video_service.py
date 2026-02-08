import cv2
import os
import asyncio
from typing import List

class VideoService:
    async def extract_frames(self, video_path: str, output_dir: str, interval_seconds: int = 2, max_frames: int = 50) -> List[str]:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps

        # Adjust interval if duration is too long to stay under max_frames
        if duration / interval_seconds > max_frames:
            interval_seconds = int(duration / max_frames) + 1

        frame_paths = []
        count = 0
        success = True
        
        while success:
            # Set position in milliseconds
            cap.set(cv2.CAP_PROP_POS_MSEC, count * interval_seconds * 1000)
            success, image = cap.read()
            if success:
                frame_filename = f"frame_{count}.jpg"
                frame_path = os.path.join(output_dir, frame_filename)
                
                # Resize to 720p if larger to save bandwidth/tokens
                height, width = image.shape[:2]
                if height > 720:
                    aspect_ratio = width / height
                    new_height = 720
                    new_width = int(new_height * aspect_ratio)
                    image = cv2.resize(image, (new_width, new_height))

                cv2.imwrite(frame_path, image)
                frame_paths.append(frame_path)
                count += 1
                
                if count >= max_frames:
                    break
            
            await asyncio.sleep(0) # Yield for async

        cap.release()
        return frame_paths

video_service = VideoService()
