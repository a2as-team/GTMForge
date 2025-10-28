"""FastAPI server for serving static assets."""

import html
import os
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette import status

try:  # pragma: no cover - dependency ensured via pyproject
    import markdown as markdown_lib
except ImportError:  # pragma: no cover
    markdown_lib = None


MARKDOWN_EXTENSIONS = {".md", ".markdown"}

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
ASSET_ROOT = PROJECT_ROOT / "asset_server_root"

# Create FastAPI app
app = FastAPI(title="Asset Server", description="Serves static assets")


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def format_timestamp(timestamp: float) -> str:
    """Format timestamp in human-readable format."""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def generate_html(title: str, content: str) -> str:
    """Generate HTML page with consistent styling."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - Asset Server</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .header {{
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }}
            h1 {{
                color: #333;
                margin: 0;
            }}
            .breadcrumb {{
                color: #666;
                margin-top: 10px;
                font-size: 14px;
            }}
            .breadcrumb a {{
                color: #4CAF50;
                text-decoration: none;
            }}
            .breadcrumb a:hover {{
                text-decoration: underline;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .item-list {{
                list-style: none;
                padding: 0;
            }}
            .item {{
                padding: 15px;
                border-bottom: 1px solid #eee;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .item:hover {{
                background-color: #f9f9f9;
            }}
            .item:last-child {{
                border-bottom: none;
            }}
            .item-name {{
                flex: 1;
            }}
            .item-name a {{
                color: #333;
                text-decoration: none;
                font-weight: 500;
            }}
            .item-name a:hover {{
                color: #4CAF50;
            }}
            .item-actions {{
                margin-left: 12px;
                font-size: 13px;
            }}
            .item-actions a {{
                color: #4CAF50;
                text-decoration: none;
                margin-left: 8px;
            }}
            .item-actions a:first-child {{
                margin-left: 0;
            }}
            .item-icon {{
                margin-right: 10px;
                font-size: 20px;
            }}
            .item-meta {{
                color: #666;
                font-size: 14px;
                text-align: right;
            }}
            .empty-state {{
                text-align: center;
                padding: 40px;
                color: #666;
            }}
            .badge {{
                display: inline-block;
                background-color: #4CAF50;
                color: white;
                padding: 3px 10px;
                border-radius: 4px;
                font-size: 12px;
                margin-left: 10px;
            }}
            .inline-form {{
                display: inline-block;
                margin-left: 12px;
            }}
            .inline-form button {{
                background-color: #ff6961;
                border: none;
                color: white;
                padding: 6px 10px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 13px;
            }}
            .inline-form button:hover {{
                background-color: #ff4c41;
            }}
            .markdown-container {{
                background-color: white;
                padding: 24px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                line-height: 1.6;
            }}
            .markdown-container h1,
            .markdown-container h2,
            .markdown-container h3,
            .markdown-container h4,
            .markdown-container h5,
            .markdown-container h6 {{
                margin-top: 1.4em;
                margin-bottom: 0.6em;
            }}
            .markdown-container pre {{
                background-color: #1f1f1f;
                color: #f5f5f5;
                padding: 12px 16px;
                border-radius: 6px;
                overflow-x: auto;
            }}
            .markdown-container code {{
                background-color: rgba(27,31,35,0.05);
                padding: 2px 4px;
                border-radius: 4px;
            }}
            .markdown-container table {{
                border-collapse: collapse;
                width: 100%;
                margin: 16px 0;
            }}
            .markdown-container table th,
            .markdown-container table td {{
                border: 1px solid #e0e0e0;
                padding: 8px 12px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>GTMForge Asset Server</h1>
            {content}
        </div>
    </body>
    </html>
    """


def _ensure_markdown_available() -> None:
    if markdown_lib is None:
        raise HTTPException(
            status_code=500,
            detail="Markdown rendering library not available. Ensure 'markdown' dependency is installed.",
        )


def _read_markdown_file(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:  # pragma: no cover - fastapi handles
        raise HTTPException(status_code=404, detail="File not found") from exc
    except OSError as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="Unable to read markdown file") from exc


def _ensure_within_asset_root(path: Path) -> Path:
    try:
        resolved = path.resolve(strict=False)
    except FileNotFoundError:
        resolved = path.resolve()
    if not str(resolved).startswith(str(ASSET_ROOT.resolve())):
        raise HTTPException(status_code=400, detail="Invalid session path")
    return resolved


