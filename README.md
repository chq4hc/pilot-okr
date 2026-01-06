# OKR Pilot - Complete OKR Management System

A professional-grade toolkit for planning, evaluating, tracking, and improving OKRs (Objectives and Key Results) with AI-powered multi-agent support.

## 🌟 Features

### Core Capabilities
- **🤖 AI-Powered Planning**: Multi-agent system for Epic and OKR generation
- **📊 Rule-Based Scoring**: Automated evaluation based on OKR best practices
- **🧠 AI-Powered Analysis**: LLM-driven critique and improvement suggestions
- **📈 Progress Tracking**: Real-time OKR and Key Result tracking with auto-updates
- **✅ Comprehensive Validation**: Structure and content validation
- **📄 Rich Reporting**: Markdown and JSON output formats
- **💾 File I/O**: Load and save OKRs in JSON format
- **🔄 Revision Suggestions**: Automated OKR improvement recommendations

### Multi-Agent Planning System (NEW!)
- **Epic Planning Agent**: Breaks down strategic goals into actionable epics
- **OKR Planning Agent**: Generates measurable objectives and key results
- **Agent Coordinator**: Orchestrates multi-agent workflows with intelligent handoffs
- **Auto-Refinement**: Validates and refines OKRs for quality

## Installation

```bash
# Install core dependencies
pip install -r requirements.txt

# Required packages
pip install openai pydantic

# Optional: For Jupyter notebooks
pip install jupyter ipykernel
```

## 🚀 Quick Start

### Option 1: AI-Powered Planning Session

```python
from agents import PlanningSession, TimeFrame

# Initialize AI planning session
session = PlanningSession(api_key="your-openai-key")

# Generate epics and OKRs for your department
result = session.start(
    department_name="Engineering",
    strategic_goals=[
        "Scale platform to 1M users",
        "Improve system reliability to 99.99%"
    ],
    timeframe=TimeFrame.Q2,
    team_size=25,
    num_epics=3,
    num_objectives_per_epic=3
)

# View results
session.print_summary()
session.export("planning_result.json", format="json")
```

### Option 2: Manual OKR Evaluation

```python
from okr_evaluator import OKREvaluatorService

# Initialize the service
service = OKREvaluatorService()

# Your OKR data
okr = {
    "objective": "Increase customer satisfaction",
    "key_results": [
        {
            "text": "Improve NPS score",
            "baseline": "Current NPS: 45",
            "target": "Target NPS: 70",
            "deadline": "Q2 2026"
        }
    ]
}

# Evaluate
rule_result, llm_result = service.evaluate_okr(okr)

print(f"Score: {rule_result.numeric_score}/4")
print(f"Quality: {llm_result.quality_label}")
```

## Module Structure

```
okr-pilot/
├── agents/                    # 🤖 Multi-Agent Planning System (NEW!)
│   ├── __init__.py           # Package exports
│   ├── models.py             # Data models (Epic, Objective, KeyResult)
│   ├── epic_agent.py         # Epic Planning Agent
│   ├── okr_agent.py          # OKR Planning Agent
│   ├── coordinator.py        # Agent coordination & workflows
│   ├── README.md             # Agents documentation
│   └── examples/             # Usage examples
│       ├── planning_session_example.py
│       └── README.md
├── okr_evaluator.py          # Core evaluation engine
├── okr_utils.py              # Utilities (I/O, formatting, validation)
├── okr_tracker.py            # Progress tracking and monitoring
├── __init__.py               # Package initialization
├── okr-pilot.ipynb           # Jupyter notebook examples
├── README.md                 # This file
└── requirements.txt          # Dependencies
```

## Components

### 🤖 Multi-Agent Planning System

**PlanningSession**: High-level interface for AI-powered planning
```python
from agents import PlanningSession, TimeFrame

session = PlanningSession(api_key="your-key")
result = session.start(
    department_name="Product",
    strategic_goals=["Launch 3 new features", "Increase engagement by 40%"],
    timeframe=TimeFrame.Q3
)
```

