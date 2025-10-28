# AGENTS.md

This file provides guidance to Claude Code and other AI agents when working with code in this repository.

## Project Overview

**GTMForge** is a fullstack Go-To-Market (GTM) agent system built with Google's Agent Development Kit (ADK) and Gemini models. It implements a sophisticated multi-agent workflow that helps analyze business goals, develop GTM strategies, create compelling pitches, generate marketing assets, and automate content publishing.

### Technology Stack

- **Backend**: Google ADK (Agent Development Kit), FastAPI, Python 3.12+, Google Gemini models
- **Frontend**: React 19, Vite, TypeScript, Tailwind CSS 4, Shadcn UI
- **Package Management**: uv (Python), npm (JavaScript)
- **Authentication**: Supports both Google AI Studio (API key) and Vertex AI (Google Cloud)
- **ADK Version**: >=1.17.0

## Development Commands

### Setup
```bash
make install          # Install Python dependencies via uv and npm dependencies for frontend
uv sync              # Install Python dependencies only
npm --prefix src/frontend install  # Install frontend dependencies only
```

### Running the Application
```bash
make dev                # Run both backend and frontend concurrently
make dev-backend        # Run backend only (ADK web server on port 8501)
make dev-frontend       # Run frontend only (Vite dev server on port 5173)
make dev-asset-server   # Run asset server only (FastAPI on port 8550)
```

Services:
- **Backend**: `http://localhost:8501` - ADK web server with agent API
- **Frontend**: `http://localhost:5173` - React UI (Vite dev server)
- **Asset Server**: `http://localhost:8550` - Browse and serve generated assets

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

1. **Root Agent** (`forge/agent.py`): Main entry point named "forge" that serves as the coordinator for all GTM operations

2. **Specialized Agents** (`forge/agents/`): Domain-specific agents for different GTM tasks

### GTMForge Agent Ecosystem

#### Research & Analysis
- **Deep Research Agent** (`deep_research/agent.py`):
  - Implements a sophisticated two-phase workflow
  - Phase 1: Plan & Refine (Human-in-the-Loop)
  - Phase 2: Autonomous Research Execution with iterative refinement
  - Uses Google Search grounding for web-based research
  - Generates comprehensive cited reports with inline citations

- **Comparative Insight Agent** (`comparative_insight_agent/agent.py`):
  - Analyzes competitive landscape
  - Identifies market positioning opportunities
  - Compares features, pricing, and value propositions

#### Strategy & Content
- **Ideation Agent** (`ideation_agent/agent.py`):
  - Expands raw startup ideas into structured components
  - Generates Ideal Customer Profiles (ICPs)
  - Identifies key pain points and market context
  - Defines value propositions and differentiators
  - First agent in the GTMForge pipeline

- **Pitch Writer Agent** (`pitch_writer_agent/agent.py`):
  - Creates compelling pitch narratives
  - Tailors messaging for different audiences
  - Generates elevator pitches, investor decks, and sales scripts

- **Prompt Forge Agent** (`prompt_forge_agent/agent.py`):
  - Optimizes prompts for content generation
  - Ensures consistency across marketing materials
  - Adapts tone and style for different channels

#### Asset Generation
- **Imagen Agent** (`imagen_agent/agent.py`):
  - Generates images using Google's Imagen models
  - Creates visual assets for marketing campaigns
  - Produces social media graphics and illustrations

- **Veo Agent** (`veo_agent/agent.py`):
  - Generates videos using Google's Veo models
  - Creates promotional videos and product demos
  - Produces social media video content

- **Canva Agent** (`canva_agent/agent.py`):
  - Integrates with Canva API for design automation
  - Creates branded marketing materials
  - Generates templates and design assets

#### Publishing & Quality
- **Publisher Agent** (`publisher_agent/agent.py`):
  - Automates content distribution across channels
  - Manages social media posting
  - Coordinates multi-platform campaigns

- **QA Agent** (`qa_agent/agent.py`):
  - Reviews generated content for quality
  - Ensures brand consistency
  - Validates messaging alignment with strategy

### Key Architectural Patterns

