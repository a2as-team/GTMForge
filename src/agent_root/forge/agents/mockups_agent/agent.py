"""Mockups Agent

Generates UI mockup images from PRD using gemini-2.5-flash-image model.
"""

from __future__ import annotations

import logging
from typing import Optional

from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent, BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from collections.abc import AsyncGenerator

from pydantic import BaseModel, Field

from forge.config import config


class MockupPrompt(BaseModel):
    """Represents a single UI screen mockup prompt."""

    screen_name: str = Field(
        description="Name of the screen (e.g., 'Dashboard - Main Interface', 'Onboarding - Welcome')"
    )
    imagen_prompt: str = Field(
        description="Detailed Imagen prompt for generating the mockup (120+ words)"
    )
    index: int = Field(description="Order index of the screen in the user journey")


class MockupPromptsList(BaseModel):
    """Structured list of all mockup prompts to generate."""

    prompts: list[MockupPrompt] = Field(
        default_factory=list,
        description="List of mockup prompts extracted from PRD screen specifications"
    )


class MockupResult(BaseModel):
    """Result of a single mockup generation."""

    screen_name: str
    imagen_prompt: str
    image_path: str
    image_url: str
    index: int


class MockupsManifest(BaseModel):
    """Complete manifest of all generated mockups."""

    results: list[MockupResult] = Field(default_factory=list)
    total_count: int = Field(default=0)


def initialize_mockup_queue_callback(callback_context: CallbackContext) -> None:
    """Initialize the mockup generation queue from extracted prompts."""
    prompts_payload = callback_context.state.get("mockup_prompts_list")

    if not prompts_payload:
        logging.warning("[mockups_agent] No mockup prompts found in state.")
        callback_context.state["mockup_queue"] = []
        callback_context.state["mockup_results"] = []
        return

    # Extract prompts from Pydantic model or dict
    if isinstance(prompts_payload, MockupPromptsList):
        prompts = [p.model_dump() for p in prompts_payload.prompts]
    else:
        prompts = list(prompts_payload.get("prompts", []))

    callback_context.state["mockup_queue"] = prompts
    callback_context.state["mockup_results"] = []

    logging.info(f"[mockups_agent] Initialized queue with {len(prompts)} prompts:")
    for p in prompts:
        logging.info(f"  - {p.get('screen_name', 'Unknown')} (prompt length: {len(p.get('imagen_prompt', ''))} chars)")


def save_mockup_image_callback(
    callback_context: CallbackContext, llm_response=None
) -> None:
    """Extracts generated mockup image from model response and saves it to asset server."""

    # Step 1: Get current prompt metadata
    prompt_data = callback_context.state.get("current_mockup_prompt")
    if not prompt_data:
        logging.warning(
            "[mockups_agent] No prompt data found at 'current_mockup_prompt'. Skipping image extraction."
        )
        return

    # Step 2: Extract image from model response
    response = llm_response
    if not response:
        logging.error("[mockups_agent] No model response available. Cannot extract image.")
        return

    image_data = None
    mime_type = None

    try:
        # Extract image from inline_data format (gemini-2.5-flash-image)
        # Use response.content.parts directly (working structure from image_generation_agent)
        if hasattr(response, "content") and response.content:
            for part in response.content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    image_data = part.inline_data.data
                    mime_type = part.inline_data.mime_type
                    logging.info("[mockups_agent] Found inline_data in response.content.parts")
                    break

        if not image_data:
            logging.error(
                "[mockups_agent] No image data found in model response. "
                "Expected inline_data format from gemini-2.5-flash-image."
            )
            return

    except Exception as e:
        logging.error(f"[mockups_agent] Error extracting image from response: {e}")
        return

    # Step 3: Determine filename
    screen_name = prompt_data.get("screen_name", "unknown_screen")
    index = prompt_data.get("index", 0)

    # Sanitize screen name for filename
    safe_screen_name = "".join(
        c if c.isalnum() or c in ("-", "_") else "_" for c in screen_name.lower()
    )

    # Determine file extension from mime_type
    extension_map = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/webp": "webp",
    }
    extension = extension_map.get(mime_type, "png")

    filename = f"{index:02d}_{safe_screen_name}.{extension}"

    # Step 4: Save binary image data
    session_id = callback_context._invocation_context.session.id

    # inline_data.data is already raw binary bytes (not base64)
    # Just use it directly (as proven working in image_generation_agent)
    image_binary = image_data

    try:
        # Create a simple object with content field containing binary data
        from types import SimpleNamespace
        binary_asset = SimpleNamespace(content=image_binary, filename=filename)

        # Save binary directly to asset server
        from forge.utils.asset_services import save_assets
        saved_files = save_assets(
            session_id=session_id,
            asset_type="mockups",
            assets=[binary_asset],
            mime_type=mime_type,
        )

        if not saved_files:
            logging.error("[mockups_agent] Failed to save image: save_assets() returned empty list")
            return

        image_url = saved_files[0]["url"]
        image_path = saved_files[0]["path"]

        logging.info(
            f"[mockups_agent] Image saved for '{screen_name}' at {image_url}"
        )

    except Exception as e:
        logging.error(f"[mockups_agent] Failed to save image for '{screen_name}': {e}")
        return

    # Step 5: Create result metadata
    result = {
        "screen_name": screen_name,
        "imagen_prompt": prompt_data.get("imagen_prompt", ""),
        "image_path": image_path,
        "image_url": image_url,
        "index": index,
    }

    # Step 6: Append to results list
    results = callback_context.state.get("mockup_results", [])
    if not isinstance(results, list):
        results = []

    results.append(result)
    callback_context.state["mockup_results"] = results

    logging.info(
        f"[mockups_agent] Added mockup result for '{screen_name}'. Total results: {len(results)}"
    )


