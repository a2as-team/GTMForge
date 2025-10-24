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

import os
from pathlib import Path

import google.auth
from pydantic import BaseModel, Field, model_validator

# To use AI Studio credentials:
# 1. Create a .env file in the /app directory with:
#    GOOGLE_GENAI_USE_VERTEXAI=FALSE
#    GOOGLE_API_KEY=PASTE_YOUR_ACTUAL_API_KEY_HERE
# 2. This will override the default Vertex AI configuration
# _, project_id = google.auth.default()
# if project_id:
#     os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
# os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
# os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


class ResearchConfiguration(BaseModel):
    """Configuration for research-related models and parameters.

    Attributes:
        critic_model (str): Model for evaluation tasks.
        worker_model (str): Model for working/generation tasks.
        max_search_iterations (int): Maximum search iterations allowed.
    """

    critic_model: str = "gemini-2.5-pro"
    worker_model: str = "gemini-2.5-flash"
    max_search_iterations: int = 5


class PromptsConfiguration(BaseModel):
    """Configuration for prompt templates loaded from files.

    Attributes:
        persona (str): Content of the persona.md prompt file.
        extras (dict[str, str]): Additional .md files not recognized as well-known.
            Key is filename, value is file content.
    """

    persona: str
    extras: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def load_prompts_from_disk(cls, data: dict) -> dict:
        """Load prompt files from the prompts directory."""
        # Get prompts path from environment or use default
        prompts_path = os.environ.get("FORGE_PROMPTS_PATH", "./prompts/forge")
        prompts_dir = Path(prompts_path)

        if not prompts_dir.exists():
            raise ValueError(f"Prompts directory not found: {prompts_dir}")

        if not prompts_dir.is_dir():
            raise ValueError(f"Prompts path is not a directory: {prompts_dir}")

        # Well-known prompt files
        well_known = {"persona.md"}

        # Load well-known prompts
        persona_path = prompts_dir / "persona.md"
        if not persona_path.exists():
            raise ValueError(f"Required prompt file not found: {persona_path}")

        data["persona"] = persona_path.read_text(encoding="utf-8")

        # Load extras (all other .md files)
        extras = {}
        for md_file in prompts_dir.glob("*.md"):
            if md_file.name not in well_known:
                extras[md_file.name] = md_file.read_text(encoding="utf-8")

        data["extras"] = extras

        return data


class Configuration(BaseModel):
    """Main configuration object for Forge.

    Attributes:
        research_config (ResearchConfiguration): Research-related configuration.
        prompts_config (PromptsConfiguration): Prompts and templates configuration.
    """

    research_config: ResearchConfiguration = Field(
        default_factory=ResearchConfiguration
    )
    prompts_config: PromptsConfiguration = Field(default_factory=PromptsConfiguration)


config = Configuration()
