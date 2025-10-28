from forge.agents.deep_research.agent import (
    market_research_wrapper,
    market_research_agent,
    express_market_research_wrapper,
)

root_agent = market_research_wrapper

__all__ = [
    "root_agent",
    "market_research_wrapper",
    "market_research_agent",
    "express_market_research_wrapper",
]