- **State Management**: Uses `callback_context.state` and `session.state` to pass data between agents
- **Structured Outputs**: Pydantic models for type-safe data exchange between agents
- **Callbacks**: Custom callbacks like `collect_research_sources_callback` handle citation tracking and source aggregation
- **Asset Management**: Automated asset saving using `after_agent_callback` to persist agent outputs
  - `Assets` model for organizing files by session and type
  - Asset server (`http://localhost:8550`) for browsing and serving saved files
  - Supports mixed MIME types (markdown, images, videos, etc.)
  - See `docs/asset-saving-guide.md` for complete documentation
- **Grounding Metadata**: Deep Research agent extracts source URLs and titles from Gemini's grounding chunks
- **Agent Tools**: Agents expose themselves as tools using `AgentTool` for delegation

### Configuration System

`src/agent_root/forge/config.py` provides centralized configuration:

- **ResearchConfiguration**: Model selection and parameters
  - `critic_model`: "gemini-2.5-pro" for evaluation tasks
  - `worker_model`: "gemini-2.5-flash" for generation tasks
  - `max_search_iterations`: 5 (configurable)

- **PromptsConfiguration**: Auto-loads prompts from `prompts/forge/` directory
  - `persona`: Main agent persona defining GTM expertise
  - `extras`: Additional .md files for specialized prompts

- **Environment Variables**:
  - `PROMPTS_PATH`: Override prompts directory (default: `./prompts/forge`)
  - `GOOGLE_GENAI_USE_VERTEXAI`: Toggle between AI Studio (FALSE) and Vertex AI (True)
  - `GOOGLE_API_KEY`: API key for AI Studio
  - `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`: For Vertex AI

### Frontend Integration Points

The frontend (`src/frontend/`) expects specific agent names to update UI correctly. When adding or renaming agents in the backend, update corresponding references in the frontend code.

## Project Structure

```
GTMForge/
├── src/
│   ├── agent_root/forge/       # Backend agent code
│   │   ├── agent.py            # Root "forge" agent entry point
│   │   ├── config.py           # Configuration and settings
│   │   ├── data_models.py      # Pydantic models for assets
│   │   ├── agents/             # Specialized agent implementations
│   │   │   ├── deep_research/       # Research agent with callbacks
│   │   │   ├── ideation_agent/      # ICP and market analysis
│   │   │   ├── comparative_insight_agent/  # Competitive analysis
│   │   │   ├── pitch_writer_agent/  # Pitch creation
│   │   │   ├── prompt_forge_agent/  # Prompt optimization
│   │   │   ├── imagen_agent/        # Image generation
│   │   │   ├── veo_agent/           # Video generation
│   │   │   ├── canva_agent/         # Design automation
│   │   │   ├── publisher_agent/     # Content distribution
│   │   │   └── qa_agent/            # Quality assurance
│   │   └── utils/              # Utility modules
│   │       └── asset_services.py    # Asset saving utilities
│   ├── asset_server/           # FastAPI asset server
│   │   ├── server.py           # Asset browsing and serving
│   │   └── README.md           # Asset server documentation
│   └── frontend/               # React frontend application
├── asset_server_root/          # Saved assets (organized by session)
├── prompts/
│   └── forge/
│       └── persona.md          # GTM expert persona definition
├── docs/                       # Project documentation
│   └── asset-saving-guide.md   # Asset management best practices
├── adk-expert/                 # ADK knowledge base (see below)
├── archive/                    # Archived/deprecated code
├── pyproject.toml              # Python dependencies (uv)
├── Makefile                    # Development commands
└── .env                        # Environment variables (not in version control)
```

## Development Workflow

### Backend Development

The ADK backend uses the ADK CLI. The Makefile's `make dev-backend` runs:
```bash
uv run adk web src/agent_root --port 8501 --allow_origins="*" --reload_agents
```

The `--reload_agents` flag enables hot-reloading during development.

### Modifying Agent Behavior

