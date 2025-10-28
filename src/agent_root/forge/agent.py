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

import datetime
import logging
import re
from collections.abc import AsyncGenerator
from typing import Literal

from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.planners import BuiltInPlanner
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.genai import types as genai_types
from pydantic import BaseModel, Field
from .agents.deep_research import market_research_wrapper, express_market_research_wrapper
from .agents.ideation_agent import ideation_agent
from .config import config


workflow_root_agent=SequentialAgent(    
    name="workflow_root_agent",
    description="Executes the end-to-end workflow for building a startup.",
    sub_agents=[
        # market_research_wrapper,
        express_market_research_wrapper,
        ideation_agent,
    ],
)
    

root_agent = LlmAgent(
    name="forge",
    description="The main agent for GTM Forge.",
    model=config.research_config.worker_model,
    instruction=config.prompts_config.persona,
    sub_agents=[workflow_root_agent],
)
