# Asset Saving Guide

This guide covers best practices for saving agent-generated assets in GTMForge using the asset service and callback system.

## Overview

GTMForge provides a comprehensive asset management system that allows agents to save their outputs (reports, briefs, images, videos, etc.) to a centralized asset server with automatic organization by session and type.

## Architecture

### Components

1. **Data Models** (`src/agent_root/forge/data_models.py`)
   - Pydantic models defining asset structure
   - Type-safe asset definitions with default MIME types

2. **Asset Service** (`src/agent_root/forge/utils/asset_services.py`)
   - Core function for saving assets to disk
   - Handles file naming, directory creation, and metadata

3. **Asset Server** (`src/asset_server/server.py`)
   - FastAPI server for browsing and serving assets
   - Web-based file browser with session organization

4. **Agent Callbacks**
   - ADK `after_agent_callback` hooks
   - Automatically save agent outputs after completion

## Directory Structure

Assets are organized by session ID and asset type:

```
asset_server_root/
├── {session_id_1}/
│   ├── reports/
│   │   └── research_report.md
│   ├── briefs/
│   │   └── gtm_brief.md
│   ├── images/
│   │   ├── chart_1.png
│   │   └── diagram.jpg
│   └── videos/
│       └── demo.mp4
└── {session_id_2}/
    └── reports/
        └── analysis.md
```

## Data Models

### AssetBase

Base model for all assets with common fields:

```python
class AssetBase(BaseModel):
    content: str                    # Asset content
    mime_type: str = "text/plain"   # MIME type (with default)
    filename: Optional[str] = None  # Optional custom filename
```

### Predefined Asset Types

| Model | Default MIME Type | Use Case |
|-------|------------------|----------|
| `ReportAsset` | `text/markdown` | Research reports, documentation |
| `DocumentAsset` | `text/markdown` | Generic documents |
| `ImageAsset` | `image/png` | Generated or processed images |
| `VideoAsset` | `video/mp4` | Video content |

### Custom MIME Types

All asset types support custom MIME types:

```python
# Override default MIME type
ReportAsset(
    content="<h1>Report</h1>",
    mime_type="text/html",  # Override default markdown
    filename="report.html"
)

ImageAsset(
    content="base64_jpeg_data",
    mime_type="image/jpeg",  # Override default png
    filename="photo.jpg"
)
```

## Assets Container

The `Assets` class provides a clean API for saving multiple assets at once, even with different MIME types:

```python
from forge.data_models import Assets, ReportAsset, ImageAsset

assets = Assets(
    session_id="session_123",
    asset_type="campaign_materials",
    items=[
        ReportAsset(content="# Report", filename="report.md"),
        ImageAsset(content="base64_png", filename="chart.png"),
        ImageAsset(content="base64_jpg", filename="photo.jpg", mime_type="image/jpeg"),
    ]
)

# Save all assets - automatically groups by MIME type
saved_files = assets.save()

# Access saved file metadata
for file in saved_files:
    print(f"Saved: {file['url']}")  # /assets/session_123/campaign_materials/report.md
```

### Assets.save() Return Value

```python
[
    {
        "filename": "report.md",
        "path": "/full/path/to/file",
        "url": "/assets/session_id/asset_type/report.md"
    },
    ...
]
```

## Creating Agent Callbacks

### Basic Pattern

```python
import logging
from google.adk.agents.callback_context import CallbackContext
from forge.data_models import Assets, ReportAsset

def save_output_callback(callback_context: CallbackContext) -> None:
    """Save agent output to asset server."""

    # 1. Get output from state (matches agent's output_key)
    output = callback_context.state.get("output_key_name")

    if not output:
        raise ValueError("Output not found in state")

    # 2. Get session ID
    session_id = callback_context._invocation_context.session.id

    # 3. Create Assets collection
    assets = Assets(
        session_id=session_id,
        asset_type="your_type",  # e.g., "reports", "briefs", "images"
        items=[
            ReportAsset(
                content=output,
                filename="output.md"  # Or generate dynamically
            )
        ],
    )

    # 4. Save and store metadata
    try:
        saved_files = assets.save()

        # Store URLs in state for downstream agents
        callback_context.state["output_asset_url"] = saved_files[0]["url"]
        callback_context.state["output_asset_path"] = saved_files[0]["path"]

        logging.info(f"Saved to {saved_files[0]['url']}")

    except Exception as e:
        logging.error(f"Failed to save: {e}")
        raise ValueError(f"Save failed: {e}") from e
```

### Attaching to Agents

```python
from google.adk import Agent

my_agent = Agent(
    name="my_agent",
    description="Agent description",
    instruction="...",
    output_key="output_key_name",  # Must match state key in callback
    after_agent_callback=save_output_callback,  # Attach callback
)
```

