"""Image Generation Agent

Generates a single image based on a prompt from state.
Simple, reusable agent for any single-image generation task.
"""

import base64
import logging

from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from forge.config import config
from forge.data_models import Assets, ImageAsset


def save_generated_image_callback(
    callback_context: CallbackContext, llm_response=None
) -> None:
    """Extracts generated image from model response and saves it to asset server."""

    # Extract image from model response
    response = llm_response
    if not response:
        logging.error("[image_generation_agent] No model response available.")
        return

    image_data = None
    mime_type = None

    try:
        # Extract image from inline_data format (gemini-2.5-flash-image)

        if hasattr(response, "content") and response.content:
            for part in response.content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    image_data = part.inline_data.data
                    mime_type = part.inline_data.mime_type
                    break

        if not image_data:
            logging.error("[image_generation_agent] No image data in response.")
            return

    except Exception as e:
        logging.error(f"[image_generation_agent] Error extracting image: {e}")
        return

    # Determine file extension
    extension_map = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/webp": "webp",
    }
    extension = extension_map.get(mime_type, "png")

    # Get filename from state or use default
    filename = callback_context.state.get(
        "image_filename", f"generated_image.{extension}"
    )
    if not filename.endswith(f".{extension}"):
        filename = f"{filename}.{extension}"

    # inline_data.data is already raw binary bytes (not base64)
    # Just use it directly
    image_binary = image_data

    # Save binary directly to asset server
    session_id = callback_context._invocation_context.session.id
    asset_type = callback_context.state.get("image_asset_type", "images")

    try:
        # Create a simple object with content field containing binary data
        from types import SimpleNamespace
        binary_asset = SimpleNamespace(content=image_binary, filename=filename)

        from forge.utils.asset_services import save_assets
        saved_files = save_assets(
            session_id=session_id,
            asset_type=asset_type,
            assets=[binary_asset],
            mime_type=mime_type,
        )

        if saved_files:
            callback_context.state["generated_image_url"] = saved_files[0]["url"]
            callback_context.state["generated_image_path"] = saved_files[0]["path"]
            logging.info(
                f"[image_generation_agent] Image saved to {saved_files[0]['url']}"
            )
        else:
            logging.error("[image_generation_agent] Failed to save image.")

    except Exception as e:
        logging.error(f"[image_generation_agent] Error saving image: {e}")


image_generation_agent = Agent(
    name="image_generation_agent",
    description="Generates a single image from a text prompt using gemini-2.5-flash-image model.",
    model=config.image_generation_model,
    instruction="""
    You are an image generation specialist. Generate a high-quality logo based on the provided company brief.

    The image prompt will be available in the session state under the 'image_prompt' key.

    Create a professional, visually appealing image that accurately represents the prompt.
    Pay attention to composition, color harmony, style, and overall aesthetic quality.

    ## Company Brief:
    {company_brief}
    """,
    after_model_callback=save_generated_image_callback,
)