- **Agent logic**: Edit agent definitions in `src/agent_root/forge/agents/*/agent.py`
- **Model selection**: Update `ResearchConfiguration` in `src/agent_root/forge/config.py`
- **Agent persona**: Edit `prompts/forge/persona.md`
- **Additional prompts**: Add `.md` files to `prompts/forge/` (auto-loaded into `config.prompts_config.extras`)
- **Frontend integration**: Update agent name references in `src/frontend/` when renaming agents

### Adding New Agents

1. Create a new directory in `src/agent_root/forge/agents/your_agent_name/`
2. Add `__init__.py` and `agent.py` files
3. Define your agent using ADK's `LlmAgent`, `SequentialAgent`, or custom `BaseAgent`
4. Register the agent in the parent agent or root agent using `AgentTool`
5. Update frontend if the agent needs UI representation

### Citation System (Deep Research Agent)

Citations use a special tag format that gets replaced by callbacks:
- In-report format: `<cite source="src-N" />`
- Processed to: `[Source Title](url)`
- Sources tracked via `url_to_short_id` mapping in callback context
- `collect_research_sources_callback` aggregates all sources from grounding metadata

## Using the ADK Expert Knowledge Base

The `adk-expert/` directory contains a comprehensive knowledge base for developing agents with Google's ADK. This is an essential resource for understanding ADK concepts, patterns, and best practices.

### What is adk-expert?

The adk-expert directory is a curated knowledge base containing:
- **Core Concepts**: Agents, Tools, Context Management, Runtime, Sessions & State
- **API Reference**: Auto-generated SDK documentation + hand-curated guides
- **Official Examples**: 28+ production Python agent examples (marketing-agency, blog-writer, RAG, etc.)
- **API Documentation**: Complete Sphinx-generated docs for ADK main and v1.17.0 (checked into git)
- **Best Practices**: Design patterns, multimedia rendering, security
- **Testing Guides**: pytest strategies, mocking, evaluation
- **Code Templates**: Ready-to-use agent templates for quick starts
- **Integrations**: Google services, LangChain, MCP, observability tools
- **Advanced Topics**: Grounding, evaluation, deployment, streaming

### Quick Start with adk-expert

The adk-expert knowledge base is included in this repository. No additional setup is required - all documentation and resources are ready to use.

### Searching the Knowledge Base

**For AI Agents (Claude Code, etc.):**

When you need information about ADK, search the knowledge base using standard file search tools:

**IMPORTANT: Search adk-expert directories first** before attempting to implement ADK features:

```bash
# Search for concepts/patterns in knowledge base using Grep
Grep(pattern="multi-agent", path="adk-expert/knowledge-base", output_mode="files_with_matches")

# Find official Python examples (28+ real-world agents)
Glob(pattern="adk-expert/repositories/adk-samples/python/agents/*/agent.py")
Grep(pattern="marketing|research|blog", path="adk-expert/repositories/adk-samples/python/agents")

# Search skill templates
Glob(pattern="adk-expert/skill/adk-expert/assets/templates/*.py")

# Search API documentation
Glob(pattern="adk-expert/docs/main/**/*.html")

# Search references
Glob(pattern="adk-expert/skill/adk-expert/references/*.md")
```

**Primary search targets:**
- `adk-expert/knowledge-base/` - Comprehensive documentation, examples, and guides
- `adk-expert/repositories/adk-samples/python/agents/` - **28+ official production agent examples**
- `adk-expert/docs/` - Complete Sphinx-generated API documentation (main & v1.17.0)
- `adk-expert/skill/adk-expert/assets/templates/` - Production-ready code templates
- `adk-expert/skill/adk-expert/references/` - Quick patterns, troubleshooting, API reference

**When to search the knowledge base:**
- Understanding ADK concepts (agents, tools, state, events)
- Finding implementation patterns and examples
- Locating specific API documentation
- Learning best practices
- Getting code templates
- Troubleshooting errors

**Search workflow:**
1. Use Grep to find relevant files by keyword
2. Use Glob to locate specific file types or patterns
3. Read the matched files for detailed information
4. Check related files in the same directory for context

### Knowledge Base Structure