**EpicPlanningAgent**: Creates strategic epics from departmental goals
```python
from agents import EpicPlanningAgent

agent = EpicPlanningAgent(api_key="your-key")
epics = agent.plan_epics(context, num_epics=3)
prioritized = agent.suggest_prioritization(epics, context)
```

**OKRPlanningAgent**: Generates measurable OKRs for epics
```python
from agents import OKRPlanningAgent

agent = OKRPlanningAgent(api_key="your-key")
objectives = agent.generate_okrs_for_epic(epic, context)
validation = agent.validate_key_results(objectives[0].key_results)
```

**AgentCoordinator**: Orchestrates multi-agent workflows
```python
from agents import AgentCoordinator

coordinator = AgentCoordinator(api_key="your-key")
result = coordinator.execute_planning_session(
    context=planning_context,
    num_epics=3,
    auto_refine=True
)
```

See [agents/README.md](agents/README.md) for complete documentation.

### 📊 OKR Evaluation System

**OKREvaluatorService**: Main evaluation service

Main service class that combines rule-based and LLM evaluation:

```python
service = OKREvaluatorService()

# Complete evaluation
rule_result, llm_result = service.evaluate_okr(okr_data)

# Evaluation with revision
rule_result, llm_result, revised_okr = service.evaluate_and_revise(okr_data)
```

### OKRRuleEngine

Rule-based scoring (0-4 points):
- KR count optimization (3-5 is optimal)
- Format completeness (baseline, target, deadline)

```python
from okr_evaluator import OKRRuleEngine

result = OKRRuleEngine.calculate_score(okr_data)
print(f"Score: {result.numeric_score}/4")
```

### OKRLLMEvaluator

AI-powered evaluation using LLM:

```python
from okr_evaluator import OKRLLMEvaluator, LLMConfig

config = LLMConfig(
    api_key="your-api-key",
    base_url="your-endpoint",
    model="your-model"
)

evaluator = OKRLLMEvaluator(config)
evaluation = evaluator.evaluate(okr_data, rule_score=3)
```

### Utility Classes

**OKRFileHandler**: Load and save OKRs
```python
from okr_utils import OKRFileHandler

okr = OKRFileHandler.load_okr("my_okr.json")
OKRFileHandler.save_okr(okr, "output.json")
```

**OKRFormatter**: Format for display
```python
from okr_utils import OKRFormatter

markdown = OKRFormatter.format_okr_markdown(okr_data)
report = OKRFormatter.format_evaluation_markdown(evaluation)
```

**OKRValidator**: Validate structure
```python
from okr_utils import OKRValidator

is_valid, issues = OKRValidator.validate_okr(okr_data, strict=True)
if not is_valid:
    print("Issues:", issues)
```

**OKRReporter**: Generate reports
```python
from okr_utils import OKRReporter

report = OKRReporter.generate_evaluation_report(
    okr_data,
    rule_result,
    llm_result,
    output_path="report.md"
)
```

### 📈 OKR Tracking System

**OKRTracker**: Track OKR progress with auto-updates
```python
from okr_tracker import OKRTracker, KeyResultTracker

# Create tracker
okr = OKRTracker(
    id="okr-001",
    title="Improve System Performance",
    owner="Engineering Team"
)

# Add key results
kr = KeyResultTracker(
    id="kr-001",
    description="Reduce API latency",
    baseline=500.0,
    target=100.0,
    current=500.0,
    unit="ms",
    parent_okr=okr  # Auto-updates parent on progress change
)

# Update progress
kr.update_progress(300.0)  # Automatically updates OKR progress
print(f"OKR Progress: {okr.progress:.1f}%")
```

**Alert System**: 5 alert types with severity ranking
- 🔴 At Risk: Progress < 30%
- 🟡 Behind: Progress 30-60%
- 🟢 On Track: Progress 60-100%
- ⚠️ Stalled: No progress in recent period
- 🎯 Complete: Target achieved

## Evaluation Criteria

### Rule-Based (0-4 points)

