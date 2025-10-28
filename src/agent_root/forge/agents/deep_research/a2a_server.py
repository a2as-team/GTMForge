#!/usr/bin/env python3
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
A2A Server for DEEP-RESEARCH-CORE Agent

This script exposes the deep research agent via the Agent-to-Agent (A2A) protocol,
allowing other agents to query it remotely.

Usage:
    uvicorn forge.agents.deep_research.a2a_server:a2a_app --host localhost --port 8002 --reload

The agent will be available at:
    - Agent Card: http://localhost:8002/.well-known/agent-card.json
    - A2A Endpoint: http://localhost:8002/

This agent can be consumed by other agents using:
    from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
    
    research_agent = RemoteA2aAgent(
        name="deep_research_core",
        description="Backend-grade analysis agent for startup concepts and market research",
        agent_card=f"http://localhost:8002{AGENT_CARD_WELL_KNOWN_PATH}"
    )
"""

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from forge.agents.deep_research.agent import market_research_agent

# Create A2A-compatible app
# This automatically generates an agent card and exposes the agent via A2A protocol
a2a_app = to_a2a(
    market_research_agent,
    port=8502  # Different from default ADK web server (8000) and other A2A servers
)

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 80)
    print("DEEP-RESEARCH-CORE A2A Server")
    print("=" * 80)
    print("\nStarting A2A server for deep research agent...")
    print("\nEndpoints:")
    print("  - Agent Card: http://localhost:8502/.well-known/agent-card.json")
    print("  - A2A API: http://localhost:8502/")
    print("\nPress CTRL+C to stop the server")
    print("=" * 80)
    print()
    
    uvicorn.run(
        "forge.agents.deep_research.a2a_server:a2a_app",
        host="localhost",
        port=8502,
        reload=True
    )

