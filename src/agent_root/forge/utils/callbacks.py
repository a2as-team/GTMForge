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

import logging
from typing import Callable, Optional, Type

from google.adk.agents.callback_context import CallbackContext
from forge.data_models import AssetBase, Assets, ReportAsset


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
