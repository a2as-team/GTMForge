# GTMForge

**Multi-Agent AI System for Go-To-Market Automation**

GTMForge is a sophisticated multi-agent AI system built with **Google's Agent Development Kit (ADK)** that automates the creation of comprehensive go-to-market materials using Google's latest AI technologies including **Gemini 2.0**, **Vertex AI**, **Imagen**, and **Veo**.

> **Current Status:** Phase 0 - Pre-Build Setup ✅  
> **Next Phase:** Phase 1 - Foundation Build (Core Agent Development)

---

## Project Vision

GTMForge orchestrates multiple specialized AI agents to transform startup ideas into polished GTM assets:

- **Ideation Agent**: Expands user input into ICPs, pain points, and context
- **Comparative Insight Agent**: Benchmarks ideas vs. successful startups
- **Pitch Writer Agent**: Builds slide narratives and talking points
- **Prompt Forge Agent**: Generates and refines prompts for Imagen/Veo (with quality loop)
- **QA Agent**: Ensures validity of assets and compliance
- **Imagen Agent (Phase 2)**: Generates high-quality slide images with refinement
- **Veo Agent (Phase 2)**: Creates cinematic video trailers from images
- **Canva Agent (Phase 2)**: Automates pitch deck creation and formatting
- **Publisher Agent**: Combines outputs into deliverable manifests (Phase 3)

---

## Project Structure

```
GTMForge/
├── app/
│   ├── agents/     # Agent implementations
│   ├── core/       # ADK orchestration engine
│   └── utils/      # Helper functions and utilities
├── frontend/       # Web UI (React/Next.js/Vite)
├── prompts/        # AI prompt templates
├── output/
│   ├── images/     # Generated images from Imagen
│   └── videos/     # Generated videos from Veo
├── main.py         # CLI entry point
├── api.py          # FastAPI backend server
├── requirements.txt
├── .env.template
└── README.md
```

---

## Getting Started

### Prerequisites

- **Python 3.9+**
- **Google Cloud Project** with Vertex AI enabled
- **Gemini 2.0 API** access (Pro, Flash, Imagen, Veo)
- **Google Cloud Storage** bucket (for asset hosting)
- **Canva Connect API** access (optional, Phase 2+)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/DanielJEfres/GTMForge.git
   cd GTMForge
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.template .env
   # Edit .env with your API keys and configuration
   ```

### Configuration

Edit `.env` file with your credentials:

- **GCP_PROJECT_ID**: Your Google Cloud project ID
- **GOOGLE_APPLICATION_CREDENTIALS**: Path to service account JSON
- **GEMINI_API_KEY**: Gemini 2.0 API key
- **VERTEX_AI_PROJECT**: Vertex AI project configuration
- **GCS_BUCKET_NAME**: Google Cloud Storage bucket for assets

Refer to `.env.template` for complete configuration options.

---

## Build Phases

### Phase 0 - Pre-Build Setup ✅
- [x] Access + API Keys configuration
- [x] Environment setup (`.env.template`)
- [x] Repository structure created
- [x] Dependencies defined
- [x] `.gitignore` configured

### Phase 1 - Foundation Build ✅ COMPLETE
- [x] Build ADK Orchestrator with sequential pipeline
- [x] Define 6 core agents with structured schemas
- [x] Implement A2A-compatible folder structure
- [x] Implement MCP Integration placeholders
- [x] Test sequential agent flow successfully
- [x] CLI entry point with beautiful output
- [x] Comprehensive logging and configuration

### Phase 2 - Generative Media Integration ⏳ IN PROGRESS
- [x] Google Cloud API clients abstraction layer (GeminiImagenClient, VeoClient, CanvaConnectClient, GCSClient)
- [x] Imagen Agent with quality-based refinement loop
- [x] Veo Agent for cinematic video generation
- [x] Canva Agent for automated deck creation
- [x] Extended schemas for media outputs (ImagenOutput, VeoOutput, CanvaOutput, MediaGenerationOutput)
- [x] Sequential media generation stage in orchestrator
- [x] Asset manifest building and temporary storage
- [x] Structured logging throughout all media phases
- [ ] Phase 3: Real Vertex AI and Canva API integration
- [ ] Phase 3: GCS asset upload and URL generation
- [ ] Phase 3: MCP implementations for real data

### Phase 3 - QA and System Integration
- [ ] End-to-end testing
- [ ] Publisher Agent implementation
- [ ] FastAPI backend with WebSocket support
- [ ] CLI entry point
- [ ] Validation across multiple ideas

### Phase 4 - Frontend, UX, and Documentation
- [ ] Modern web frontend (React/Next.js/Vite)
- [ ] Real-time generation dashboard
- [ ] Visual enhancements and branding
- [ ] Architecture diagrams (Excalidraw)
- [ ] Complete documentation and user guides

### Phase 5 - Bake-Off Readiness
- [ ] Live demo preparation
- [ ] Judging criteria alignment
- [ ] Final submission materials

---

## Technology Stack

- **Google ADK**: Multi-agent orchestration (sequential, parallel, loop)
- **Gemini 2.0**: LLM reasoning and content generation
- **Vertex AI**: Cloud AI platform
- **Imagen**: Image generation (Phase 2)
- **Veo 3.1**: Video generation (Phase 2)
- **Canva Connect API**: Presentation automation (Phase 2)
- **Google Cloud Storage**: Asset hosting (Phase 3)
- **FastAPI**: Backend API server (Phase 3)

---

## Documentation

- **`implementation.md`**: Complete implementation roadmap
- Architecture diagrams: Coming in Phase 4
- Agent specifications: Coming in Phase 1

---

## Contributing

This project is part of the **Google Cloud AI Bake-Off** and is currently in active development.

1. Follow the implementation roadmap in `implementation.md`
2. Maintain folder structure and naming conventions
3. Add tests for new functionality
4. Keep documentation updated

---

## Team

**Author:** Daniel Efres  
**Collaborator:** Luis Sala (Google Cloud)  
**Codename:** GTMForge  
**Event:** Google Cloud AI Bake-Off 2025

---

## Links

- [Google ADK Documentation](https://cloud.google.com/agent-builder/docs)
- [Vertex AI](https://cloud.google.com/vertex-ai)
- [Gemini API](https://ai.google.dev/)
- [Imagen Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/image/overview)
- [Veo Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/video/overview)