class MockupQueueLoader(BaseAgent):
    """Pops the next mockup prompt from queue and sets it as current."""

    def __init__(self) -> None:
        super().__init__(name="mockup_queue_loader")

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        queue: list[dict] = list(state.get("mockup_queue", []))

        if not queue:
            logging.info("[mockup_queue_loader] Queue is empty, clearing current prompt.")
            # Clear current prompt when queue is empty
            state.pop("current_mockup_prompt", None)
            yield Event(author=self.name)
            return

        current_prompt = queue.pop(0)
        state["mockup_queue"] = queue
        state["current_mockup_prompt"] = current_prompt

        logging.info(
            f"[mockup_queue_loader] Loaded: '{current_prompt.get('screen_name', 'Unknown')}' "
            f"(Remaining: {len(queue)})"
        )

        yield Event(author=self.name)


class MockupLoopTerminator(BaseAgent):
    """Terminates the loop when all prompts have been processed."""

    def __init__(self) -> None:
        super().__init__(name="mockup_loop_terminator")

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        queue = state.get("mockup_queue", [])

        # Only check queue - current_mockup_prompt is cleared by loader
        if queue:
            logging.debug(f"[mockup_loop_terminator] {len(queue)} prompts remaining, continuing loop.")
            yield Event(author=self.name)
            return

        logging.info("[mockups_agent] All mockups generated. Escalating to stop loop.")
        yield Event(author=self.name, actions=EventActions(escalate=True))


# LLM-based prompt extractor (more robust than regex)
mockup_prompt_extractor = LlmAgent(
    name="mockup_prompt_extractor",
    model=config.research_config.worker_model,
    description="Extracts Imagen mockup prompts from PRD screen specifications.",
    instruction="""
    You are a PRD analyzer specializing in extracting UI mockup specifications.

    Your task is to analyze the Product Requirements Document (PRD) from the 'product_requirements_doc'
    state key and extract ALL screen specifications that include Imagen mockup prompts.

    The PRD contains a "Screen Specifications" section (typically Section 5) where each screen has:
    - Screen name/purpose (e.g., "### Screen 1: Dashboard - Main Interface")
    - User context and purpose
    - UI components and layout
    - **Imagen Mockup Prompt**: A detailed prompt for generating the UI mockup (typically 120+ words)

    For each screen specification, extract:
    1. `screen_name`: The name/title of the screen exactly as it appears
    2. `imagen_prompt`: The EXACT text of the Imagen mockup prompt (do NOT modify or summarize)
    3. `index`: The sequential order number (0 for first screen, 1 for second, etc.)

    IMPORTANT:
    - Extract ALL screens that have Imagen Mockup Prompts
    - Preserve the exact wording of the prompts - do NOT modify, shorten, or paraphrase
    - Maintain the original order of screens as they appear in the PRD
    - If a screen doesn't have an Imagen prompt, skip it
    - The prompt text is typically after "**Imagen Mockup Prompt**:" and before the next section

    Return the extracted prompts as a structured list conforming to the MockupPromptsList schema.
    """,
    output_schema=MockupPromptsList,
    output_key="mockup_prompts_list",
    after_agent_callback=initialize_mockup_queue_callback,
)


mockup_image_generator = LlmAgent(
    name="mockup_image_generator",
    model=config.image_generation_model,
    description="Generates a single UI mockup image from an Imagen prompt.",
    instruction="""
    You are a UI mockup generator using Gemini's image generation capabilities.

    Generate a high-quality UI mockup image based on the following prompt:

    {current_mockup_prompt[imagen_prompt]}

    Create a realistic, professional UI mockup that accurately represents:
    - The screen layout and structure described in the prompt
    - UI components and their precise arrangement
    - Visual hierarchy and design aesthetic
    - Color scheme and branding elements
    - Realistic data and content examples
    - Interaction states and responsive considerations

    The generated image should be suitable for product documentation, presentations, and development references.
    """,
    after_model_callback=save_mockup_image_callback,
)


mockup_generation_loop = LoopAgent(
    name="mockup_generation_loop",
    description="Iterates through all mockup prompts and generates images sequentially.",
    max_iterations=20,  # Safety limit
    sub_agents=[
        MockupQueueLoader(),
        mockup_image_generator,
        MockupLoopTerminator(),
    ],
)


def save_mockups_manifest_callback(callback_context: CallbackContext) -> None:
    """Saves the final mockups manifest to disk and state."""
    results = callback_context.state.get("mockup_results", [])

    if not results:
        logging.warning("[mockups_agent] No mockup results to save.")
        return

    # Create manifest
    manifest = MockupsManifest(
        results=[MockupResult(**r) for r in results],
        total_count=len(results),
    )

    # Save manifest as JSON
    manifest_json = manifest.model_dump_json(indent=2)
    callback_context.state["mockups_manifest"] = manifest_json

    # Also save to asset server
    session_id = callback_context._invocation_context.session.id
    from forge.data_models import Assets, ReportAsset

    assets = Assets(
        session_id=session_id,
        asset_type="mockups",
        items=[ReportAsset(content=manifest_json, filename="mockups_manifest.json")],
    )

    saved_files = assets.save()
    callback_context.state["mockups_manifest_url"] = saved_files[0]["url"]
    callback_context.state["mockups_manifest_path"] = saved_files[0]["path"]

    logging.info(
        f"[mockups_agent] Saved manifest with {len(results)} mockups to {saved_files[0]['url']}"
    )


mockups_agent = SequentialAgent(
    name="mockups_agent",
    description="Extracts mockup prompts from PRD and generates UI mockup images using gemini-2.5-flash-image.",
    sub_agents=[
        mockup_prompt_extractor,
        mockup_generation_loop,
    ],
    after_agent_callback=save_mockups_manifest_callback,
)
