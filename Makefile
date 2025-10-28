install:
	uv sync && npm --prefix src/frontend install

dev-backend:
	uv run adk web src/agent_root --port 8501 --allow_origins="*" --reload_agents

dev-frontend:
	npm --prefix src/frontend run dev

dev-asset-server:
	uv run python -m src.asset_server.server