```
adk-expert/
├── knowledge-base/              # Comprehensive documentation
│   ├── core-concepts/           # Fundamental ADK concepts
│   │   ├── 01-agents.md         # Agent types and patterns
│   │   ├── 02-tools.md          # Tool design and usage
│   │   ├── 03-context-management.md  # Events, callbacks, artifacts
│   │   ├── 04-runtime.md        # Runner and event loop
│   │   └── 05-sessions-state.md # State management
│   ├── api-reference/           # API docs and patterns
│   ├── best-practices/          # Design patterns and guidelines
│   ├── examples/                # Code samples and demos
│   ├── testing/                 # pytest strategies
│   ├── integrations/            # Third-party integrations
│   └── advanced/                # Streaming, grounding, deployment
├── repositories/                # Official ADK source code and examples
│   ├── adk-samples/             # Production agent examples
│   │   └── python/agents/       # 28+ Python agent examples
│   │       ├── marketing-agency/     # Multi-agent marketing system
│   │       ├── blog-writer/          # Content generation agent
│   │       ├── academic-research/    # Research agent
│   │       ├── customer-service/     # Customer support agent
│   │       ├── RAG/                  # Retrieval-augmented generation
│   │       ├── podcast_transcript_agent/  # Multi-agent podcast system
│   │       └── ...22 more examples
│   ├── adk-python/              # ADK Python library source
│   └── adk-docs/                # Official documentation source
├── docs/                        # Sphinx-generated API documentation (checked into git)
│   ├── main/                    # Latest development docs
│   ├── v1.17.0/                 # Stable release docs
│   └── index.html               # Documentation entry point
├── skill/adk-expert/            # Quick reference and templates
│   ├── assets/templates/        # Production-ready code templates
│   │   ├── agent_basic.py       # Simple LLM agent
│   │   ├── agent_with_tools.py  # Agent with custom tools
│   │   ├── multi_agent.py       # Multi-agent coordinator
│   │   ├── callback_example.py  # Lifecycle callbacks
│   │   ├── memory_example.py    # Long-term memory
│   │   └── test_template.py     # pytest test suite
│   ├── references/              # Quick lookups
│   │   ├── quick-patterns.md    # Common code patterns
│   │   ├── troubleshooting.md   # Error solutions
│   │   └── api-quick-ref.md     # API reference
│   └── scripts/                 # Helper scripts
├── README.md                    # Knowledge base overview
├── TABLE_OF_CONTENTS.md         # Complete navigation
└── QUICK_REFERENCE.md           # Fast syntax lookup
```

### Key Resources in adk-expert

