"""Google Veo API client for video generation."""

import asyncio
import logging
import os
import random
import time
from typing import Tuple
from pathlib import Path

from google import genai
from google.genai import types


class VeoClient:
    """Client for Google Veo video generation using GenAI SDK."""

    def __init__(self, project_id: str, model_name: str = "veo-3.1-generate-preview"):
        self.project_id = project_id
        self.location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.model_name = model_name
        self.use_mock = False  # Will be set to True if no API key is found
        self.client = None
        
        # Initialize GenAI client
        try:
            # Try both GEMINI_API_KEY and GOOGLE_API_KEY for compatibility
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                logging.warning("GEMINI_API_KEY or GOOGLE_API_KEY not set. Falling back to mock mode.")
                self.use_mock = True
            else:
                # Initialize the new genai.Client() for Veo API
                self.client = genai.Client(api_key=api_key)
                logging.info(f"VeoClient initialized with API Key for model {model_name}")
        except Exception as e:
            logging.error(f"Failed to initialize Veo client: {e}. Using mock mode.")
            self.use_mock = True

    async def generate_video(
        self, 
        prompt: str, 
        duration_seconds: int, 
        aspect_ratio: str, 
        style: str
    ) -> bytes:
        """Generate video using Google Veo API."""
        # Note: Veo 3 API only supports model and prompt parameters
        # duration_seconds, aspect_ratio, and style are passed but not used by the API
        logging.info(
            f"Generating video for prompt: '{prompt[:50]}...' "
            f"(requested duration: {duration_seconds}s, but Veo generates 8s clips)"
        )
        
        # If in mock mode, raise error to skip this clip
        if self.use_mock:
            logging.warning("VeoClient in mock mode - skipping video generation. Set GOOGLE_API_KEY or GOOGLE_CLOUD_PROJECT to enable real Veo.")
            raise Exception("Mock mode - Veo API not configured")
        
        try:
            # Call Veo API using GenAI SDK
            video_bytes = await asyncio.to_thread(
                self._generate_video_sync,
                prompt,
                duration_seconds,
                aspect_ratio
            )
            
            if video_bytes:
                logging.info(f"Successfully generated video ({len(video_bytes)} bytes)")
                return video_bytes
            
            raise Exception("No video data in Veo response")
            
        except Exception as e:
            logging.error(f"Veo API error: {e}")
            raise

    def _generate_video_sync(
        self, 
        prompt: str, 
        duration_seconds: int, 
        aspect_ratio: str
    ) -> bytes:
        """Synchronous Veo API call with polling."""
        
        try:
            logging.info(f"Calling Veo API: model={self.model_name} (Veo always generates 8s clips)")
            
            # Start video generation using the new API
            operation = self.client.models.generate_videos(
                model=self.model_name,
                prompt=prompt
            )
            
            logging.info(f"Video generation started. Operation: {operation.name}")
            
            # Poll until complete (with timeout)
            max_wait_time = 360  # 6 minutes max (Veo can take 11s to 6min)
            poll_interval = 10  # Check every 10 seconds
            elapsed = 0
            
            while not operation.done and elapsed < max_wait_time:
                time.sleep(poll_interval)
                elapsed += poll_interval
                logging.info(f"Video generation in progress... ({elapsed}s elapsed)")
                # Pass the operation object itself, not the name
                operation = self.client.operations.get(operation)
            
            if not operation.done:
                raise TimeoutError(f"Video generation timed out after {max_wait_time}s")
            
            logging.info("Video generation complete, downloading video...")
            
            # Get the generated video
            generated_video = operation.response.generated_videos[0]
            
            # Download the video file
            video_file = self.client.files.download(file=generated_video.video)
            
            logging.info(f"Successfully generated video ({len(video_file)} bytes)")
            return video_file
                
        except Exception as e:
            logging.error(f"Veo API call failed: {e}")
            raise

    def validate_prompt(self, prompt: str) -> Tuple[bool, str]:
        """Validate video generation prompt."""
        if len(prompt) < 10:
            return False, "Prompt is too short (min 10 characters)."
        if len(prompt) > 1000:
            return False, "Prompt is too long (max 1000 characters)."
        
        # Basic safety checks
        forbidden_keywords = ["nsfw", "violence", "gore"]
        if any(keyword in prompt.lower() for keyword in forbidden_keywords):
            return False, "Prompt contains forbidden content."
        
        return True, "Prompt is valid."