## Real-World Examples

### Example 1: Research Report Callback

From `src/agent_root/forge/agents/deep_research/agent.py`:

```python
def save_report_callback(callback_context: CallbackContext) -> None:
    """Saves the final research report to the asset server."""

    final_report = callback_context.state.get("final_cited_research_report")

    if not final_report:
        raise ValueError("No final report found in state")

    session_id = callback_context._invocation_context.session.id

    assets = Assets(
        session_id=session_id,
        asset_type="reports",
        items=[ReportAsset(content=final_report, filename="research_report.md")],
    )

    saved_files = assets.save()
    callback_context.state["report_asset_url"] = saved_files[0]["url"]
    callback_context.state["report_asset_path"] = saved_files[0]["path"]
    logging.info(f"Report saved to {saved_files[0]['url']}")

research_pipeline = SequentialAgent(
    name="research_pipeline",
    description="...",
    sub_agents=[...],
    after_agent_callback=save_report_callback,
)
```

### Example 2: GTM Brief Callback

From `src/agent_root/forge/agents/ideation_agent/agent.py`:

```python
def save_company_brief_callback(callback_context: CallbackContext) -> None:
    """Saves the GTM company brief to the asset server."""

    company_brief = callback_context.state.get("company_brief")

    if not company_brief:
        raise ValueError("No company brief found in state")

    session_id = callback_context._invocation_context.session.id

    assets = Assets(
        session_id=session_id,
        asset_type="briefs",
        items=[ReportAsset(content=company_brief, filename="gtm_brief.md")],
    )

    saved_files = assets.save()
    callback_context.state["company_brief_asset_url"] = saved_files[0]["url"]
    callback_context.state["company_brief_asset_path"] = saved_files[0]["path"]

ideation_agent = Agent(
    name="ideation_agent",
    description="...",
    instruction="...",
    output_key="company_brief",
    after_agent_callback=save_company_brief_callback,
)
```

### Example 3: Multiple Asset Types

Saving different types of assets from one agent:

```python
def save_mixed_assets_callback(callback_context: CallbackContext) -> None:
    """Save multiple different asset types."""

    # Get different outputs from state
    report = callback_context.state.get("report")
    chart_data = callback_context.state.get("chart_base64")
    video_data = callback_context.state.get("video_bytes")

    session_id = callback_context._invocation_context.session.id

    assets = Assets(
        session_id=session_id,
        asset_type="mixed_output",
        items=[
            ReportAsset(content=report, filename="summary.md"),
            ImageAsset(content=chart_data, filename="chart.png"),
            VideoAsset(content=video_data, filename="demo.mp4"),
        ],
    )

    saved_files = assets.save()

    # Store all URLs
    for file in saved_files:
        key = f"{file['filename']}_url"
        callback_context.state[key] = file["url"]
```

## Best Practices

### 1. Consistent Naming

Use clear, descriptive asset types and filenames:

```python
# Good
asset_type="reports"
filename="market_research_report.md"

# Less clear
asset_type="output"
filename="file.md"
```

### 2. Error Handling

Always wrap save operations in try-except:

```python
try:
    saved_files = assets.save()
except Exception as e:
    logging.error(f"Failed to save: {e}")
    raise ValueError(f"Save failed: {e}") from e
```

### 3. State Management

Store asset URLs in state for downstream agents:

```python
# Store URLs with descriptive keys
callback_context.state["report_asset_url"] = saved_files[0]["url"]
callback_context.state["report_asset_path"] = saved_files[0]["path"]

# Downstream agents can access:
# report_url = ctx.state.get("report_asset_url")
```

### 4. MIME Type Accuracy

Use correct MIME types for proper file handling:

```python
# Text formats
ReportAsset(content="...", mime_type="text/markdown")
ReportAsset(content="<html>...", mime_type="text/html")
DocumentAsset(content="...", mime_type="text/plain")

# Images
ImageAsset(content="...", mime_type="image/png")
ImageAsset(content="...", mime_type="image/jpeg")
ImageAsset(content="...", mime_type="image/webp")

# Videos
VideoAsset(content=b"...", mime_type="video/mp4")
VideoAsset(content=b"...", mime_type="video/webm")
```

### 5. Filename Generation

Provide explicit filenames when possible:

```python
# Good: Explicit filename
ReportAsset(content="...", filename="q4_analysis.md")

# Acceptable: Uses default from 'name' field
ReportAsset(content="...", name="analysis")  # -> analysis.md

# Auto-generated: Falls back to asset_0.md
ReportAsset(content="...")
```

### 6. Session Organization

