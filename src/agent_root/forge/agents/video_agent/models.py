"""Pydantic models for Video Agent data structures."""

from typing import Optional
from pydantic import BaseModel, Field


class VideoGenerationPrompt(BaseModel):
    """Structured prompt for generating a single video clip."""
    
    clip_index: int = Field(
        description="Index of this clip in the sequence (0-based)"
    )
    duration: float = Field(
        default=10.0,
        description="Target duration in seconds (8-12 seconds)"
    )
    scene_description: str = Field(
        description="Detailed description of what should happen in this video clip"
    )
    visual_style: str = Field(
        description="Visual style and aesthetic for the clip"
    )
    key_message: str = Field(
        description="Key message or narrative for this clip"
    )
    transition_hint: Optional[str] = Field(
        default=None,
        description="Hint for transition to next clip"
    )


class VideoClipMetadata(BaseModel):
    """Metadata for a generated video clip."""
    
    clip_index: int = Field(description="Index of this clip")
    duration: float = Field(description="Actual duration in seconds")
    local_path: str = Field(description="Local file path of the clip")
    asset_url: str = Field(description="Asset server URL")
    scene_description: str = Field(description="What this clip shows")
    

class VideoGenerationPlan(BaseModel):
    """Complete plan for generating multiple video clips."""
    
    startup_name: str = Field(description="Name of the startup")
    video_concept: str = Field(description="Overall concept for the promotional video")
    target_audience: str = Field(description="Target audience for the video")
    clips: list[VideoGenerationPrompt] = Field(
        description="List of prompts for individual clips to generate"
    )
    

class FinalVideoOutput(BaseModel):
    """Final video output metadata and locations."""
    
    startup_name: str = Field(description="Name of the startup")
    video_title: str = Field(description="Title of the promotional video")
    video_description: str = Field(
        description="Description/caption for downstream usage"
    )
    total_duration: float = Field(description="Total duration in seconds")
    local_path: str = Field(description="Local path of combined video")
    asset_url: str = Field(description="Asset server URL of combined video")
    component_clips: list[VideoClipMetadata] = Field(
        default_factory=list,
        description="Metadata for individual component clips"
    )
    transcript: Optional[str] = Field(
        default=None,
        description="Video transcript or narration text"
    )

