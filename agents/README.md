# Multi-Agent Epic & OKR Planning System

A Microsoft Swarm-based multi-agent system for strategic planning of Epics and OKRs. This system uses specialized AI agents to break down departmental strategic goals into actionable epics and measurable objectives with key results.

## 🎯 Features

- **🤖 Multi-Agent Architecture**: Specialized agents for Epic planning and OKR creation
- **📋 Epic Planning Agent**: Breaks down strategic goals into actionable epics with clear business value
- **📊 OKR Planning Agent**: Generates measurable Objectives and Key Results aligned with epics
- **🔄 Agent Coordination**: Intelligent handoffs and context sharing between agents
- **✅ Auto-Validation**: Automatic validation and refinement of OKRs
- **📈 Progress Tracking**: Built-in progress calculation for Key Results and Objectives
- **💾 Export Options**: Export to JSON or Markdown formats
- **🎨 Rich CLI Output**: Colored, formatted output with progress indicators

## 🏗️ Architecture

```
agents/
├── models.py          # Pydantic data models (Department, Epic, Objective, KeyResult)
├── epic_agent.py      # Epic Planning Agent
├── okr_agent.py       # OKR Planning Agent
├── coordinator.py     # Agent Coordinator & Planning Session
├── __init__.py        # Package exports
└── examples/          # Usage examples
    └── planning_session_example.py
```

## 📦 Installation

### Prerequisites

- Python 3.8+
- OpenAI API key

### Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set OpenAI API key:**
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

## 🚀 Quick Start

### Simple Planning Session

```python
from agents import PlanningSession, TimeFrame

# Initialize session
session = PlanningSession(api_key="your-openai-key")

# Start planning
result = session.start(
    department_name="Engineering",
    strategic_goals=[
        "Scale platform to 1M users",
        "Improve system reliability to 99.99%",
        "Reduce technical debt by 30%"
    ],
    timeframe=TimeFrame.Q2,
    team_size=25,
    num_epics=3,
    num_objectives_per_epic=3
)

# Print summary
session.print_summary()

# Export results
session.export("planning_result.json", format="json")
session.export("planning_result.md", format="markdown")
```

### Advanced Usage with Coordinator

```python
from agents import AgentCoordinator, PlanningContext, Department, TimeFrame

# Setup coordinator
coordinator = AgentCoordinator(api_key="your-openai-key")

# Build context
department = Department(
    name="Product",
    strategic_goals=[
        "Launch 3 new features",
        "Increase user engagement by 40%"
    ],
    team_size=15
)

context = PlanningContext(
    department=department,
    timeframe=TimeFrame.Q3,
    focus_areas=["User Experience", "Feature Adoption"],
    company_okrs=["Achieve $5M ARR", "Reach 50K users"]
)

# Execute planning
result = coordinator.execute_planning_session(
    context=context,
    num_epics=3,
    num_objectives_per_epic=3
)

# Refine an epic
result = coordinator.refine_with_feedback(
    result=result,
    epic_id="epic-001",
    feedback="Add more focus on mobile experience"
)
```

## 📚 Core Components

### 1. Data Models

**Department**: Represents a team or department
```python
department = Department(
    name="Engineering",
    strategic_goals=["Goal 1", "Goal 2"],
    team_size=20,
    budget=500000.0
)
```

**Epic**: Large body of work
```python
epic = Epic(
    id="epic-001",
    title="Platform Scalability Initiative",
    description="Scale infrastructure to support 1M users",
    business_value="Enable 10x user growth without proportional cost increase",
    priority=Priority.HIGH
)
```

**Objective**: Qualitative goal with measurable Key Results
```python
objective = Objective(
    id="obj-001",
    title="Improve System Performance",
    description="Optimize critical paths for better user experience",
    priority=Priority.HIGH
)
```

**KeyResult**: Measurable outcome
```python
key_result = KeyResult(
    id="kr-001",
    description="Reduce API response time",
    metric="Average response time",
    baseline=500.0,
    target=100.0,
    unit="ms"
)
```

### 2. Agents

#### Epic Planning Agent
Specializes in breaking down strategic goals into actionable epics.

```python
from agents import EpicPlanningAgent

agent = EpicPlanningAgent(api_key="your-key")
epics = agent.plan_epics(context, num_epics=3)
```

**Capabilities:**
- Generate epics from strategic goals
- Prioritize epics based on impact
- Analyze dependencies
- Suggest optimal execution order
- Refine epics based on feedback

#### OKR Planning Agent
Specializes in creating measurable OKRs for epics.

```python
from agents import OKRPlanningAgent

agent = OKRPlanningAgent(api_key="your-key")
objectives = agent.generate_okrs_for_epic(epic, context, num_objectives=3)
```

**Capabilities:**
- Generate SMART objectives
- Create measurable key results
- Validate OKR quality
- Suggest appropriate metrics
- Calculate objective health

### 3. Coordination Layer