Use meaningful asset types to organize by session:

```python
# Separate by content type
asset_type="reports"     # Research outputs
asset_type="briefs"      # GTM briefs
asset_type="images"      # Generated visuals
asset_type="videos"      # Video content
asset_type="documents"   # Generic docs

# Or by purpose
asset_type="marketing_materials"
asset_type="investor_documents"
asset_type="product_specs"
```

## Asset Server Integration

### Starting the Asset Server

```bash
# Using Make
make dev-asset-server

# Or directly
python -m src.asset_server.server
```

Server runs on `http://localhost:8550`

### Browsing Assets

- **Home**: `http://localhost:8550/` - Lists all sessions
- **Session**: `http://localhost:8550/browse/{session_id}` - Lists asset types
- **Files**: `http://localhost:8550/browse/{session_id}/{asset_type}` - Lists files

### Direct File Access

```
http://localhost:8550/assets/{session_id}/{asset_type}/{filename}
```

Example:
```
http://localhost:8550/assets/abc123/reports/research_report.md
http://localhost:8550/assets/abc123/briefs/gtm_brief.md
```

## Testing

### Manual Testing

```python
from forge.data_models import Assets, ReportAsset

# Create test assets
assets = Assets(
    session_id="test_session",
    asset_type="test_reports",
    items=[
        ReportAsset(
            content="# Test Report\n\nThis is a test.",
            filename="test_report.md"
        )
    ]
)

# Save
saved = assets.save()

# Verify
print(f"Saved to: {saved[0]['url']}")
# Visit: http://localhost:8550/assets/test_session/test_reports/test_report.md
```

### Callback Testing

Test callbacks independently:

```python
from unittest.mock import Mock

# Create mock callback context
mock_context = Mock()
mock_context.state = {"company_brief": "# Test Brief\n\nContent"}
mock_context._invocation_context.session.id = "test_session"

# Call the callback
save_company_brief_callback(mock_context)

# Verify state was updated
assert "company_brief_asset_url" in mock_context.state
```

## Troubleshooting

### Common Issues

**Issue: "No output found in state"**
- Verify agent's `output_key` matches the key used in callback
- Check that agent completed successfully before callback runs

**Issue: "Assets.save() returned empty list"**
- Verify asset content is not empty
- Check file permissions on `asset_server_root/` directory
- Ensure MIME type is valid

**Issue: "File not accessible in browser"**
- Verify asset server is running (`make dev-asset-server`)
- Check the generated URL path
- Ensure session_id directory was created

### Debug Tips

1. **Enable logging**:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

2. **Check saved file paths**:
```python
saved_files = assets.save()
print(f"Path: {saved_files[0]['path']}")
# Verify file exists: ls -la {path}
```

3. **Inspect state after callback**:
```python
print(callback_context.state.get("report_asset_url"))
```

## Migration Guide

### From Direct File Writing

**Before:**
```python
import os
report_path = f"/path/to/files/{session_id}/report.md"
os.makedirs(os.path.dirname(report_path), exist_ok=True)
with open(report_path, "w") as f:
    f.write(report_content)
```

**After:**
```python
from forge.data_models import Assets, ReportAsset

assets = Assets(
    session_id=session_id,
    asset_type="reports",
    items=[ReportAsset(content=report_content, filename="report.md")]
)
assets.save()
```

### From save_assets() Function

**Before:**
```python
from forge.utils.asset_services import save_assets

saved = save_assets(
    session_id=session_id,
    asset_type="reports",
    assets=[report_asset],
    mime_type="text/markdown"
)
```

**After (Recommended):**
```python
from forge.data_models import Assets, ReportAsset

assets = Assets(
    session_id=session_id,
    asset_type="reports",
    items=[ReportAsset(content=content, filename="report.md")]
    # mime_type now on the asset itself
)
assets.save()
```

## Summary

### Quick Checklist

- [ ] Choose appropriate asset type (`reports`, `briefs`, `images`, etc.)
- [ ] Use correct asset model (`ReportAsset`, `ImageAsset`, etc.)
- [ ] Provide explicit filename when possible
- [ ] Set MIME type if not using default
- [ ] Create callback function that reads from state
- [ ] Attach callback via `after_agent_callback`
- [ ] Store asset URLs back in state
- [ ] Handle errors with try-except
- [ ] Test with asset server running

### Key Takeaways

1. **Use `Assets` model** for clean, type-safe asset management
2. **Each asset carries its own MIME type** - no need for global type
3. **Callbacks run automatically** after agent completion
4. **Store URLs in state** for downstream agent access
5. **Asset server provides browsing** at `http://localhost:8550/`
6. **Organization by session** keeps outputs clean and accessible
