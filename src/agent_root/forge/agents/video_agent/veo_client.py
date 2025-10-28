"""Mock Google Veo API client for video generation."""

import asyncio
import logging
import os
import random
import time
from typing import Tuple
import numpy as np
from pathlib import Path

try:
    from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
    from moviepy.config import check as check_moviepy
    MOVIEPY_AVAILABLE = True
except ImportError:
    logging.warning("MoviePy not available. Videos will use simple mock bytes.")
    MOVIEPY_AVAILABLE = False

# Mock bytes for a tiny MP4 file (minimal valid structure)
# This is a very basic, non-playable MP4 header for demonstration.
# Real video data would be much larger and more complex.
MOCK_MP4_BYTES = (
    b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom\x00\x00\x00\x00"
    b"\x00\x00\x00\x08free\x00\x00\x00\x00\x00\x00\x00\x08mdat"
)


class VeoClient:
    """Mock client for Google Veo video generation."""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.location = "us-central1"  # Default location
        logging.info(f"VeoClient initialized for project {project_id} in {self.location}")
        if project_id == "CHANGE-ME":
            logging.warning("GOOGLE_CLOUD_PROJECT is set to 'CHANGE-ME'. Please configure your project ID for actual Veo API calls.")

    async def generate_video(self, prompt: str, duration_seconds: int, aspect_ratio: str, style: str) -> bytes:
        """Mocks video generation using Google Veo."""
        logging.info(
            f"Generating mock video for prompt: '{prompt[:50]}...' "
            f"(duration: {duration_seconds}s, aspect_ratio: {aspect_ratio}, style: {style})"
        )
        
        # Simulate API call delay
        await self._simulate_delay(duration_seconds)
        
        # Check if MoviePy is available dynamically
        try:
            from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
            # Generate a proper video that QuickTime can play
            return self._generate_real_video(prompt, duration_seconds, aspect_ratio)
        except ImportError:
            # Return mock video bytes
            logging.warning("MoviePy not available, using mock bytes. Install with: uv add moviepy")
            return MOCK_MP4_BYTES

    def validate_prompt(self, prompt: str) -> Tuple[bool, str]:
        """Mocks prompt validation."""
        if len(prompt) < 10:
            return False, "Prompt is too short."
        if "invalid_keyword" in prompt.lower():
            return False, "Prompt contains invalid keywords."
        return True, "Prompt is valid."

    async def _simulate_delay(self, duration: int):
        """Simulates network delay for API calls."""
        await asyncio.sleep(random.uniform(1, 3)) # Simulate 1-3 seconds network latency
    
    def _generate_real_video(self, prompt: str, duration_seconds: int, aspect_ratio: str) -> bytes:
        """Generate a real MP4 video using MoviePy that QuickTime can play."""
        import tempfile
        
        # Parse aspect ratio
        width, height = 1920, 1080  # Default 16:9
        if aspect_ratio == "9:16":
            width, height = 1080, 1920
        elif aspect_ratio == "1:1":
            width, height = 1080, 1080
        
        # Create a gradient background
        background_colors = [
            (147, 51, 234),   # Purple
            (236, 72, 153),   # Pink
            (59, 130, 246),   # Blue
        ]
        
        # Pick random gradient colors
        color1 = random.choice(background_colors)
        color2 = random.choice(background_colors)
        
        # Create gradient background clip
        gradient = ColorClip(size=(width, height), color=color1, duration=duration_seconds)
        
        # Add text overlay
        text_lines = prompt[:100].split()  # First 100 chars
        text = '\n'.join([' '.join(text_lines[i:i+5]) for i in range(0, len(text_lines), 5)])
        
        try:
            # Create text clip
            txt_clip = TextClip(
                text,
                fontsize=48,
                color='white',
                font='Arial',
                align='center',
                method='label',
                size=(width * 0.8, None)
            ).set_duration(duration_seconds).set_position('center')
            
            # Add subtle fade in/out
            txt_clip = txt_clip.crossfadein(0.5).crossfadeout(0.5)
            
            # Composite text over background
            video = CompositeVideoClip([gradient, txt_clip])
        except Exception as e:
            logging.warning(f"Failed to create text overlay: {e}. Using plain color video.")
            video = gradient
        
        # Write to temporary file with H.264 codec
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        try:
            video.write_videofile(
                temp_path,
                codec='libx264',
                audio=False,
                fps=24,
                preset='ultrafast',
                logger=None,  # Suppress MoviePy output
                threads=4,
                # QuickTime compatibility settings
                ffmpeg_params=[
                    '-pix_fmt', 'yuv420p',
                    '-profile:v', 'high',
                    '-level', '4.0',
                    '-movflags', '+faststart'
                ]
            )
            
            # Read the video bytes
            with open(temp_path, 'rb') as f:
                video_bytes = f.read()
            
            return video_bytes
        finally:
            # Clean up
            video.close()
            if os.path.exists(temp_path):
                os.unlink(temp_path)