**AgentCoordinator**: Orchestrates multi-agent workflows
```python
coordinator = AgentCoordinator(api_key="your-key")
result = coordinator.execute_planning_session(context)
```

**PlanningSession**: High-level interface
```python
session = PlanningSession(api_key="your-key")
result = session.start(department_name="Engineering", ...)
```

## 🎓 Examples

### Run the Complete Example

```bash
python agents/examples/planning_session_example.py
```

This example demonstrates:
- Creating a planning session
- Generating epics and OKRs
- Exporting results
- Refining epics with feedback
- Detailed output formatting

### Example Output

```
🚀 Starting planning session for Engineering
   Timeframe: Q2

📋 Step 1: Generating 3 epics...
   ✓ Generated 3 epics

🎯 Step 2: Prioritizing epics...

📊 Step 3: Generating OKRs for each epic...
   Processing Epic 1/3: Platform Scalability Initiative
   ✓ Added 3 objectives with 9 key results

✅ Planning session complete!
   Total: 3 epics, 9 objectives, 27 key results
```

## 📊 Output Formats

### JSON Export
Complete structured data with all fields:
```json
{
  "epics": [...],
  "context": {...},
  "created_at": "2026-01-06T10:30:00",
  "agent_metadata": {...}
}
```

### Markdown Export
Human-readable report format:
```markdown
# Planning Results - Engineering

**Timeframe:** Q2

## Strategic Goals
- Scale platform to 1M users
- Improve system reliability

## Epics

### Platform Scalability Initiative
**Priority:** HIGH
...
```

## 🔧 Configuration

### Model Selection
```python
session = PlanningSession(
    api_key="your-key",
    model="gpt-4o"  # or "gpt-4-turbo", "gpt-3.5-turbo"
)
```

### Temperature Control
```python
coordinator = AgentCoordinator(
    api_key="your-key",
    temperature=0.7  # 0.0-1.0, higher = more creative
)
```

### Auto-Refinement
```python
result = coordinator.execute_planning_session(
    context=context,
    auto_refine=True  # Automatically refine low-quality OKRs
)
```

## 🎯 Best Practices

### Strategic Goals
- Keep goals clear and concise
- Focus on outcomes, not activities
- Align with company-wide objectives
- Consider team capacity and constraints

### Epic Planning
- 3-5 epics per planning session
- Each epic should be 1-6 months scope
- Clear business value statement required
- Identify dependencies early

### OKR Creation
- 2-5 key results per objective
- Use concrete, measurable metrics
- Set ambitious but achievable targets
- Ensure alignment across levels

## 📈 Progress Tracking

Key Results automatically calculate progress:
```python
kr = KeyResult(
    baseline=100.0,
    target=500.0,
    current=300.0,
    unit="users"
)
print(kr.progress_percentage)  # 50.0%
```

Objectives aggregate KR progress:
```python
objective = Objective(...)
print(objective.overall_progress)  # Average of all KRs
```

Epics aggregate objective progress:
```python
epic = Epic(...)
print(epic.overall_progress)  # Average of all objectives
```

## 🔍 Validation

The OKR Agent includes automatic validation:

```python
validation = okr_agent.validate_key_results(key_results)
# Returns:
# {
#     "valid": True/False,
#     "score": 0-100,
#     "issues": [...],
#     "suggestions": [...]
# }
```

## 🤝 Integration

### With Existing OKR System
```python
# Import current OKRs
from okr_tracker import OKRTracker

tracker = OKRTracker.from_json("current_okrs.json")

# Generate new epics
session = PlanningSession()
result = session.start(...)

# Merge with existing
for epic in result.epics:
    for objective in epic.objectives:
        okr = OKRTracker.from_objective(objective)
        tracker.add_okr(okr)
```

### With Project Management Tools
```python
# Export for import into Jira, Azure DevOps, etc.
session.export("epics_for_jira.json", format="json")
```

## 🧪 Testing

Run tests (if available):
```bash
pytest tests/
```

## 📝 License

This project is part of the OKR Pilot system.

## 🆘 Troubleshooting

### "OpenAI API key not set"
```bash
export OPENAI_API_KEY="your-key"
```

### "No module named 'agents'"
```bash
# Make sure you're in the project directory
cd pilot-okr
python -m agents.examples.planning_session_example
```

### "Rate limit exceeded"
- Use a lower value for `num_epics` or `num_objectives_per_epic`
- Add delays between API calls
- Upgrade your OpenAI plan

## 🔮 Future Enhancements

- [ ] Support for more LLM providers (Anthropic, Azure OpenAI)
- [ ] Interactive CLI with prompts
- [ ] Web UI for planning sessions
- [ ] Integration with popular project management tools
- [ ] Historical analysis and trend tracking
- [ ] Team collaboration features

## 📧 Support

For issues or questions, please refer to the main project documentation.

---

**Version:** 1.0.0  
**Last Updated:** January 2026
