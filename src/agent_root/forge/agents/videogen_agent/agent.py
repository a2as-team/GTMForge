"""Video Generation Agent

Generates promo video by creating individual scenes from company brief's
promo video script and splicing them together using moviepy.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional
from collections.abc import AsyncGenerator

from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent, BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions

from pydantic import BaseModel, Field

from forge.config import config


class VideoPrompt(BaseModel):
    """Represents a single video scene prompt."""

    scene_name: str = Field(
        description="Name of the scene (e.g., 'Hook (0-8s)', 'Problem (8-16s)')"
    )
    veo_prompt: str = Field(
        description="Detailed Veo prompt for generating the video scene"
    )
    index: int = Field(description="Order index of the scene in the video")
    duration: int = Field(default=8, description="Duration of the scene in seconds")


class VideoPromptsList(BaseModel):
    """Structured list of all video scene prompts."""

    prompts: list[VideoPrompt] = Field(
        default_factory=list,
        description="List of video prompts extracted from company brief promo script"
    )


class VideoResult(BaseModel):
    """Result of a single video generation."""

    scene_name: str
    veo_prompt: str
    video_path: str
    video_url: str
    index: int
    duration: int


class VideoManifest(BaseModel):
    """Complete manifest of all generated videos."""

    individual_videos: list[VideoResult] = Field(default_factory=list)
    spliced_video_path: str = Field(default="")
    spliced_video_url: str = Field(default="")
    total_duration: int = Field(default=0)


def initialize_video_queue_callback(callback_context: CallbackContext) -> None:
    """Initialize the video generation queue from extracted prompts."""
    prompts_payload = callback_context.state.get("video_prompts_list")

    if not prompts_payload:
        logging.warning("[videogen_agent] No video prompts found in state.")
        callback_context.state["video_queue"] = []
        callback_context.state["video_results"] = []
        return

    # Extract prompts from Pydantic model or dict
    if isinstance(prompts_payload, VideoPromptsList):
        prompts = [p.model_dump() for p in prompts_payload.prompts]
    else:
        prompts = list(prompts_payload.get("prompts", []))

    callback_context.state["video_queue"] = prompts
    callback_context.state["video_results"] = []

    logging.info(f"[videogen_agent] Initialized queue with {len(prompts)} video prompts:")
    for p in prompts:
        logging.info(f"  - {p.get('scene_name', 'Unknown')} ({p.get('duration', 8)}s)")


def save_video_callback(
    callback_context: CallbackContext, llm_response=None
) -> None:
    """Extracts generated video from model response and saves it to asset server."""

    # Step 1: Get current prompt metadata
    prompt_data = callback_context.state.get("current_video_prompt")
    if not prompt_data:
        logging.warning(
            "[videogen_agent] No prompt data found at 'current_video_prompt'. Skipping video extraction."
        )
        return

    # Step 2: Extract video from model response
    response = llm_response
    if not response:
        logging.error("[videogen_agent] No model response available. Cannot extract video.")
        return

    video_data = None
    mime_type = None

    try:
        # Extract video from inline_data format (assuming similar to gemini-2.5-flash-image)
        # Try response.content.parts directly first
        if hasattr(response, "content") and response.content:
            for part in response.content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    video_data = part.inline_data.data
                    mime_type = part.inline_data.mime_type
                    logging.info("[videogen_agent] Found inline_data in response.content.parts")
                    break

        # Fallback: try response.candidates[0].content.parts
        if not video_data and hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and candidate.content:
                for part in candidate.content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        video_data = part.inline_data.data
                        mime_type = part.inline_data.mime_type
                        logging.info("[videogen_agent] Found inline_data in response.candidates[0].content.parts")
                        break

        if not video_data:
            logging.error(
                "[videogen_agent] No video data found in model response. "
                "Expected inline_data format from Veo model."
            )
            return

    except Exception as e:
        logging.error(f"[videogen_agent] Error extracting video from response: {e}")
        return

    # Step 3: Determine filename
    scene_name = prompt_data.get("scene_name", "unknown_scene")
    index = prompt_data.get("index", 0)
    duration = prompt_data.get("duration", 8)

    # Sanitize scene name for filename
    safe_scene_name = "".join(
        c if c.isalnum() or c in ("-", "_") else "_" for c in scene_name.lower()
    )

    # Determine file extension from mime_type
    extension_map = {
        "video/mp4": "mp4",
        "video/mpeg": "mpg",
        "video/quicktime": "mov",
        "video/x-msvideo": "avi",
        "video/webm": "webm",
    }
    extension = extension_map.get(mime_type, "mp4")

    filename = f"{index:02d}_{safe_scene_name}.{extension}"

    # Step 4: Save binary video data
    session_id = callback_context._invocation_context.session.id

    # inline_data.data is already raw binary bytes (not base64)
    # Just use it directly (same as image handling)
    video_binary = video_data

    try:
        # Create a simple object with content field containing binary data
        from types import SimpleNamespace
        binary_asset = SimpleNamespace(content=video_binary, filename=filename)

        # Save binary directly to asset server
        from forge.utils.asset_services import save_assets
        saved_files = save_assets(
            session_id=session_id,
            asset_type="videos",
            assets=[binary_asset],
            mime_type=mime_type,
        )

        if not saved_files:
            logging.error("[videogen_agent] Failed to save video: save_assets() returned empty list")
            return

        video_url = saved_files[0]["url"]
        video_path = saved_files[0]["path"]

        logging.info(
            f"[videogen_agent] Video saved for '{scene_name}' at {video_url}"
        )

    except Exception as e:
        logging.error(f"[videogen_agent] Failed to save video for '{scene_name}': {e}")
        return

    # Step 5: Create result metadata
    result = {
        "scene_name": scene_name,
        "veo_prompt": prompt_data.get("veo_prompt", ""),
        "video_path": video_path,
        "video_url": video_url,
        "index": index,
        "duration": duration,
    }

    # Step 6: Append to results list
    results = callback_context.state.get("video_results", [])
    if not isinstance(results, list):
        results = []

    results.append(result)
    callback_context.state["video_results"] = results

    logging.info(
        f"[videogen_agent] Added video result for '{scene_name}'. Total results: {len(results)}"
    )


class VideoQueueLoader(BaseAgent):
    """Pops the next video prompt from queue and sets it as current."""

    def __init__(self) -> None:
        super().__init__(name="video_queue_loader")

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        queue: list[dict] = list(state.get("video_queue", []))

        if not queue:
            logging.info("[video_queue_loader] Queue is empty, clearing current prompt.")
            # Clear current prompt when queue is empty
            state.pop("current_video_prompt", None)
            yield Event(author=self.name)
            return

        current_prompt = queue.pop(0)
        state["video_queue"] = queue
        state["current_video_prompt"] = current_prompt

        logging.info(
            f"[video_queue_loader] Loaded: '{current_prompt.get('scene_name', 'Unknown')}' "
            f"(Remaining: {len(queue)})"
        )

        yield Event(author=self.name)


class VideoLoopTerminator(BaseAgent):
    """Terminates the loop when all prompts have been processed."""

    def __init__(self) -> None:
        super().__init__(name="video_loop_terminator")

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        queue = state.get("video_queue", [])

        # Only check queue - current_video_prompt is cleared by loader
        if queue:
            logging.debug(f"[video_loop_terminator] {len(queue)} prompts remaining, continuing loop.")
            yield Event(author=self.name)
            return

        logging.info("[videogen_agent] All videos generated. Escalating to stop loop.")
        yield Event(author=self.name, actions=EventActions(escalate=True))


class VideoSplicer(BaseAgent):
    """Splices individual video scenes into a single final video using moviepy."""

    def __init__(self) -> None:
        super().__init__(name="video_splicer")

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        results = state.get("video_results", [])

        if not results:
            logging.warning("[videogen_agent] No video results to splice.")
            yield Event(author=self.name)
            return

        # Sort by index to ensure correct order
        results_sorted = sorted(results, key=lambda x: x["index"])

        logging.info(f"[videogen_agent] Splicing {len(results_sorted)} video scenes together...")

        try:
            # Import moviepy
            from moviepy.editor import VideoFileClip, concatenate_videoclips

            # Load video clips
            clips = []
            for result in results_sorted:
                video_path = result["video_path"]
                logging.info(f"  Loading clip {result['index']}: {result['scene_name']}")

                # Check if file exists
                if not os.path.exists(video_path):
                    logging.error(f"[videogen_agent] Video file not found: {video_path}")
                    continue

                clip = VideoFileClip(video_path)
                clips.append(clip)

            if not clips:
                logging.error("[videogen_agent] No valid video clips loaded for splicing.")
                yield Event(author=self.name)
                return

            # Concatenate clips
            logging.info(f"[videogen_agent] Concatenating {len(clips)} clips...")
            final_video = concatenate_videoclips(clips, method="compose")

            # Save spliced video to temp file
            session_id = ctx.session.id
            output_filename = "promo_video_final.mp4"
            temp_path = f"/tmp/{session_id}_{output_filename}"

            logging.info(f"[videogen_agent] Writing final video to {temp_path}...")
            final_video.write_videofile(
                temp_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=f'/tmp/{session_id}_temp_audio.m4a',
                remove_temp=True,
                logger=None  # Suppress moviepy progress bars
            )

            # Read the file as binary
            with open(temp_path, "rb") as f:
                video_binary = f.read()

            # Save to asset server
            from forge.utils.asset_services import save_assets
            from types import SimpleNamespace

            binary_asset = SimpleNamespace(
                content=video_binary,
                filename=output_filename
            )

            saved_files = save_assets(
                session_id=session_id,
                asset_type="videos",
                assets=[binary_asset],
                mime_type="video/mp4"
            )

            if saved_files:
                state["spliced_video_url"] = saved_files[0]["url"]
                state["spliced_video_path"] = saved_files[0]["path"]

                # Calculate total duration
                total_duration = sum(r["duration"] for r in results_sorted)
                state["spliced_video_total_duration"] = total_duration

                logging.info(
                    f"[videogen_agent] Final video saved to {saved_files[0]['url']} "
                    f"(Duration: {total_duration}s)"
                )
            else:
                logging.error("[videogen_agent] Failed to save spliced video to asset server.")

            # Cleanup
            final_video.close()
            for clip in clips:
                clip.close()

            # Remove temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

        except ImportError as e:
            logging.error(f"[videogen_agent] moviepy not installed: {e}")
            logging.error("Install with: pip install moviepy")
        except Exception as e:
            logging.error(f"[videogen_agent] Error during video splicing: {e}")
            import traceback
            logging.error(traceback.format_exc())

        yield Event(author=self.name)


# LLM-based prompt extractor
video_prompt_extractor = LlmAgent(
    name="video_prompt_extractor",
    model=config.research_config.worker_model,
    description="Extracts Veo video prompts from company brief promo video script.",
    instruction="""
    You are a video script analyzer specializing in extracting video scene specifications.

    Your task is to analyze the company brief from the 'company_brief' state key and extract
    ALL video scene prompts from the "Promo Video Script" section.

    The company brief contains a "Promo Video Script" section with 4 beats (scenes):
    - 0-8s Hook: Hook text and narration
    - 8-16s Problem: Problem statement text and narration
    - 16-24s Solution: Solution reveal text and narration
    - 24-32s Call to Action: CTA text and narration

    For each scene/beat, extract:
    1. `scene_name`: The beat name exactly as it appears (e.g., "Hook (0-8s)", "Problem (8-16s)")
    2. `veo_prompt`: The EXACT text for the scene including all narration and on-screen text (do NOT modify or summarize)
    3. `index`: The sequential order number (0 for first beat, 1 for second, 2 for third, 3 for fourth)
    4. `duration`: Always 8 seconds for each scene

    IMPORTANT:
    - Extract ALL 4 scenes from the promo video script
    - Preserve the exact wording of the prompts - do NOT modify, shorten, or paraphrase
    - Maintain the original order of scenes (0-8s, 8-16s, 16-24s, 24-32s)
    - Each scene should be detailed enough for video generation (include visual descriptions, narration, text overlays)

    Return the extracted prompts as a structured list conforming to the VideoPromptsList schema.
    """,
    output_schema=VideoPromptsList,
    output_key="video_prompts_list",
    after_agent_callback=initialize_video_queue_callback,
)


video_generator = LlmAgent(
    name="video_generator",
    model=config.video_model,
    description="Generates a single video scene using Veo model.",
    instruction="""
    You are a video generation specialist using Google's Veo video generation model.

    Generate a high-quality 8-second video based on the following prompt:

    {current_video_prompt[veo_prompt]}

    Create a professional, engaging video scene that accurately represents:
    - The visual scene description
    - Any on-screen text or graphics mentioned
    - The mood and tone specified
    - Transitions and pacing as described
    - Duration: exactly 8 seconds

    The generated video should be suitable for a professional promo video.
    """,
    after_model_callback=save_video_callback,
)


video_generation_loop = LoopAgent(
    name="video_generation_loop",
    description="Iterates through all video prompts and generates scenes sequentially.",
    max_iterations=10,  # Safety limit (4 scenes expected)
    sub_agents=[
        VideoQueueLoader(),
        video_generator,
        VideoLoopTerminator(),
    ],
)


def save_video_manifest_callback(callback_context: CallbackContext) -> None:
    """Saves the final video manifest to disk and state."""
    results = callback_context.state.get("video_results", [])

    if not results:
        logging.warning("[videogen_agent] No video results to save in manifest.")
        return

    # Get spliced video info
    spliced_url = callback_context.state.get("spliced_video_url", "")
    spliced_path = callback_context.state.get("spliced_video_path", "")
    total_duration = callback_context.state.get("spliced_video_total_duration", 0)

    # Create manifest
    manifest = VideoManifest(
        individual_videos=[VideoResult(**r) for r in results],
        spliced_video_url=spliced_url,
        spliced_video_path=spliced_path,
        total_duration=total_duration,
    )

    # Save manifest as JSON
    manifest_json = manifest.model_dump_json(indent=2)
    callback_context.state["video_manifest"] = manifest_json

    # Also save to asset server
    session_id = callback_context._invocation_context.session.id
    from forge.data_models import Assets, ReportAsset

    assets = Assets(
        session_id=session_id,
        asset_type="videos",
        items=[ReportAsset(content=manifest_json, filename="video_manifest.json")],
    )

    saved_files = assets.save()
    callback_context.state["video_manifest_url"] = saved_files[0]["url"]
    callback_context.state["video_manifest_path"] = saved_files[0]["path"]

    logging.info(
        f"[videogen_agent] Saved manifest with {len(results)} videos to {saved_files[0]['url']}"
    )


videogen_agent = SequentialAgent(
    name="videogen_agent",
    description="Generates promo video by creating individual scenes from company brief and splicing them together using moviepy.",
    sub_agents=[
        video_prompt_extractor,
        video_generation_loop,
        VideoSplicer(),
    ],
    after_agent_callback=save_video_manifest_callback,
)
