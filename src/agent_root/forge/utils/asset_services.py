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

import mimetypes
from pathlib import Path
from typing import Any

from pydantic import BaseModel


# Get the project root directory (assuming this file is in src/agent_root/forge/utils/)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
ASSET_SERVER_ROOT = PROJECT_ROOT / "asset_server_root"


def save_assets(
    session_id: str,
    asset_type: str,
    assets: list[BaseModel],
    mime_type: str,
) -> list[dict[str, str]]:
    """Save assets to the asset server directory structure.

    Creates a folder structure: asset_server_root/{session_id}/{asset_type}/
    and saves each asset as an individual file.

    Note: For most use cases, prefer using the Assets model which provides
    a cleaner interface and handles mixed MIME types automatically:

        >>> from forge.data_models import Assets, ReportAsset, ImageAsset
        >>> assets = Assets(
        ...     session_id="session123",
        ...     asset_type="mixed",
        ...     items=[
        ...         ReportAsset(content="# Report", filename="report.md"),
        ...         ImageAsset(content="base64...", filename="chart.png")
        ...     ]
        ... )
        >>> saved = assets.save()  # Handles different mime types automatically

    Args:
        session_id: Unique identifier for the session
        asset_type: Type of asset (e.g., "images", "videos", "documents", "reports")
        assets: List of pydantic model instances representing the assets.
            See forge.data_models for standard asset models (ReportAsset,
            ImageAsset, DocumentAsset, etc.)
        mime_type: MIME type of the assets (e.g., "image/png", "text/html",
            "text/markdown")

    Returns:
        List of dictionaries containing information about saved files:
        [
            {
                "filename": "asset_0.png",
                "path": "/path/to/file",
                "url": "/assets/session_id/asset_type/asset_0.png"
            },
            ...
        ]

    Raises:
        ValueError: If the asset objects don't have a valid content field

    Example (direct usage):
        >>> from forge.data_models import ReportAsset
        >>> report = ReportAsset(content="# My Report\\n\\nContent here")
        >>> saved = save_assets("session123", "reports", [report], "text/markdown")
        >>> print(saved[0]["url"])
        /assets/session123/reports/research_report.md
    """
    # Create the directory structure
    asset_dir = ASSET_SERVER_ROOT / session_id / asset_type
    asset_dir.mkdir(parents=True, exist_ok=True)

    # Determine file extension from mime type
    extension = mimetypes.guess_extension(mime_type)
    if not extension:
        # Fallback to common extensions based on mime type
        extension = _get_extension_from_mime(mime_type)

    saved_files = []

    for idx, asset in enumerate(assets):
        # Try to get content from the asset object
        content = _extract_content(asset)

        # Generate filename
        filename = _generate_filename(asset, idx, extension)
        file_path = asset_dir / filename

        # Write the content to file
        if isinstance(content, bytes):
            file_path.write_bytes(content)
        else:
            file_path.write_text(str(content), encoding="utf-8")

        # Build the URL path for the asset server
        url_path = f"/assets/{session_id}/{asset_type}/{filename}"

        saved_files.append(
            {
                "filename": filename,
                "path": str(file_path),
                "url": url_path,
            }
        )

    return saved_files


def _extract_content(asset: BaseModel) -> Any:
    """Extract content from a pydantic asset object.

    Tries common field names: content, data, text, body, value.

    Args:
        asset: Pydantic object containing the asset data

    Returns:
        The content extracted from the asset

    Raises:
        ValueError: If no valid content field is found
    """
    # Try common field names
    for field_name in ["content", "data", "text", "body", "value"]:
        if hasattr(asset, field_name):
            return getattr(asset, field_name)

    # If no common field found, try to serialize the entire object
    if hasattr(asset, "model_dump_json"):
        return asset.model_dump_json(indent=2)

    raise ValueError(
        f"Could not extract content from asset object. "
        f"Expected one of: content, data, text, body, value. "
        f"Available fields: {list(asset.model_fields.keys())}"
    )


def _generate_filename(asset: BaseModel, index: int, extension: str) -> str:
    """Generate a filename for the asset.

    Tries to use the filename field first, then name/id fields, otherwise uses index.

    Args:
        asset: Pydantic object containing the asset
        index: Index of the asset in the list
        extension: File extension to use

    Returns:
        Generated filename
    """
    # Priority 1: Use explicit filename field if provided
    if hasattr(asset, "filename") and asset.filename:
        safe_name = str(asset.filename).replace("/", "_").replace("\\", "_")
        # If filename already has an extension, use it; otherwise add the default extension
        if not any(safe_name.endswith(ext) for ext in ['.md', '.txt', '.html', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.mp4', '.webm', '.mov', '.json', '.pdf']):
            safe_name += extension
        return safe_name

    # Priority 2: Try to get a name or id from the asset
    for field_name in ["name", "id", "title"]:
        if hasattr(asset, field_name):
            value = getattr(asset, field_name)
            if value:
                # Sanitize the filename
                safe_name = str(value).replace("/", "_").replace("\\", "_")
                if not safe_name.endswith(extension):
                    safe_name += extension
                return safe_name

    # Fallback to index-based naming
    return f"asset_{index}{extension}"


def _get_extension_from_mime(mime_type: str) -> str:
    """Get file extension from MIME type.

    Provides fallback mappings for common MIME types.

    Args:
        mime_type: MIME type string

    Returns:
        File extension including the dot (e.g., ".png")
    """
    mime_to_ext = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/svg+xml": ".svg",
        "video/mp4": ".mp4",
        "video/webm": ".webm",
        "video/quicktime": ".mov",
        "text/html": ".html",
        "text/plain": ".txt",
        "text/css": ".css",
        "text/javascript": ".js",
        "application/json": ".json",
        "application/pdf": ".pdf",
    }

    return mime_to_ext.get(mime_type.lower(), ".bin")
