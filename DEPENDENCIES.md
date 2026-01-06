# Module Dependencies Report

Generated: 2026-01-06 15:22

---

## Overview

- **Total Modules**: 8
- **Total Dependencies**: 0
- **External Packages**: 11

## Modules

### `agents.__init__`

**Path**: `agents\__init__.py`

**External Dependencies**: `coordinator`, `epic_agent`, `models`, `okr_agent`

---

### `agents.coordinator`

**Path**: `agents\coordinator.py`

**Classes**: `AgentCoordinator`, `PlanningSession`

**External Dependencies**: `datetime`, `epic_agent`, `json`, `models`, `okr_agent`, `typing`

---

### `agents.epic_agent`

**Path**: `agents\epic_agent.py`

**Classes**: `EpicPlanningAgent`

**External Dependencies**: `json`, `models`, `openai`, `typing`

---

### `agents.examples.__init__`

**Path**: `agents\examples\__init__.py`

---

### `agents.examples.advanced_usage`

**Path**: `agents\examples\advanced_usage.py`

**Functions**: `advanced_epic_planning_example`, `advanced_okr_planning_example`, `custom_coordination_example`, `main`

**External Dependencies**: `os`

---

### `agents.examples.planning_session_example`

**Path**: `agents\examples\planning_session_example.py`

**Classes**: `LLMConfig`

**Functions**: `main`

**External Dependencies**: `coordinator`, `models`, `os`

---

### `agents.models`

**Path**: `agents\models.py`

**Classes**: `Priority`, `TimeFrame`, `Department`, `KeyResult`, `Objective`, `Epic`, `PlanningContext`, `PlanningResult`

**External Dependencies**: `datetime`, `enum`, `pydantic`, `typing`

---

### `agents.okr_agent`

**Path**: `agents\okr_agent.py`

**Classes**: `OKRPlanningAgent`

**External Dependencies**: `json`, `models`, `openai`, `typing`

---

## Dependency Graph

```mermaid
graph TD
    classDef core fill:#4CAF50,stroke:#2E7D32,color:#fff
    classDef agent fill:#2196F3,stroke:#1565C0,color:#fff
    classDef example fill:#FF9800,stroke:#E65100,color:#fff
    classDef external fill:#9E9E9E,stroke:#424242,color:#fff
    M0["__init__"]:::agent
    M1["coordinator<br/><small>AgentCoordinator, PlanningSession</small>"]:::agent
    M2["epic_agent<br/><small>EpicPlanningAgent</small>"]:::agent
    M3["__init__"]:::agent
    M4["advanced_usage"]:::agent
    M5["planning_session_example<br/><small>LLMConfig</small>"]:::agent
    M6["models<br/><small>Priority, TimeFrame...</small>"]:::agent
    M7["okr_agent<br/><small>OKRPlanningAgent</small>"]:::agent
```



📂 Module Dependency Tree
================================================================================

agents.__init__

agents.coordinator

agents.epic_agent

agents.examples.__init__

agents.examples.advanced_usage

agents.examples.planning_session_example

agents.models

agents.okr_agent