1. **repositories/adk-samples/python/agents/**: **28+ official production agent examples** (START HERE)
   - marketing-agency, blog-writer, academic-research, RAG, customer-service, and more
2. **docs/**: Complete Sphinx API documentation (checked into git, no build required)
   - `docs/main/` - Latest development version
   - `docs/v1.17.0/` - Stable release
3. **skill/adk-expert/assets/templates/**: Ready-to-use code templates for quick starts
4. **skill/adk-expert/references/**: Quick patterns, troubleshooting, API reference
5. **knowledge-base/core-concepts/**: Essential ADK architecture
6. **knowledge-base/examples/**: Annotated code samples with explanations
7. **knowledge-base/testing/**: Comprehensive pytest guide
8. **TABLE_OF_CONTENTS.md**: Complete navigation of all topics
9. **QUICK_REFERENCE.md**: Fast syntax lookup for common patterns

### Using adk-expert in Development

**When building new agents:**
1. **Start with official examples**: Browse `adk-expert/repositories/adk-samples/python/agents/`
   - Find similar agent: `Grep(pattern="marketing|research", path="adk-expert/repositories/adk-samples/python/agents")`
   - Read complete implementation: `Read adk-expert/repositories/adk-samples/python/agents/marketing-agency/marketing_agency/agent.py`
2. Check quick-start templates: Read `adk-expert/skill/adk-expert/assets/templates/agent_basic.py`
3. Search for patterns: `Grep(pattern="LlmAgent|SequentialAgent", path="adk-expert/knowledge-base")`
4. Review annotated examples in `knowledge-base/examples/`
5. Follow best practices in `knowledge-base/best-practices/`
6. Consult API reference: Read `adk-expert/skill/adk-expert/references/api-quick-ref.md`

**When debugging:**
1. Check troubleshooting guide: Read `adk-expert/skill/adk-expert/references/troubleshooting.md`
2. Search for error messages: `Grep(pattern="your error", path="adk-expert/knowledge-base")`
3. Review runtime documentation: Read `adk-expert/knowledge-base/core-concepts/04-runtime.md`
4. Check session/state management: Read `adk-expert/knowledge-base/core-concepts/05-sessions-state.md`

**When testing:**
1. Use test template: Read `adk-expert/skill/adk-expert/assets/templates/test_template.py`
2. Refer to testing guide: Read `adk-expert/knowledge-base/testing/README.md`
3. Review pytest patterns and fixtures documented there

**When integrating external services:**
1. Check integrations guide: Read `adk-expert/knowledge-base/integrations/README.md`
2. Search for specific integrations: `Grep(pattern="LangChain|MCP|Vertex", path="adk-expert/knowledge-base/integrations")`

**When looking up API details:**
1. Quick API reference: Read `adk-expert/skill/adk-expert/references/api-quick-ref.md`
2. Complete API docs: Browse `adk-expert/docs/v1.17.0/index.html` (or open in browser)
3. Source code examples: Read `adk-expert/repositories/adk-samples/python/agents/*/agent.py`

**Quick lookups:**
- Common patterns: Read `adk-expert/skill/adk-expert/references/quick-patterns.md`
- API reference: Read `adk-expert/skill/adk-expert/references/api-quick-ref.md`
- Full API docs: Browse `adk-expert/docs/v1.17.0/` (Sphinx HTML)
- Table of contents: Read `adk-expert/TABLE_OF_CONTENTS.md`

### Updating the Knowledge Base

When ADK releases new versions:

```bash
cd adk-expert

# Refresh repositories (if using setup scripts)
./scripts/refresh-repos.sh

# Generate change report
./scripts/generate-diff-report.sh

# Update documentation (manual)
# Edit files in knowledge-base/

