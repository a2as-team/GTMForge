# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GTMForge is a strategic go-to-market agent built with Google's Agent Development Kit (ADK) and Gemini models. It implements a sophisticated multi-agent workflow that creates GTM strategies, executes market research, and generates comprehensive business intelligence reports through an iterative refinement loop.

### Technology Stack

- **Backend**: Google ADK (Agent Development Kit), FastAPI, Python 3.12+, Google Gemini models
- **Frontend**: React 19, Vite, TypeScript, Tailwind CSS 4, Shadcn UI
- **Package Management**: uv (Python), npm (JavaScript)
- **Authentication**: Supports both Google AI Studio (API key) and Vertex AI (Google Cloud)

## Development Commands

### Setup
```bash
make install          # Install Python dependencies via uv and npm dependencies for frontend
uv sync              # Install Python dependencies only
npm --prefix src/frontend install  # Install frontend dependencies only
```

### Running the Application
```bash
make dev             # Run both backend and frontend concurrently
make dev-backend     # Run backend only (ADK web server on port 8501)
make dev-frontend    # Run frontend only (Vite dev server on port 5173)
```

The backend is served at `http://localhost:8501` and frontend at `http://localhost:5173`.

### Testing
```bash
pytest               # Run tests (configured in dev dependencies)
```

### Frontend-Specific Commands
```bash
cd src/frontend
npm run dev          # Start Vite dev server
npm run build        # Build for production (TypeScript + Vite)
npm run lint         # Run ESLint
npm run preview      # Preview production build
```

## Architecture

### Agent Hierarchy

The agent system follows a hierarchical multi-agent architecture defined in `src/agent_root/forge/`:

1. **Root Agent** (`forge/agent.py`): Main entry point that delegates to the deep research agent
2. **Deep Research Agent** (`forge/deep_research/agent.py`): Implements a two-phase workflow:

#### Phase 1: Plan & Refine (Human-in-the-Loop)
- `interactive_research_planner_agent`: Coordinates the planning process
- `plan_generator`: Creates/refines research plans with task type tagging (`[RESEARCH]`, `[DELIVERABLE]`)
- User reviews and approves plan before execution

#### Phase 2: Autonomous Research Execution
- `research_pipeline` (SequentialAgent): Orchestrates the research workflow
  - `section_planner`: Converts plan into structured report outline
  - `section_researcher`: Performs initial web searches and summarizes findings
  - `iterative_refinement_loop` (LoopAgent): Up to 5 iterations (configurable)
    - `research_evaluator`: Critiques research quality, generates follow-up queries
    - `escalation_checker`: Custom agent to break loop when research passes evaluation
    - `enhanced_search_executor`: Executes follow-up searches and integrates new findings
  - `report_composer`: Synthesizes final report with inline citations

### Key Architectural Patterns

- **State Management**: Uses `callback_context.state` and `session.state` to pass data between agents
- **Structured Outputs**: Pydantic models (`SearchQuery`, `Feedback`) with LLM schema validation
- **Callbacks**: `collect_research_sources_callback` and `citation_replacement_callback` handle citation tracking and formatting
- **Grounding Metadata**: Extracts source URLs and titles from Gemini's grounding chunks

### Configuration System

`src/agent_root/forge/config.py` provides centralized configuration:

- **ResearchConfiguration**: Model selection (`gemini-2.5-pro` for critic, `gemini-2.5-flash` for worker) and max iterations
- **PromptsConfiguration**: Auto-loads persona and other prompts from `prompts/forge/` directory
- **Environment Variables**:
  - `FORGE_PROMPTS_PATH`: Override prompts directory (default: `./prompts/forge`)
  - `GOOGLE_GENAI_USE_VERTEXAI`: Toggle between AI Studio (FALSE) and Vertex AI (True)
  - `GOOGLE_API_KEY`: API key for AI Studio
  - `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`: For Vertex AI

### Frontend Integration Points

The frontend (`src/frontend/`) expects specific agent names to update UI correctly:

- `section_researcher` & `enhanced_search_executor`: Track websites consulted
- `report_composer_with_citations`: Processes final report
- `interactive_planner_agent`: Updates AI messages during planning
- `plan_generator` & `section_planner`: Used for activity timeline labels

**Important**: If renaming agents in backend, update corresponding references in frontend code.

## Project Structure

```
gtmforge/
├── src/
│   ├── agent_root/forge/       # Backend agent code
│   │   ├── agent.py            # Root agent entry point
│   │   ├── config.py           # Configuration and settings
│   │   └── deep_research/      # Deep research agent implementation
│   │       └── agent.py        # Multi-agent research workflow
│   ├── frontend/               # React frontend application
│   └── README.md               # Detailed technical documentation
├── prompts/
│   └── forge/
│       └── persona.md          # Agent persona definition
├── docs/                       # Project documentation
├── pyproject.toml              # Python dependencies and project config
├── Makefile                    # Development commands
└── .env                        # Environment variables (not in version control)
```

## Development Workflow

### Backend Development

The ADK backend uses a special command structure. The Makefile's `make dev-backend` runs:
```bash
uv run adk web src/app --port 8501 --allow_origins="*"
```

Note: The `src/app` path referenced in the Makefile does not currently exist in the repository. The actual agent code is in `src/agent_root/forge/`. This may need to be corrected.

### Modifying Agent Behavior

- **Agent logic**: Edit agent definitions and instructions in `src/agent_root/forge/deep_research/agent.py`
- **Model selection**: Update `ResearchConfiguration` in `src/agent_root/forge/config.py`
- **Agent persona**: Edit `prompts/forge/persona.md`
- **Additional prompts**: Add `.md` files to `prompts/forge/` (auto-loaded into `config.prompts_config.extras`)

### Citation System

Citations use a special tag format that gets replaced by callbacks:
- In-report format: `<cite source="src-N" />`
- Processed to: `[Source Title](url)`
- Sources tracked via `url_to_short_id` mapping in callback context

## Important Notes

- Agent names are tightly coupled between backend and frontend for UI functionality
- The project was adapted from Gemini FullStack LangGraph Quickstart for the frontend
- Research loop iterations default to 5, configurable via `ResearchConfiguration.max_search_iterations`
- Tags in research plans (`[RESEARCH]`, `[DELIVERABLE]`, `[MODIFIED]`, `[NEW]`, `[IMPLIED]`) guide downstream agent execution
