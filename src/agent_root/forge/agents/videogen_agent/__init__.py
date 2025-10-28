"""Video Generation Agent

Generates promo video by creating individual scenes from company brief
and splicing them together using moviepy.
"""

from .agent import videogen_agent

__all__ = ["videogen_agent"]