@app.get("/", response_class=HTMLResponse)
async def list_sessions():
    """List all session folders."""
    if not ASSET_ROOT.exists():
        ASSET_ROOT.mkdir(parents=True, exist_ok=True)

    sessions = []
    for item in ASSET_ROOT.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # Count asset types in this session
            asset_types = [d.name for d in item.iterdir() if d.is_dir()]
            sessions.append({
                "name": item.name,
                "path": item,
                "modified": item.stat().st_mtime,
                "asset_types": asset_types
            })

    # Sort by modification time (newest first)
    sessions.sort(key=lambda x: x["modified"], reverse=True)

    if not sessions:
        content = """
        <div class="container">
            <div class="empty-state">
                <h2>No Sessions Found</h2>
                <p>No asset sessions have been created yet.</p>
                <p>Assets will appear here once agents generate content.</p>
            </div>
        </div>
        """
    else:
        items_html = []
        for session in sessions:
            asset_count = len(session["asset_types"])
            asset_types_str = ", ".join(session["asset_types"]) if session["asset_types"] else "empty"
            items_html.append(f"""
            <li class="item">
                <div class="item-name">
                    <span class="item-icon">📁</span>
                    <a href="/browse/{session['name']}">{session['name']}</a>
                    <span class="badge">{asset_count} type(s)</span>
                    <form class="inline-form" method="post" action="/sessions/{session['name']}/delete" onsubmit="return confirm('Delete session {session['name']} and all assets?');">
                        <button type="submit">Delete</button>
                    </form>
                </div>
                <div class="item-meta">
                    {asset_types_str}<br>
                    {format_timestamp(session['modified'])}
                </div>
            </li>
            """)

        content = f"""
        <div class="breadcrumb">Home</div>
        <div class="container">
            <h2>Sessions ({len(sessions)})</h2>
            <ul class="item-list">
                {''.join(items_html)}
            </ul>
        </div>
        """

    return generate_html("Sessions", content)


@app.get("/browse/{session_id}", response_class=HTMLResponse)
async def browse_session(session_id: str):
    """Browse asset types in a session."""
    session_path = ASSET_ROOT / session_id

    if not session_path.exists() or not session_path.is_dir():
        raise HTTPException(status_code=404, detail="Session not found")

    asset_types = []
    for item in session_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            # Count files in this asset type
            files = [f for f in item.iterdir() if f.is_file()]
            asset_types.append({
                "name": item.name,
                "path": item,
                "file_count": len(files),
                "modified": item.stat().st_mtime
            })

    # Sort by name
    asset_types.sort(key=lambda x: x["name"])

    if not asset_types:
        items_html = """
        <div class="empty-state">
            <h3>No Assets</h3>
            <p>This session doesn't contain any assets yet.</p>
        </div>
        """
    else:
        items = []
        for asset_type in asset_types:
            items.append(f"""
            <li class="item">
                <div class="item-name">
                    <span class="item-icon">📂</span>
                    <a href="/browse/{session_id}/{asset_type['name']}">{asset_type['name']}</a>
                    <span class="badge">{asset_type['file_count']} file(s)</span>
                </div>
                <div class="item-meta">
                    {format_timestamp(asset_type['modified'])}
                </div>
            </li>
            """)
        items_html = f'<ul class="item-list">{"".join(items)}</ul>'

    content = f"""
    <div class="breadcrumb">
        <a href="/">Home</a> / {session_id}
    </div>
    <div class="container">
        <h2>Asset Types</h2>
        {items_html}
    </div>
    """

    return generate_html(f"Session: {session_id}", content)


