# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Callback utilities for GTMForge agents.

This module provides factory functions to reduce boilerplate when creating
callbacks for saving agent outputs to the asset server.
"""

import base64
import logging
from pathlib import Path
from typing import Callable, Optional, Type

from google.adk.agents.callback_context import CallbackContext
from forge.data_models import AssetBase, Assets, ReportAsset, ImageAsset


def create_asset_save_callback(
    state_key: str,
    asset_type: str,
    filename: str,
    asset_class: Type[AssetBase] = ReportAsset,
    url_state_key: Optional[str] = None,
    path_state_key: Optional[str] = None,
) -> Callable[[CallbackContext], None]:
    """Factory function to create asset-saving callbacks with minimal boilerplate.

    This factory generates a callback function that:
    1. Reads content from callback_context.state using the specified state_key
    2. Validates that content exists
    3. Creates an Assets collection with the specified parameters
    4. Saves to the asset server
    5. Stores the resulting URL and path back in state

    Args:
        state_key: Key to read content from callback_context.state.
            This should match the agent's output_key parameter.
        asset_type: Type of asset for directory organization.
            Examples: "reports", "briefs", "website_specs", "images"
        filename: Filename to save the asset as.
            Example: "research_report.md", "gtm_brief.md"
        asset_class: Pydantic model class for the asset (default: ReportAsset).
            Use ReportAsset for markdown/text, ImageAsset for images, etc.
        url_state_key: State key for storing the asset URL.
            Defaults to f"{state_key}_asset_url" if not provided.
        path_state_key: State key for storing the asset file path.
            Defaults to f"{state_key}_asset_path" if not provided.

    Returns:
        A callback function compatible with ADK's after_agent_callback parameter.

    Example:
        >>> from forge.utils.callbacks import create_asset_save_callback
        >>>
        >>> agent = Agent(
        ...     name="my_agent",
        ...     output_key="my_output",
        ...     after_agent_callback=create_asset_save_callback(
        ...         state_key="my_output",
        ...         asset_type="reports",
        ...         filename="my_report.md"
        ...     )
        ... )

    Example with custom asset class:
        >>> callback = create_asset_save_callback(
        ...     state_key="product_image",
        ...     asset_type="images",
        ...     filename="hero.png",
        ...     asset_class=ImageAsset
        ... )

    Note:
        The generated callback will raise ValueError if:
        - The state_key is not found in callback_context.state
        - The Assets.save() operation fails
        - The save operation returns an empty list
    """
    # Use smart defaults for state keys
    url_key = url_state_key or f"{state_key}_asset_url"
    path_key = path_state_key or f"{state_key}_asset_path"

    def callback(callback_context: CallbackContext) -> None:
        """Generated callback that saves agent output to asset server."""

        # Step 1: Get content from state
        content = callback_context.state.get(state_key)

        # Step 2: Validate content exists
        if not content:
            raise ValueError(
                f"No {state_key} found in state. The '{state_key}' "
                f"key is missing or empty. Ensure the agent with "
                f"output_key='{state_key}' ran successfully."
            )
        
        # Step 2.5: Convert dict/list to string if needed
        if isinstance(content, (dict, list)):
            import json
            logging.info(f"Converting {state_key} from {type(content).__name__} to JSON string")
            content = json.dumps(content, indent=2, ensure_ascii=False)

        # Step 3: Get session_id from invocation context
        session_id = callback_context._invocation_context.session.id

        # Step 4: Create Assets collection
        assets = Assets(
            session_id=session_id,
            asset_type=asset_type,
            items=[asset_class(content=content, filename=filename)],
        )

        # Step 5: Save and handle errors
        try:
            saved_files = assets.save()

            if not saved_files:
                raise ValueError("Assets.save() returned empty list")

            # Step 6: Store URLs in state for downstream agents
            callback_context.state[url_key] = saved_files[0]["url"]
            callback_context.state[path_key] = saved_files[0]["path"]

            logging.info(
                f"Asset '{state_key}' saved successfully to {saved_files[0]['url']}"
            )

        except Exception as e:
            logging.error(f"Failed to save asset '{state_key}': {e}")
            raise ValueError(
                f"Failed to save asset '{state_key}' to asset server: {e}"
            ) from e

    # Set a descriptive name for the generated callback
    callback.__name__ = f"save_{state_key}_callback"
    callback.__doc__ = f"Saves {state_key} to asset server as {asset_type}/{filename}"

    return callback


def create_image_extraction_callback(
    prompt_state_key: str,
    asset_type: str,
    results_state_key: str,
    filename_prefix: Optional[str] = None,
) -> Callable[[CallbackContext], None]:
    """Factory function to create image extraction callbacks for model responses.

    This factory generates an after_model_callback that:
    1. Extracts the current prompt/metadata from state
    2. Extracts generated image data from the model response (inline_data blobs)
    3. Saves the image to the asset server
    4. Creates a metadata structure with image path and prompt info
    5. Appends the result to a results list in state

    Designed specifically for gemini-2.5-flash-image which returns images as
    inline_data blobs in the response parts.

    Args:
        prompt_state_key: State key containing the current prompt metadata.
            Expected to have fields like: screen_name, imagen_prompt, index
        asset_type: Type of asset for directory organization (e.g., "mockups")
        results_state_key: State key for storing the list of results
        filename_prefix: Optional prefix for generated filenames.
            If not provided, uses screen_name from prompt data.

    Returns:
        A callback function compatible with ADK's after_model_callback parameter.

    Example:
        >>> callback = create_image_extraction_callback(
        ...     prompt_state_key="current_mockup_prompt",
        ...     asset_type="mockups",
        ...     results_state_key="mockup_results"
        ... )
        >>>
        >>> agent = LlmAgent(
        ...     name="image_gen",
        ...     model="gemini-2.5-flash-image",
        ...     after_model_callback=callback
        ... )

    Note:
        The callback expects the model response to contain image data in
        response.candidates[0].content.parts[].inline_data format.
    """

    def callback(callback_context: CallbackContext, llm_response=None) -> None:
        """Generated callback that extracts and saves image from model response."""

        # Step 1: Get current prompt metadata
        prompt_data = callback_context.state.get(prompt_state_key)
        if not prompt_data:
            logging.warning(
                f"No prompt data found at '{prompt_state_key}'. Skipping image extraction."
            )
            return

        # Step 2: Extract image from model response
        # The response is passed as a parameter
        response = llm_response
        if not response:
            logging.error("No model response available. Cannot extract image.")
            return

        # Extract image data from response parts
        image_data = None
        mime_type = None

        try:
            # gemini-2.5-flash-image returns images in inline_data format
            if hasattr(response, "candidates") and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, "content") and candidate.content:
                    for part in candidate.content.parts:
                        if hasattr(part, "inline_data") and part.inline_data:
                            image_data = part.inline_data.data
                            mime_type = part.inline_data.mime_type
                            break

            if not image_data:
                logging.error(
                    "No image data found in model response. "
                    "Expected inline_data format from gemini-2.5-flash-image."
                )
                return

        except Exception as e:
            logging.error(f"Error extracting image from response: {e}")
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

        prefix = filename_prefix or safe_screen_name
        filename = f"{index:02d}_{prefix}.{extension}"

        # Step 4: Save binary image data
        session_id = callback_context._invocation_context.session.id

        # inline_data.data is already raw binary bytes (not base64)
        # Just use it directly
        image_binary = image_data

        try:
            # Create a simple object with content field containing binary data
            from types import SimpleNamespace
            binary_asset = SimpleNamespace(content=image_binary, filename=filename)

            # Save binary directly to asset server
            from forge.utils.asset_services import save_assets
            saved_files = save_assets(
                session_id=session_id,
                asset_type=asset_type,
                assets=[binary_asset],
                mime_type=mime_type,
            )

            if not saved_files:
                logging.error("Failed to save image: Assets.save() returned empty list")
                return

            image_url = saved_files[0]["url"]
            image_path = saved_files[0]["path"]

            logging.info(
                f"Image saved for '{screen_name}' at {image_url}"
            )

        except Exception as e:
            logging.error(f"Failed to save image for '{screen_name}': {e}")
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
        results = callback_context.state.get(results_state_key, [])
        if not isinstance(results, list):
            results = []

        results.append(result)
        callback_context.state[results_state_key] = results

        logging.info(
            f"Added mockup result for '{screen_name}'. Total results: {len(results)}"
        )

    # Set descriptive name
    callback.__name__ = f"extract_and_save_image_callback"
    callback.__doc__ = f"Extracts image from model response and saves to {asset_type}"

    return callback