1. **KR Count** (0-2 points)
   - 3-5 KRs: 2 points (optimal)
   - Other counts: 1 point
   - No KRs: 0 points

2. **KR Format** (0-2 points)
   - All KRs complete: 2 points
   - Some KRs complete: 1 point
   - No complete KRs: 0 points

### LLM Assessment (0-6 points)

1. **Objective Clarity**: Outcome-focused vs activity-focused
2. **Leading/Lagging Balance**: Mix of predictive and outcome metrics
3. **Ambition vs Attainability**: Challenging but achievable
4. **Dependency Clarity**: Clear ownership and dependencies

**Total Score**: 0-10 (Rule-based + LLM)

### Quality Labels

- **High** (8-10): Well-structured, clear, measurable
- **Neutral** (5-7): Acceptable, needs improvement
- **Low** (0-4): Significant issues, requires major revision

## Configuration

Create a custom LLM configuration:

```python
from okr_evaluator import LLMConfig

config = LLMConfig(
    api_key="your-api-key",
    base_url="https://your-endpoint.com",
    model="gpt-4",
    temperature=0.7,
    max_tokens=2000
)

service = OKREvaluatorService(llm_config=config)
```

## Complete Workflow Example

### End-to-End: Planning → Evaluation → Tracking

```python
# Step 1: AI-Powered Planning
from agents import PlanningSession, TimeFrame

session = PlanningSession(api_key="your-key")
result = session.start(
    department_name="Engineering",
    strategic_goals=["Scale to 1M users", "99.99% uptime"],
    timeframe=TimeFrame.Q2,
    num_epics=2
)

# Step 2: Evaluate Generated OKRs
from okr_evaluator import OKREvaluatorService

service = OKREvaluatorService()
for epic in result.epics:
    for objective in epic.objectives:
        okr_data = {
            "objective": objective.title,
            "key_results": [
                {
                    "text": kr.description,
                    "baseline": f"{kr.baseline} {kr.unit}",
                    "target": f"{kr.target} {kr.unit}",
                    "deadline": kr.due_date or "Q2 2026"
                }
                for kr in objective.key_results
            ]
        }
        rule_result, llm_result = service.evaluate_okr(okr_data)
        print(f"Score: {rule_result.numeric_score}/4 - {llm_result.quality_label}")

# Step 3: Track Progress
from okr_tracker import OKRTracker, KeyResultTracker

for epic in result.epics:
    for objective in epic.objectives:
        tracker = OKRTracker(
            id=objective.id,
            title=objective.title,
            owner=objective.owner or "TBD"
        )
        
        for kr in objective.key_results:
            kr_tracker = KeyResultTracker(
                id=kr.id,
                description=kr.description,
                baseline=kr.baseline,
                target=kr.target,
                current=kr.current,
                unit=kr.unit,
                parent_okr=tracker
            )
        
        # Monitor progress
        print(f"{tracker.title}: {tracker.progress:.1f}%")
        alerts = tracker.get_alerts()
        for alert in alerts:
            print(f"  {alert['severity']}: {alert['message']}")

# Step 4: Export Everything
session.export("planning_result.json", format="json")
session.export("planning_result.md", format="markdown")
```

## Examples

### Load, Evaluate, and Generate Report

```python
from okr_evaluator import OKREvaluatorService
from okr_utils import load_okr_from_json, OKRReporter

# Load OKR
okr = load_okr_from_json("my_okr.json")

# Evaluate
service = OKREvaluatorService()
rule_result, llm_result = service.evaluate_okr(okr)

# Generate report
report = OKRReporter.generate_evaluation_report(
    okr,
    rule_result.__dict__,
    llm_result.dict() if llm_result else None,
    output_path="evaluation_report.md"
)

print(report)
```

### Batch Evaluation

```python
from okr_utils import OKRFileHandler

# Load multiple OKRs
okrs = OKRFileHandler.load_multiple_okrs("okrs.json")

# Evaluate each
service = OKREvaluatorService()
results = []

for okr in okrs:
    rule_result, llm_result = service.evaluate_okr(okr)
    results.append({
        "objective": okr["objective"],
        "score": rule_result.numeric_score,
        "quality": llm_result.quality_label if llm_result else "N/A"
    })

# Print summary
for r in results:
    print(f"{r['objective']}: {r['score']}/4 ({r['quality']})")
```

