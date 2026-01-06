"""
Multi-Agent Epic and OKR Planning System

This package provides a Microsoft Swarm-based multi-agent system for strategic
planning of Epics and OKRs. It includes specialized agents for epic planning,
OKR creation, and coordination between agents.

Main Components:
- EpicPlanningAgent: Creates strategic epics from departmental goals
- OKRPlanningAgent: Generates measurable OKRs for epics
- AgentCoordinator: Orchestrates multi-agent workflows
- PlanningSession: High-level interface for planning sessions

Quick Start:
    from agents import PlanningSession, TimeFrame
    
    session = PlanningSession(api_key="your-openai-key")
    result = session.start(
        department_name="Engineering",
        strategic_goals=["Scale platform to 1M users", "Improve system reliability"],
        timeframe=TimeFrame.Q2
    )
    session.print_summary()
"""

from .models import (
    Department,
    Epic,
    Objective,
    KeyResult,
    PlanningContext,
    PlanningResult,
    Priority,
    TimeFrame
)

from .epic_agent import EpicPlanningAgent
from .okr_agent import OKRPlanningAgent
from .coordinator import AgentCoordinator, PlanningSession

__version__ = "1.0.0"

__all__ = [
    # Data Models
    "Department",
    "Epic",
    "Objective",
    "KeyResult",
    "PlanningContext",
    "PlanningResult",
    "Priority",
    "TimeFrame",
    
    # Agents
    "EpicPlanningAgent",
    "OKRPlanningAgent",
    
    # Coordination
    "AgentCoordinator",
    "PlanningSession",
]
