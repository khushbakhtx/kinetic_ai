import boto3
import os
from dotenv import load_dotenv
from botocore.config import Config

load_dotenv()

class StorageService:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=os.getenv("R2_ENDPOINT"),
            aws_access_key_id=os.getenv("R2_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("R2_SECRET_KEY"),
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        self.bucket = os.getenv("R2_BUCKET")

    async def upload_video(self, file_path: str, object_name: str):
        try:
            # Explicitly set ContentType for video playback compatibility
            self.s3.upload_file(
                file_path, 
                self.bucket, 
                object_name,
                ExtraArgs={'ContentType': 'video/mp4'}
            )
            return f"{os.getenv('R2_ENDPOINT')}/{self.bucket}/{object_name}"
        except Exception as e:
            print(f"Error uploading to R2: {e}")
            raise e

    def get_presigned_url(self, object_name: str, expiration=3600):
        try:
            response = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': object_name},
                ExpiresIn=expiration
            )
            return response
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return None

storage_service = StorageService()
