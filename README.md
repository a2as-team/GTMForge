# GTMForge

A fullstack Go-To-Market (GTM) agent system built with Google's Agent Development Kit (ADK) and Gemini models.

## Quick Start

```bash
# Install dependencies
make install

# Run all services
make dev                # Backend + Frontend
make dev-asset-server   # Asset server (in separate terminal)
```

**Services:**
- Backend: http://localhost:8501
- Frontend: http://localhost:5173
- Asset Server: http://localhost:8550

## Documentation

- **[AGENTS.md](AGENTS.md)** - Complete development guide for AI agents and developers
- **[docs/asset-saving-guide.md](docs/asset-saving-guide.md)** - Asset management best practices
- **[src/asset_server/README.md](src/asset_server/README.md)** - Asset server usage

## Key Features

- **Multi-Agent System**: Research, ideation, pitch writing, asset generation
- **Asset Management**: Automatic saving and organization of agent outputs
- **Asset Server**: Web-based file browser for generated content
- **ADK Integration**: Built on Google's Agent Development Kit
- **Modern Stack**: Python 3.12+, React 19, FastAPI, Gemini models

## Architecture

GTMForge implements a sophisticated multi-agent workflow:

1. **Research & Analysis**: Deep research with citations, competitive insights
2. **Strategy & Content**: Ideation, pitch writing, prompt optimization
3. **Asset Generation**: Images (Imagen), videos (Veo), designs (Canva)
4. **Publishing & QA**: Quality assurance and content distribution

All agent outputs are automatically saved to `asset_server_root/` organized by session and asset type, accessible via the asset server.

See [AGENTS.md](AGENTS.md) for complete details.
