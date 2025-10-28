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
A2A Client Example for DEEP-RESEARCH-CORE Agent

This script demonstrates how to connect to the DEEP-RESEARCH-CORE agent
exposed via A2A protocol and send queries to it.

Prerequisites:
    1. Start the A2A server first:
       uvicorn forge.agents.deep_research.a2a_server:a2a_app --host localhost --port 8002

Usage:
    python -m forge.agents.deep_research.a2a_client_example
"""

import asyncio

from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.runners import Runner
from google.genai import types


async def main():
    """Demonstrate A2A client connecting to DEEP-RESEARCH-CORE agent."""
    
    print("=" * 80)
    print("DEEP-RESEARCH-CORE A2A Client Example")
    print("=" * 80)
    print()
    
    # Create a RemoteA2aAgent that connects to the A2A server
    deep_research_agent = RemoteA2aAgent(
        name="deep_research_core",
        description=(
            "Backend-grade analysis agent for startup concepts, product ideas, "
            "markets, and problem statements. Returns structured DEEP-RESEARCH-CORE analysis."
        ),
        agent_card=f"http://localhost:8502{AGENT_CARD_WELL_KNOWN_PATH}"
    )
    
    # Create a runner to execute the agent
    runner = Runner(
        app_name="deep_research_client",
        agent=deep_research_agent
    )
    
    # Example startup idea to analyze
    startup_idea = """
    A B2B SaaS platform that uses AI to automatically generate and maintain 
    software documentation by analyzing code repositories, pull requests, and 
    team communications. The platform integrates with GitHub, GitLab, and Slack 
    to keep documentation always up-to-date without manual intervention.
    """
    
    print("Sending startup idea for analysis...")
    print(f"\nStartup Idea:\n{startup_idea}\n")
    print("-" * 80)
    print("\nWaiting for DEEP-RESEARCH-CORE analysis...\n")
    
    # Run the agent asynchronously
    try:
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session",
            new_message=types.Content(parts=[types.Part.from_text(startup_idea)])
        ):
            # Print agent responses
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"[{event.author}] {part.text}")
            
            # Check if this is the final response
            if event.is_final_response():
                print("\n" + "=" * 80)
                print("Analysis Complete!")
                print("=" * 80)
                break
                
    except Exception as e:
        print(f"\n❌ Error connecting to A2A server: {e}")
        print("\nMake sure the A2A server is running:")
        print("  uvicorn forge.agents.deep_research.a2a_server:a2a_app --host localhost --port 8502")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

