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


def save_generated_image_callback(callback_context: CallbackContext) -> None:
    """Extracts generated image from model response and saves it to asset server."""

    # Extract image from model response
    response = callback_context._last_response
    if not response:
        logging.error("[image_generation_agent] No model response available.")
        return

    image_data = None
    mime_type = None

    try:
        # Extract image from inline_data format (gemini-2.5-flash-image)
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and candidate.content:
                for part in candidate.content.parts:
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
    filename = callback_context.state.get("image_filename", f"generated_image.{extension}")
    if not filename.endswith(f".{extension}"):
        filename = f"{filename}.{extension}"

    # Convert to base64 string if needed (ImageAsset expects string)
    if isinstance(image_data, bytes):
        image_content = base64.b64encode(image_data).decode("utf-8")
    else:
        image_content = image_data

    # Save to asset server
    session_id = callback_context._invocation_context.session.id
    asset_type = callback_context.state.get("image_asset_type", "images")

    try:
        assets = Assets(
            session_id=session_id,
            asset_type=asset_type,
            items=[ImageAsset(content=image_content, filename=filename)],
        )

        saved_files = assets.save()

        if saved_files:
            callback_context.state["generated_image_url"] = saved_files[0]["url"]
            callback_context.state["generated_image_path"] = saved_files[0]["path"]
            logging.info(f"[image_generation_agent] Image saved to {saved_files[0]['url']}")
        else:
            logging.error("[image_generation_agent] Failed to save image.")

    except Exception as e:
        logging.error(f"[image_generation_agent] Error saving image: {e}")


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
