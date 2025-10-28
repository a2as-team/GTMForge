"""Image Generation Agent

Generates a single image based on a prompt from state.
Simple, reusable agent for any single-image generation task.
"""

import base64
import logging

from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from forge.config import config

prompt = """
Review the following GTM brief and generate a logo for the product described in the brief.

GTM Brief:
{+company_brief}+
"""


# Use factory pattern to create callback
image_generation_agent = Agent(
    name="image_generation_agent",
    description="Generates a single image from a text prompt using gemini-2.5-flash-image model.",
    model=config.image_generation_model,
    instruction="""
    You are an image generation specialist. Generate a high-quality image based on the prompt provided.

    The image prompt will be available in the session state under the 'image_prompt' key.

    Create a professional, visually appealing image that accurately represents the prompt.
    Pay attention to composition, color harmony, style, and overall aesthetic quality.
    """,
    after_model_callback=save_generated_image_callback,
)
