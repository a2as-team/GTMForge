"""Video Generation Agent

Generates promotional videos from startup context using Google Veo.
Creates 2-3 short clips and stitches them into a cohesive video.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Optional

from google.adk.agents import LlmAgent, SequentialAgent, BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.genai import types as genai_types
from collections.abc import AsyncGenerator

from forge.config import config
from forge.data_models import Assets, VideoAsset
from forge.utils.callbacks import create_asset_save_callback

from .models import (
    VideoGenerationPlan,
    VideoGenerationPrompt,
    VideoClipMetadata,
    FinalVideoOutput
)
from .veo_client import VeoClient
from .stitch import VideoStitcher


class VideoGenerationAgent(BaseAgent):
    """Custom agent that generates videos using Veo and stitches them together."""
    
    def __init__(self, **data):
        super().__init__(
            name="video_generation_worker",
            description="Generates and stitches video clips using Google Veo",
            **data
        )
        
        # Initialize clients as instance attributes (not Pydantic fields)
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "mock-project")
        self._veo_client = VeoClient(project_id=project_id)
        self._stitcher = VideoStitcher(transition_duration=0.5)
        
    async def _run_async_impl(
        self,
        ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """Generate videos based on the plan in state."""
        
        state = ctx.session.state
        
        # Get the video generation plan
        plan_data = state.get("video_generation_plan")
        if not plan_data:
            logging.error("No video generation plan found in state")
            yield Event(author=self.name)
            return
        
        # Parse plan
        if isinstance(plan_data, dict):
            plan = VideoGenerationPlan(**plan_data)
        else:
            plan = plan_data
        
        logging.info(
            f"Starting video generation for {plan.startup_name} "
            f"with {len(plan.clips)} clips"
        )
        
        # Generate each clip
        clip_metadata = []
        clip_paths = []
        
        for i, clip_prompt in enumerate(plan.clips):
            logging.info(f"Generating clip {i+1}/{len(plan.clips)}")
            
            try:
                # Validate prompt
                is_valid, error = self._veo_client.validate_prompt(
                    clip_prompt.scene_description
                )
                if not is_valid:
                    logging.error(f"Invalid prompt for clip {i}: {error}")
                    continue
                
                # Generate video
                video_bytes = await self._veo_client.generate_video(
                    prompt=clip_prompt.scene_description,
                    duration_seconds=clip_prompt.duration,
                    aspect_ratio="16:9",
                    style=clip_prompt.visual_style
                )
                
                # Save individual clip
                session_id = ctx.session.id
                clip_filename = f"clip_{i:02d}_{plan.startup_name.lower().replace(' ', '_')}.mp4"
                
                # Save using Assets model
                assets = Assets(
                    session_id=session_id,
                    asset_type="video_clips",
                    items=[VideoAsset(
                        content=video_bytes,
                        filename=clip_filename,
                        duration=clip_prompt.duration
                    )]
                )
                
                saved_files = assets.save()
                if saved_files:
                    clip_path = saved_files[0]["path"]
                    clip_url = saved_files[0]["url"]
                    
                    # Add to metadata
                    metadata = VideoClipMetadata(
                        clip_index=i,
                        duration=clip_prompt.duration,
                        local_path=clip_path,
                        asset_url=clip_url,
                        scene_description=clip_prompt.scene_description
                    )
                    clip_metadata.append(metadata)
                    clip_paths.append(clip_path)
                    
                    logging.info(f"Saved clip {i} to {clip_url}")
                
            except Exception as e:
                logging.error(f"Failed to generate clip {i}: {e}")
                continue
        
        if not clip_paths:
            logging.error("No clips were successfully generated")
            yield Event(author=self.name)
            return
        
        # Stitch clips together
        try:
            logging.info("Stitching clips together...")
            
            # Prepare output path
            final_filename = f"promo_{plan.startup_name.lower().replace(' ', '_')}.mp4"
            temp_output_path = Path("/tmp") / final_filename
            
            # Stitch videos
            output_path, total_duration = self._stitcher.stitch_clips(
                clip_paths=clip_paths,
                output_path=str(temp_output_path),
                title_text=f"{plan.startup_name} - {plan.video_concept}",
                add_transitions=True
            )
            
            # Read the final video
            with open(output_path, "rb") as f:
                final_video_bytes = f.read()
            
            # Save final video to asset server
            final_assets = Assets(
                session_id=ctx.session.id,
                asset_type="videos",
                items=[VideoAsset(
                    content=final_video_bytes,
                    filename=final_filename,
                    duration=total_duration
                )]
            )
            
            final_saved = final_assets.save()
            
            if final_saved:
                final_url = final_saved[0]["url"]
                final_path = final_saved[0]["path"]
                
                # Create final output metadata
                output = FinalVideoOutput(
                    startup_name=plan.startup_name,
                    video_title=f"{plan.startup_name} Promotional Video",
                    video_description=(
                        f"A {total_duration:.1f} second promotional video for "
                        f"{plan.startup_name}. {plan.video_concept}. "
                        f"Target audience: {plan.target_audience}."
                    ),
                    total_duration=total_duration,
                    local_path=final_path,
                    asset_url=final_url,
                    component_clips=clip_metadata
                )
                
                # Save to state
                state["final_video_output"] = output.model_dump()
                state["final_video_url"] = final_url
                state["final_video_path"] = final_path
                state["final_video_duration"] = total_duration
                
                logging.info(
                    f"Successfully created final video: {final_url} "
                    f"(duration: {total_duration:.1f}s)"
                )
                
                # Clean up temp file
                if temp_output_path.exists():
                    temp_output_path.unlink()
            
        except Exception as e:
            logging.error(f"Failed to stitch videos: {e}")
            logging.error(f"[{self.name}] Failed to stitch videos: {e}")
            yield Event(author=self.name)
            return
        
        # Success event with proper content format
        content = genai_types.Content(
            role="model",
            parts=[genai_types.Part(text=f"Successfully generated promotional video for {plan.startup_name}")]
        )
        yield Event(author=self.name, content=content)


# Video plan generator agent
video_plan_generator = LlmAgent(
    name="video_plan_generator",
    model=config.research_config.worker_model,
    description="Creates a video generation plan from startup context",
    instruction="""You are a video creative director specializing in startup promotional videos.

    Your task is to analyze the startup context from upstream agents and create a compelling
    video generation plan consisting of 2-3 short clips that tell the startup's story.

    Input data available in state:
    - company_brief: Startup concept, ICPs, pain points, value props
    - website_spec: Website structure and content plan  
    - product_requirements_doc: Detailed product specifications
    - mockups_manifest: UI/UX mockup details

    Create a video plan with exactly 2-3 clips (8-12 seconds each) that:
    1. Hook the viewer with the problem/pain point
    2. Introduce the solution elegantly
    3. Show the value/benefits (optional 3rd clip)

    Each clip should have:
    - Clear scene description (what happens visually)
    - Visual style (cinematic, minimal, dynamic, etc.)
    - Key message/narrative
    - Smooth transition hints

    Focus on:
    - Emotional storytelling that resonates with the target audience
    - Clear problem-solution narrative
    - Professional, modern aesthetic
    - Concise, impactful messaging

    The video should work without sound but can include text overlays.
    Total runtime should be 20-30 seconds after stitching.""",
    output_schema=VideoGenerationPlan,
    output_key="video_generation_plan",
)


# Save video manifest callback - convert dict to JSON string
def save_video_manifest_callback(callback_context: CallbackContext) -> None:
    """Save video manifest as JSON string."""
    from forge.data_models import Assets, DocumentAsset
    import json
    
    final_video_output = callback_context.state.get("final_video_output")
    if not final_video_output:
        logging.warning("No final_video_output found in state")
        return
    
    # Convert to JSON string
    if isinstance(final_video_output, dict):
        content = json.dumps(final_video_output, indent=2)
    else:
        content = str(final_video_output)
    
    # Save using Assets model
    session_id = callback_context._invocation_context.session.id
    assets = Assets(
        session_id=session_id,
        asset_type="videos",
        items=[DocumentAsset(content=content, filename="video_manifest.json")]
    )
    
    saved_files = assets.save()
    if saved_files:
        callback_context.state["video_manifest_url"] = saved_files[0]["url"]
        callback_context.state["video_manifest_path"] = saved_files[0]["path"]
        logging.info(f"Video manifest saved: {saved_files[0]['url']}")
    else:
        logging.error("Failed to save video manifest")


# Main video agent combining plan + generation
video_agent = SequentialAgent(
    name="video_agent",
    description="Generates promotional videos from startup context using Google Veo",
    sub_agents=[
        video_plan_generator,
        VideoGenerationAgent(),
    ],
    after_agent_callback=save_video_manifest_callback,
)