@app.get("/browse/{session_id}/{asset_type}", response_class=HTMLResponse)
async def browse_asset_type(session_id: str, asset_type: str):
    """Browse files in an asset type folder."""
    asset_type_path = ASSET_ROOT / session_id / asset_type

    if not asset_type_path.exists() or not asset_type_path.is_dir():
        raise HTTPException(status_code=404, detail="Asset type not found")

    files = []
    for item in asset_type_path.iterdir():
        if item.is_file() and not item.name.startswith('.'):
            files.append({
                "name": item.name,
                "path": item,
                "size": item.stat().st_size,
                "modified": item.stat().st_mtime
            })

    # Sort by name
    files.sort(key=lambda x: x["name"])

    if not files:
        items_html = """
        <div class="empty-state">
            <h3>No Files</h3>
            <p>This asset type folder is empty.</p>
        </div>
        """
    else:
        items = []
        for file in files:
            ext = file['path'].suffix.lower()
            icon = {
                '.md': '📝', '.markdown': '📝', '.txt': '📄', '.html': '🌐',
                '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️',
                '.mp4': '🎬', '.webm': '🎬', '.mov': '🎬',
                '.json': '📋', '.pdf': '📕'
            }.get(ext, '📄')

            encoded_name = quote(file['name'])
            file_url = f"/assets/{session_id}/{asset_type}/{encoded_name}"
            display_name = html.escape(file['name'])

            if ext in MARKDOWN_EXTENSIONS:
                rendered_url = f"/render/{session_id}/{asset_type}/{encoded_name}"
                main_link = f"<a href=\"{rendered_url}\" target=\"_blank\">{display_name}</a>"
                extra_links = f"<span class=\"item-actions\"><a href=\"{rendered_url}\" target=\"_blank\">Rendered</a><a href=\"{file_url}\" target=\"_blank\">Raw</a></span>"
            else:
                main_link = f"<a href=\"{file_url}\" target=\"_blank\">{display_name}</a>"
                extra_links = ""

            items.append(f"""
            <li class="item">
                <div class="item-name">
                    <span class="item-icon">{icon}</span>
                    {main_link}
                    {extra_links}
                </div>
                <div class="item-meta">
                    {format_size(file['size'])}<br>
                    {format_timestamp(file['modified'])}
                </div>
            </li>
            """)
        items_html = f'<ul class="item-list">{"".join(items)}</ul>'

    content = f"""
    <div class="breadcrumb">
        <a href="/">Home</a> / <a href="/browse/{session_id}">{session_id}</a> / {asset_type}
    </div>
    <div class="container">
        <h2>Files</h2>
        {items_html}
    </div>
    """

    return generate_html(f"{asset_type} - {session_id}", content)


@app.get("/render/{session_id}/{asset_type}/{filename}", response_class=HTMLResponse)
async def render_markdown_asset(session_id: str, asset_type: str, filename: str):
    """Render a markdown asset as HTML."""

    file_path = ASSET_ROOT / session_id / asset_type / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    if file_path.suffix.lower() not in MARKDOWN_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Requested file is not markdown")

    _ensure_markdown_available()

    markdown_text = _read_markdown_file(file_path)
    html_body = markdown_lib.markdown(  # type: ignore[union-attr]
        markdown_text,
        extensions=["fenced_code", "tables"],
        output_format="html5",
    )

    encoded_name = quote(filename)
    raw_url = f"/assets/{session_id}/{asset_type}/{encoded_name}"

    breadcrumb = f"<a href=\"/\">Home</a> / <a href=\"/browse/{session_id}\">{session_id}</a> / <a href=\"/browse/{session_id}/{asset_type}\">{asset_type}</a> / {html.escape(filename)}"
    content = f"""
    <div class="breadcrumb">
        {breadcrumb}
    </div>
    <div class="markdown-container">
        <div class="item-actions" style="margin-bottom: 16px;">
            <a href="{raw_url}" target="_blank">View raw markdown</a>
        </div>
        {html_body}
    </div>
    """

    return generate_html(f"{filename} - {asset_type}", content)


@app.post("/sessions/{session_id}/delete")
async def delete_session(session_id: str):
    """Delete a session folder and all contained assets."""

    session_path = ASSET_ROOT / session_id
    if not session_path.exists() or not session_path.is_dir():
        raise HTTPException(status_code=404, detail="Session not found")

    resolved_path = _ensure_within_asset_root(session_path)

    try:
        shutil.rmtree(resolved_path)
    except OSError as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail="Failed to delete session") from exc

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


# Mount the asset_server_root directory to serve all static files
app.mount("/assets", StaticFiles(directory=str(ASSET_ROOT)), name="assets")


def start_server(host: str = "0.0.0.0", port: int = 8550):
    """Start the FastAPI server.

    Args:
        host: The host to bind to
        port: The port to bind to
    """
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
