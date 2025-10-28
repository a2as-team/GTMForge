.PHONY: help install setup setup-adk-expert dev-backend dev-frontend dev-asset-server

help:  ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install Python and frontend dependencies
	uv sync && npm --prefix src/frontend install

setup:  ## Complete project setup (install dependencies + setup ADK Expert)
	@echo "Running complete project setup..."
	$(MAKE) install
	$(MAKE) setup-adk-expert
	@echo "✅ Setup complete! Run 'make dev-backend' and 'make dev-frontend' to start development."

setup-adk-expert:  ## Setup ADK Expert knowledge base (clones repos, generates docs, builds search index)
	@echo "Setting up ADK Expert knowledge base..."
	@if [ -d "adk-expert" ]; then \
		cd adk-expert && ./scripts/setup.sh; \
	else \
		echo "Error: adk-expert directory not found"; \
		exit 1; \
	fi

dev-backend:  ## Run ADK web server with hot reload (port 8501)
	uv run adk web src/agent_root --port 8501 --allow_origins="*" --reload_agents

dev-frontend:  ## Run frontend development server (port 5173)
	npm --prefix src/frontend run dev

dev-asset-server:  ## Run asset server for generated files (port 8550)
	uv run uvicorn src.asset_server.server:app --reload --reload-dir src/asset_server --host 0.0.0.0 --port 8550