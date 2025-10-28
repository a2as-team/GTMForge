"""Mockups Agent

Generates UI mockup images from PRD using gemini-2.5-flash-image model.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Optional

from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent, BaseAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai import types as genai_types
from collections.abc import AsyncGenerator

from pydantic import BaseModel, Field

from forge.config import config
from forge.utils.callbacks import create_image_extraction_callback


class MockupPrompt(BaseModel):
    """Represents a single UI screen mockup prompt."""

    screen_name: str = Field(
        description="Name of the screen (e.g., 'Dashboard', 'Login')"
    )
    imagen_prompt: str = Field(
        description="Detailed Imagen prompt for generating the mockup"
    )
    index: int = Field(description="Order index of the screen in the user journey")


class MockupPromptsList(BaseModel):
    """Structured list of all mockup prompts to generate."""

    prompts: list[MockupPrompt] = Field(
        default_factory=list, description="List of mockup prompts extracted from PRD"
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
    # Debug: Check if PRD exists
    prd = callback_context.state.get("product_requirements_doc")
    if prd:
        logging.info(f"[mockups_agent] PRD found, length: {len(prd)} characters")
        # Check if it contains Imagen prompts
        if "**Imagen Mockup Prompt**:" in prd:
            count = prd.count("**Imagen Mockup Prompt**:")
            logging.info(f"[mockups_agent] Found {count} Imagen Mockup Prompts in PRD")
        else:
            logging.warning(
                "[mockups_agent] No '**Imagen Mockup Prompt**:' found in PRD"
            )
    else:
        logging.warning("[mockups_agent] No PRD found in state")

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
    logging.info(f"[mockups_agent] Initialized queue with {len(prompts)} prompts.")


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
            logging.info("[mockups_agent] Queue is empty.")
            yield Event(author=self.name)
            return

        current_prompt = queue.pop(0)
        state["mockup_queue"] = queue
        state["current_mockup_prompt"] = current_prompt

        logging.info(
            f"[mockups_agent] Loaded prompt for '{current_prompt.get('screen_name', 'Unknown')}'. Remaining: {len(queue)}"
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
        current = state.get("current_mockup_prompt")

        if queue or current:
            yield Event(author=self.name)
            return

        logging.info("[mockups_agent] All mockups generated. Escalating to stop loop.")
        yield Event(author=self.name, actions=EventActions(escalate=True))


# Create a simple base agent that just extracts prompts manually
class MockupPromptExtractorAgent(BaseAgent):
    """Manually extracts mockup prompts from PRD."""

    def __init__(self, **data):
        super().__init__(
            name="mockup_prompt_extractor",
            description="Extracts Imagen mockup prompts from the PRD",
            **data,
        )

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        # Extract prompts directly from PRD
        prd = ctx.session.state.get("product_requirements_doc", "")

        if not prd:
            logging.warning("[mockup_prompt_extractor] No PRD found in state")
            ctx.session.state["mockup_prompts_list"] = {"prompts": []}
            yield Event(author=self.name)
            return

        logging.info(
            f"[mockup_prompt_extractor] PRD found, length: {len(prd)} characters"
        )

        prompts = []

        # Split PRD into sections based on "### Screen" pattern
        import re

        screen_sections = re.split(r"### Screen \d+:", prd)

        for i, section in enumerate(
            screen_sections[1:], 0
        ):  # Skip the first split before any screen
            # Extract screen name from first line
            lines = section.strip().split("\n")
            if not lines:
                continue

            screen_name = lines[0].strip()

            # Look for Imagen Mockup Prompt
            if "**Imagen Mockup Prompt**:" in section:
                # Extract everything after "**Imagen Mockup Prompt**:"
                prompt_start = section.find("**Imagen Mockup Prompt**:") + len(
                    "**Imagen Mockup Prompt**:"
                )

                # Find the end of the prompt (next section or end of content)
                prompt_end = section.find("\n\n---", prompt_start)
                if prompt_end == -1:
                    prompt_end = section.find("\n\n###", prompt_start)
                if prompt_end == -1:
                    prompt_end = section.find("\n\n##", prompt_start)
                if prompt_end == -1:
                    prompt_end = len(section)

                imagen_prompt = section[prompt_start:prompt_end].strip()
                # Remove quotes if present
                if imagen_prompt.startswith('"') and imagen_prompt.endswith('"'):
                    imagen_prompt = imagen_prompt[1:-1]

                if imagen_prompt:
                    prompts.append(
                        {
                            "screen_name": screen_name,
                            "imagen_prompt": imagen_prompt,
                            "index": i,
                        }
                    )
                    logging.info(
                        f"[mockup_prompt_extractor] Extracted prompt for screen: {screen_name}"
                    )

        result = {"prompts": prompts}
        ctx.session.state["mockup_prompts_list"] = result

        # Yield success event with proper content format
        content = genai_types.Content(
            role="model",
            parts=[
                genai_types.Part(
                    text=f"Successfully extracted {len(prompts)} mockup prompts from PRD"
                )
            ],
        )
        yield Event(author=self.name, content=content)


mockup_prompt_extractor = MockupPromptExtractorAgent(
    before_agent_callback=initialize_mockup_queue_callback,
)


# Create the image extraction callback that will save images after generation
save_mockup_image_callback = create_image_extraction_callback(
    prompt_state_key="current_mockup_prompt",
    asset_type="mockups",
    results_state_key="mockup_results",
)


mockup_image_generator = LlmAgent(
    name="mockup_image_generator",
    model=config.image_generation_model,
    description="Generates a single UI mockup image from an Imagen prompt.",
    instruction="""
    You are a UI mockup generator using Gemini's image generation capabilities.

    The current mockup prompt is stored in the 'current_mockup_prompt' state key, which contains:
    - screen_name: The name of the screen
    - imagen_prompt: The detailed Imagen prompt for this screen
    - index: The order of this screen

    Your task is to generate a high-quality UI mockup image based on the 'imagen_prompt' field.

    Use the detailed prompt to create a realistic, professional UI mockup that accurately represents:
    - The screen layout and structure
    - UI components and their arrangement
    - Visual hierarchy and design aesthetic
    - Color scheme and branding
    - Realistic data and content

    The generated image should be suitable for use in product documentation, presentations, and development references.
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
