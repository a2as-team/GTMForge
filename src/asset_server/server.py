"""FastAPI server for serving static assets."""

import os
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn

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
            # Determine icon based on file extension
            ext = file['path'].suffix.lower()
            icon = {
                '.md': '📝', '.txt': '📄', '.html': '🌐',
                '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️',
                '.mp4': '🎬', '.webm': '🎬', '.mov': '🎬',
                '.json': '📋', '.pdf': '📕'
            }.get(ext, '📄')

            file_url = f"/assets/{session_id}/{asset_type}/{file['name']}"
            items.append(f"""
            <li class="item">
                <div class="item-name">
                    <span class="item-icon">{icon}</span>
                    <a href="{file_url}" target="_blank">{file['name']}</a>
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