# Validate changes
./scripts/validate-kb.sh
```

See `adk-expert/UPDATE_GUIDE.md` for detailed update instructions.

### ADK Expert Contents Summary

The adk-expert knowledge base includes:

**Official Examples (`repositories/adk-samples/python/agents/`):** ⭐ **START HERE**
- 28+ production Python agent implementations
- Notable examples:
  - `marketing-agency/` - Multi-agent marketing system (highly relevant to GTMForge!)
  - `blog-writer/` - Content generation with research
  - `academic-research/` - Research agent with citations
  - `RAG/` - Retrieval-augmented generation
  - `customer-service/` - Customer support automation
  - `podcast_transcript_agent/` - Multi-agent podcast system
  - Plus 22 more real-world examples

**API Documentation (`docs/`):** (Checked into git, ready to browse)
- `docs/main/` - Latest development API docs (Sphinx-generated)
- `docs/v1.17.0/` - Stable release API docs
- Complete reference for all ADK classes, methods, and parameters

**Documentation (`knowledge-base/`):**
- Core concepts (agents, tools, runtime, state)
- Testing strategies with pytest
- Best practices and design patterns
- Integration guides (Google services, LangChain, MCP)
- Advanced topics (streaming, grounding, deployment)

**Templates (`skill/adk-expert/assets/templates/`):**
- `agent_basic.py` - Simple LLM agent
- `agent_with_tools.py` - Agent with custom tools
- `multi_agent.py` - Multi-agent coordinator
- `callback_example.py` - Lifecycle callbacks
- `memory_example.py` - Long-term memory
- `test_template.py` - pytest test suite

**Quick References (`skill/adk-expert/references/`):**
- `quick-patterns.md` - Common code patterns
- `troubleshooting.md` - Error messages and solutions
- `api-quick-ref.md` - API parameters and methods

## Important Notes

- **Agent names** may be referenced in the frontend - coordinate changes between backend and frontend
- **Environment variables** in `.env` control API authentication (AI Studio vs Vertex AI)
- **Research iterations** in Deep Research agent default to 5, configurable via `ResearchConfiguration.max_search_iterations`
- **Grounding metadata** extraction requires Gemini models with grounding support
- **Citation tracking** in Deep Research agent uses custom callbacks to process grounding chunks
- **ADK version**: This project requires ADK >=1.17.0 (see `pyproject.toml`)

## GTMForge Agent Flow

Typical GTMForge workflow:

1. **Ideation Agent**: User provides startup idea → generates ICPs, pain points, market context
2. **Deep Research Agent**: Conducts autonomous web research on market, competitors, trends
3. **Comparative Insight Agent**: Analyzes competitive positioning
4. **Pitch Writer Agent**: Creates compelling narrative and pitch materials
5. **Prompt Forge Agent**: Optimizes prompts for asset generation
6. **Imagen/Veo Agents**: Generate visual and video assets
7. **Canva Agent**: Creates designed marketing materials
8. **QA Agent**: Reviews all content for quality and consistency
9. **Publisher Agent**: Distributes content across channels

Each agent can be invoked independently or as part of a coordinated workflow.

## Development Tips

### Documentation Maintenance

**CRITICAL: Always update documentation after major changes**

When making significant changes to the codebase, you MUST review and update relevant documentation:

1. **After adding new features or systems:**
   - Create or update documentation in `docs/`
   - Include usage examples, API reference, and best practices
   - Update this `AGENTS.md` file if architecture changes

2. **After modifying existing systems:**
   - Update relevant docs in `docs/` to reflect changes
   - Ensure examples remain accurate
   - Update any affected guides or tutorials

3. **Documentation checklist:**
   - [ ] Created/updated relevant documentation files
   - [ ] Included code examples demonstrating new features
   - [ ] Documented API/function signatures and parameters
   - [ ] Added best practices and common pitfalls
   - [ ] Updated architecture diagrams if applicable
   - [ ] Reviewed for clarity and completeness

4. **Where to document:**
   - **New systems/features**: Create new file in `docs/` (e.g., `docs/feature-name-guide.md`)
   - **Agent changes**: Update `AGENTS.md` agent descriptions
   - **API changes**: Update inline documentation and docstrings
   - **Architecture changes**: Update relevant sections in `AGENTS.md`
   - **Configuration changes**: Update `config.py` docstrings and `AGENTS.md`

**Example Documentation Files:**
- `docs/asset-saving-guide.md` - Comprehensive guide on asset management system
- `src/asset_server/README.md` - Asset server usage and API
- Agent-specific READMEs in agent directories

### Working with ADK
- **Start with official examples**: The `marketing-agency` example in `adk-expert/repositories/adk-samples/python/agents/` is particularly relevant to GTMForge
- Always consult `adk-expert/` knowledge base first (use Grep/Glob to search)
- Check templates in `adk-expert/skill/adk-expert/assets/templates/` for quick starts
- Browse API docs in `adk-expert/docs/v1.17.0/` for complete reference
- Review troubleshooting guide: `adk-expert/skill/adk-expert/references/troubleshooting.md`
- Use structured outputs (Pydantic models) for type safety
- Leverage callbacks for cross-agent state management
- Test agents in isolation before integrating into workflows

### State Management
- Use state prefixes for scoping: `app:`, `user:`, `temp:`
- Store cross-agent data in `callback_context.state`
- Persist important data in `session.state`
- Review `adk-expert/knowledge-base/core-concepts/05-sessions-state.md`

### Testing
- Write unit tests with mocked LLM responses
- Use pytest fixtures for agent setup
- Test with real API for integration tests
- See `adk-expert/knowledge-base/testing/README.md`

### Debugging
- Enable `--reload_agents` for hot-reloading during development
- Check ADK logs for event processing details
- Use `InvocationContext` to inspect agent state
- Review `adk-expert/knowledge-base/core-concepts/04-runtime.md`

---

*This file helps AI agents and developers understand and work effectively with the GTMForge codebase.*
