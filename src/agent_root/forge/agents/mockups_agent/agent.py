"""Mockups Agent

Skeleton implementation for iterative UI mockup generation.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from typing import Optional

from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions

from pydantic import BaseModel, Field

from forge.config import config
from forge.utils.callbacks import create_asset_save_callback


class MockupScreenTask(BaseModel):
    """Represents a single UI screen generation request."""

    name: str
    prompt: str


class MockupTasks(BaseModel):
    """Structured payload describing all mockup screens to generate."""

    tasks: list[MockupScreenTask] = Field(default_factory=list)


def append_mockup_to_state_callback(callback_context: CallbackContext) -> None:
    """Append the latest mockup output into session state.

    TODO: Extend to persist generated images via AssetService.
    """

    screen_markdown = callback_context.state.get("mockup_screen_markdown")
    if not screen_markdown:
        return

    current_task = callback_context.state.pop("current_mockup_task", None)

    completed = list(callback_context.state.get("completed_screens", []))
    if current_task and current_task.get("name"):
        completed.append(current_task["name"])
    callback_context.state["completed_screens"] = completed

    aggregated_brief = callback_context.state.get("mockups_brief")
    if aggregated_brief:
        aggregated_brief += "\n\n" + screen_markdown
    else:
        aggregated_brief = screen_markdown
    callback_context.state["mockups_brief"] = aggregated_brief

    logging.info(
        "[mockups_agent] Added screen to mockups brief. Completed screens: %s",
        completed,
    )


class MockupTaskLoader(BaseAgent):
    """Loads the next mockup task from pending queue into state."""

    def __init__(self) -> None:
        super().__init__(name="mockup_task_loader")

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        pending: list[dict] = list(state.get("mockup_pending_tasks", []))

        if not pending:
            logging.info("[mockups_agent] No pending mockup tasks detected.")
            yield Event(author=self.name)
            return

        current_task = pending.pop(0)
        state["mockup_pending_tasks"] = pending
        state["current_mockup_task"] = current_task
        state["current_mockup_prompt"] = current_task.get("prompt", "")

        logging.info(
            "[mockups_agent] Loaded mockup task '%s'. Remaining: %d",
            current_task.get("name", "Unnamed"),
            len(pending),
        )

        yield Event(author=self.name)


class MockupsLoopTerminator(BaseAgent):
    """Escalates to end the loop once all tasks are completed."""

    def __init__(self) -> None:
        super().__init__(name="mockups_loop_terminator")

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        state = ctx.session.state
        pending = state.get("mockup_pending_tasks", [])
        current = state.get("current_mockup_task")

        if pending or current:
            yield Event(author=self.name)
            return

        logging.info(
            "[mockups_agent] All mockup tasks completed. Escalating to stop loop."
        )
        yield Event(author=self.name, actions=EventActions(escalate=True))


mockups_generator_agent = LlmAgent(
    name="mockups_generator_agent",
    model=config.research_config.nano_banana_model,
    description="Generates UI mockup details and prompts for a single screen.",
    instruction="""
    You are a UI mockup generator. Given a screen specification from a PRD, produce:
    1. A concise description of the screen layout and interactions.
    2. A generation-ready image prompt suitable for rendering the UI.
    3. Any supplementary notes the design engineer should know.

    Context for the screen is stored under the state key `current_mockup_task`.
    Use the "name" and "prompt" fields to tailor your response.

    Return output as structured markdown with sections:
    # Screen
    ## Description
    ## Image Prompt
    ## Notes
    """,
    output_key="mockup_screen_markdown",
    after_agent_callback=append_mockup_to_state_callback,
)


def initialize_mockup_tasks_callback(callback_context: CallbackContext) -> None:
    """Seed loop state with tasks extracted from the PRD."""

    tasks_payload = callback_context.state.get("mockup_tasks")
    if not tasks_payload:
        logging.warning("[mockups_agent] No mockup tasks produced from PRD input.")
        return

    if isinstance(tasks_payload, MockupTasks):
        raw_tasks = [task.model_dump() for task in tasks_payload.tasks]
    else:
        raw_tasks = list(tasks_payload.get("tasks", []))

    callback_context.state["mockup_pending_tasks"] = raw_tasks
    callback_context.state.setdefault("completed_screens", [])
    callback_context.state.setdefault("mockups_brief", None)


mockups_task_generator = LlmAgent(
    name="mockups_task_generator",
    model=config.research_config.worker_model,
    description="Parses the PRD to enumerate screens requiring UI mockups.",
    instruction="""
    You are a product requirements analyst. Review the PRD provided in
    `prd_markdown` and extract a list of screens that require UI mockups.

    For each screen provide:
      * `name`: a short human readable label (e.g., "Checkout - Payment")
      * `prompt`: a detailed description and stylistic notes the mockup
        generator should follow when producing the image and layout summary.

    Return the list as structured JSON conforming to the provided schema.
    """,
    output_schema=MockupTasks,
    output_key="mockup_tasks",
)


mockups_loop_agent = LoopAgent(
    name="mockups_agent",
    description="Iterates through PRD-defined screens to generate UI mockups.",
    max_iterations=20,
    sub_agents=[
        MockupTaskLoader(),
        mockups_generator_agent,
        MockupsLoopTerminator(),
    ],
)


save_mockups_callback = create_asset_save_callback(
    state_key="mockups_brief",
    asset_type="mockups",
    filename="mockups_brief.md",
)


mockups_agent = SequentialAgent(
    name="mockups_agent",
    description="Generates mockup tasks from a PRD then iterates to produce UI mockups.",
    sub_agents=[
        mockups_task_generator,
        mockups_loop_agent,
    ],
    before_agent_callback=initialize_mockup_tasks_callback,
    after_agent_callback=save_mockups_callback,
)
