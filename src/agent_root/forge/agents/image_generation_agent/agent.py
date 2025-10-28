"""
Product Requirements Document (PRD) Agent
Generates comprehensive PRD from GTM brief including user journey, screen specs, and design guidelines.
"""

from google.adk import Agent
from forge.utils.callbacks import create_asset_save_callback
from forge.config import config

prompt = """
Review the following GTM brief and generate a logo for the product described in the brief.

GTM Brief:
{+company_brief}+
"""


# Use factory pattern to create callback
image_generation_agent = Agent(
    name="prd_agent",
    description="Generates an image based on a prompt",
    instruction=prompt,
    model=config.image_generation_model,
    output_key="image",
    after_agent_callback=create_asset_save_callback(
        state_key="images",
        asset_type="images",
        filename="image.png",
    ),
)