## 📚 Documentation

- **Main README**: [README.md](README.md) (this file)
- **Agents Package**: [agents/README.md](agents/README.md) - Multi-agent planning system
- **Agent Examples**: [agents/examples/README.md](agents/examples/README.md) - Usage patterns
- **Jupyter Notebook**: [okr-pilot.ipynb](okr-pilot.ipynb) - Interactive examples

## 🎯 Use Cases

### 1. Strategic Planning
Use the multi-agent system to generate epics and OKRs aligned with company goals:
```bash
python agents/examples/planning_session_example.py
```

### 2. OKR Quality Assessment
Evaluate existing OKRs for quality and get improvement suggestions:
```python
service = OKREvaluatorService()
rule_result, llm_result = service.evaluate_okr(okr_data)
```

### 3. Progress Monitoring
Track OKR progress with automatic alerts:
```python
tracker = OKRTracker.from_json("okr.json")
tracker.update_progress(new_value)
alerts = tracker.get_alerts()
```

### 4. Batch Processing
Evaluate multiple OKRs and generate reports:
```python
okrs = OKRFileHandler.load_multiple_okrs("okrs.json")
for okr in okrs:
    rule_result, llm_result = service.evaluate_okr(okr)
```

## 🔧 Configuration

### OpenAI API Setup

```bash
# Set environment variable
export OPENAI_API_KEY="your-api-key"

# Or pass directly in code
session = PlanningSession(api_key="your-key")
```

### Custom LLM Configuration

```python
from okr_evaluator import LLMConfig

config = LLMConfig(
    api_key="your-api-key",
    base_url="https://your-endpoint.com",
    model="gpt-4o",
    temperature=0.7,
    max_tokens=2000
)

service = OKREvaluatorService(llm_config=config)
```

## Best Practices

### Planning
1. **Start with clear strategic goals** - Well-defined goals lead to better epics
2. **Use appropriate timeframes** - Q1/Q2 for short-term, H1/H2 for medium-term
3. **Consider team capacity** - Set realistic num_epics based on team size
4. **Enable auto-refinement** - Let agents improve low-quality OKRs automatically
5. **Review and iterate** - Use refine_epic() to improve based on feedback

### Evaluation
1. **Always validate** OKR structure before evaluation
2. **Use strict mode** for production environments
3. **Handle errors** gracefully (LLM calls may fail)
4. **Log evaluations** for audit trails
5. **Version control** your OKR files

### Tracking
1. **Update progress regularly** - Weekly or bi-weekly updates recommended
2. **Monitor alerts** - Act on at-risk and behind alerts promptly
3. **Review baselines** - Ensure baselines reflect actual starting points
4. **Set realistic targets** - Ambitious but achievable (60-70% is excellent)
5. **Document ownership** - Clear owners for accountability

## 🚀 Getting Started

### Quick Setup

1. **Clone and install:**
```bash
cd pilot-okr
pip install -r requirements.txt
```

2. **Set API key:**
```bash
export OPENAI_API_KEY="your-key"
```

3. **Run examples:**
```bash
# AI Planning Example
python agents/examples/planning_session_example.py

# Or open Jupyter notebook
jupyter notebook okr-pilot.ipynb
```

### Your First Planning Session

```python
from agents import PlanningSession, TimeFrame

session = PlanningSession()
result = session.start(
    department_name="Your Department",
    strategic_goals=["Your Goal 1", "Your Goal 2"],
    timeframe=TimeFrame.Q1
)
session.print_summary()
```

## API Reference

See inline documentation in the source files for detailed API reference.

## License

Internal use only - Bosch AI Team

## Contributing

Contact the OKR Team for contribution guidelines.

## Support

For issues or questions, contact: [Your team contact]

---

**Version**: 1.0.0  
**Last Updated**: December 2025
