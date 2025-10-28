# Asset Server

A FastAPI server for browsing and serving static assets from the `asset_server_root/` directory.

## Features

- **Web-based file browser** - Navigate sessions, asset types, and files through a clean UI
- **Session organization** - Automatically organizes assets by session ID
- **Asset type categorization** - Groups files by type (reports, images, videos, etc.)
- **Direct file access** - Serves all static files under the `/assets` path
- **Metadata display** - Shows file sizes, modification times, and counts

## Installation

Make sure you have the required dependencies installed:

```bash
uv add fastapi uvicorn
```

## Usage

### Running the server

From the project root directory:

```bash
python -m src.asset_server.server
```

Or from the `src/asset_server` directory:

```bash
python server.py
```

The server will start on `http://0.0.0.0:8550` by default.

### Browsing Assets

The server provides a web-based file browser with the following routes:

- **Home** (`http://localhost:8550/`): Lists all session folders
  - Shows session IDs with their asset types
  - Displays modification times and file counts
  - Click any session to browse its contents

- **Session View** (`http://localhost:8550/browse/{session_id}`): View asset types in a session
  - Lists all asset type folders (e.g., "reports", "images")
  - Shows file counts and last modified times
  - Click any asset type to see files

- **Asset Type View** (`http://localhost:8550/browse/{session_id}/{asset_type}`): View files
  - Lists all files in the asset type folder
  - Shows file sizes and modification times
  - Click any file to view/download it

### Direct File Access

Files can be accessed directly via the `/assets` path:

```
http://localhost:8550/assets/{session_id}/{asset_type}/{filename}
```

Example:
```
http://localhost:8550/assets/abc123/reports/research_report.md
```

## Configuration

You can customize the host and port by modifying the `start_server()` call in `server.py`:

```python
if __name__ == "__main__":
    start_server(host="127.0.0.1", port=8080)
```

## Directory Structure

Assets are organized by session and type:

```
GTMForge/
├── asset_server_root/           # Root directory for all assets
│   ├── {session_id_1}/          # Session-specific folder
│   │   ├── reports/             # Asset type folder
│   │   │   └── research_report.md
│   │   ├── images/
│   │   │   ├── chart_1.png
│   │   │   └── diagram.jpg
│   │   └── videos/
│   │       └── demo.mp4
│   ├── {session_id_2}/
│   │   └── reports/
│   │       └── analysis.md
│   └── index.html               # Legacy file (optional)
└── src/
    └── asset_server/            # FastAPI server code
        ├── __init__.py
        ├── server.py
        └── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Lists all sessions with navigation UI |
| `/browse/{session_id}` | GET | Lists asset types in a session |
| `/browse/{session_id}/{asset_type}` | GET | Lists files in an asset type |
| `/assets/{path}` | GET | Direct file access (static files) |

## Integration with GTMForge

The asset server integrates with the GTMForge agent system through the `save_assets()` utility function:

```python
from forge.utils.asset_services import save_assets
from forge.data_models import ReportAsset

# Create a report asset
report = ReportAsset(content="# My Report\n\nContent here")

# Save it (automatically creates session/type folders)
saved_files = save_assets(
    session_id="abc123",
    asset_type="reports",
    assets=[report],
    mime_type="text/markdown"
)

# Access via: http://localhost:8550/assets/abc123/reports/research_report.md
```
