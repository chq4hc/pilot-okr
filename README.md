# OKR Evaluator

A professional-grade toolkit for evaluating, analyzing, and improving OKRs (Objectives and Key Results).

## Features

- **Rule-Based Scoring**: Automated evaluation based on OKR best practices
- **AI-Powered Analysis**: LLM-driven critique and improvement suggestions
- **Comprehensive Validation**: Structure and content validation
- **Rich Reporting**: Markdown and JSON output formats
- **File I/O**: Load and save OKRs in JSON format
- **Revision Suggestions**: Automated OKR improvement recommendations

## Installation

```bash
pip install openai pydantic
```

## Quick Start

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
├── okr_evaluator.py      # Core evaluation engine
├── okr_utils.py           # Utilities (I/O, formatting, validation)
├── okr_tracker.py         # Progress tracking and monitoring
├── __init__.py            # Package initialization
├── README.md              # This file
└── requirements.txt       # Dependencies
```

## Components

### OKREvaluatorService

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

## Best Practices

1. **Always validate** OKR structure before evaluation
2. **Use strict mode** for production environments
3. **Handle errors** gracefully (LLM calls may fail)
4. **Log evaluations** for audit trails
5. **Version control** your OKR files

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
