# 📚 Agent Examples Guide

This directory contains examples demonstrating how to use the Multi-Agent Epic & OKR Planning System.

## Examples

### 1. planning_session_example.py
**Complete planning session workflow**

Demonstrates:
- Initializing a planning session
- Generating epics and OKRs for a department
- Exporting results to JSON and Markdown
- Refining epics based on feedback
- Displaying detailed output

**Run:**
```bash
cd agents/examples
python planning_session_example.py
```

**Prerequisites:**
- OpenAI API key set as environment variable
- All dependencies installed

## Quick Usage Patterns

### Pattern 1: Simple Planning Session
```python
from agents import PlanningSession, TimeFrame

session = PlanningSession(api_key="your-key")
result = session.start(
    department_name="Marketing",
    strategic_goals=["Increase brand awareness", "Generate 10K leads"],
    timeframe=TimeFrame.Q3,
    num_epics=2
)
session.print_summary()
```

### Pattern 2: Custom Context Planning
```python
from agents import AgentCoordinator, PlanningContext, Department

coordinator = AgentCoordinator(api_key="your-key")

context = PlanningContext(
    department=Department(
        name="Sales",
        strategic_goals=["Close $5M in deals"],
        team_size=10
    ),
    timeframe=TimeFrame.H2,
    focus_areas=["Enterprise customers"],
    constraints=["Limited headcount"]
)

result = coordinator.execute_planning_session(context)
```

### Pattern 3: Individual Agent Usage
```python
from agents import EpicPlanningAgent, OKRPlanningAgent

# Epic planning
epic_agent = EpicPlanningAgent(api_key="your-key")
epics = epic_agent.plan_epics(context, num_epics=3)

# OKR planning
okr_agent = OKRPlanningAgent(api_key="your-key")
for epic in epics:
    objectives = okr_agent.generate_okrs_for_epic(epic, context)
    epic.objectives = objectives
```

### Pattern 4: Refinement Loop
```python
session = PlanningSession(api_key="your-key")
result = session.start(...)

# Review and refine
for epic in result.epics:
    feedback = input(f"Feedback for {epic.title}: ")
    if feedback:
        result = session.refine_epic(epic.id, feedback)
```

### Pattern 5: Validation and Quality Check
```python
from agents import OKRPlanningAgent

agent = OKRPlanningAgent(api_key="your-key")

for objective in objectives:
    validation = agent.validate_key_results(objective.key_results)
    if validation["score"] < 80:
        print(f"Quality issues in {objective.title}:")
        for issue in validation["issues"]:
            print(f"  - {issue}")
```

## Common Scenarios

### Scenario 1: Quarterly Planning
```python
# Planning for Q1 2026
result = session.start(
    department_name="Engineering",
    strategic_goals=["Launch v2.0", "Improve performance"],
    timeframe=TimeFrame.Q1,
    team_size=20,
    num_epics=3,
    num_objectives_per_epic=3
)
```

### Scenario 2: Half-Year Planning
```python
# Planning for H1 2026
result = session.start(
    department_name="Product",
    strategic_goals=["3 new features", "User retention +20%"],
    timeframe=TimeFrame.H1,
    num_epics=5,  # More epics for longer timeframe
    num_objectives_per_epic=4
)
```

### Scenario 3: Cross-Functional Planning
```python
# Align with company OKRs
result = session.start(
    department_name="Operations",
    strategic_goals=["Scale operations", "Reduce costs"],
    timeframe=TimeFrame.Q2,
    company_okrs=[
        "Achieve profitability",
        "Expand to 5 new markets"
    ]
)
```

## Output Examples

### Console Output
```
🚀 Starting planning session for Engineering
   Timeframe: Q2

📋 Step 1: Generating 3 epics...
   ✓ Generated 3 epics

🎯 Step 2: Prioritizing epics...

📊 Step 3: Generating OKRs for each epic...
   Processing Epic 1/3: Platform Scalability Initiative
   ✓ Added 3 objectives with 9 key results
```

### JSON Export Structure
```json
{
  "epics": [
    {
      "id": "epic-001",
      "title": "Platform Scalability Initiative",
      "objectives": [
        {
          "id": "obj-001",
          "title": "Improve System Performance",
          "key_results": [...]
        }
      ]
    }
  ],
  "context": {...},
  "created_at": "2026-01-06T10:30:00"
}
```

### Markdown Export Preview
```markdown
# Planning Results - Engineering

## Epic 1: Platform Scalability Initiative
**Priority:** HIGH

### Objectives
**Improve System Performance**
- Progress: 0.0%
- Priority: high

Key Results:
- Reduce API response time: 0/100 ms (0.0%)
- Increase throughput: 0/10000 requests/sec (0.0%)
```

## Tips & Best Practices

### 1. API Key Management
```python
import os
api_key = os.getenv("OPENAI_API_KEY")
session = PlanningSession(api_key=api_key)
```

### 2. Error Handling
```python
try:
    result = session.start(...)
except Exception as e:
    print(f"Planning failed: {e}")
    # Handle error or retry
```

### 3. Iterative Refinement
```python
# Generate initial plan
result = session.start(...)

# Review and refine multiple times
for epic in result.epics:
    if epic.overall_progress < expected_threshold:
        result = session.refine_epic(epic.id, "Needs more detail")
```

### 4. Export Best Practices
```python
# Export with timestamps
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
session.export(f"planning_{timestamp}.json", format="json")
session.export(f"planning_{timestamp}.md", format="markdown")
```

### 5. Progress Tracking Integration
```python
from okr_tracker import OKRTracker

# Convert planning result to trackable OKRs
for epic in result.epics:
    for objective in epic.objectives:
        tracker = OKRTracker.from_objective(objective)
        # Add to tracking system
```

## Environment Setup

### Required Environment Variables
```bash
# OpenAI API Key (required)
export OPENAI_API_KEY="sk-..."

# Optional: Model selection
export OPENAI_MODEL="gpt-4o"

# Optional: Temperature
export OPENAI_TEMPERATURE="0.7"
```

### Python Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Troubleshooting

### Issue: "No module named 'agents'"
**Solution:**
```bash
# Run from project root
cd pilot-okr
python -m agents.examples.planning_session_example
```

### Issue: "OpenAI API key not set"
**Solution:**
```bash
export OPENAI_API_KEY="your-key"
# or set in Python
session = PlanningSession(api_key="your-key")
```

### Issue: "Rate limit exceeded"
**Solution:**
- Reduce num_epics or num_objectives_per_epic
- Add delays between API calls
- Upgrade OpenAI plan

### Issue: "Low quality OKRs"
**Solution:**
- Enable auto_refine=True
- Provide more detailed strategic goals
- Add specific focus_areas and constraints
- Review and manually refine using refine_epic()

## Next Steps

1. **Run the example:** `python planning_session_example.py`
2. **Modify for your use case:** Edit strategic goals and context
3. **Integrate with existing systems:** Export and import into your tools
4. **Build on top:** Create custom workflows using the agents

## Additional Resources

- Main README: [../README.md](../README.md)
- API Documentation: See module docstrings
- Data Models: [../models.py](../models.py)
- Agent Implementations: [../epic_agent.py](../epic_agent.py), [../okr_agent.py](../okr_agent.py)

---

**Happy Planning! 🎯**
