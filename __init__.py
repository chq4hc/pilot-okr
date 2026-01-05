"""
OKR Package

A comprehensive toolkit for OKR (Objectives and Key Results) evaluation,
analysis, and quality improvement.

Components:
- okr_evaluator: Core evaluation engine (rule-based + LLM)
- okr_utils: Utilities for file I/O, formatting, and validation
- okr_tracker: OKR tracking and progress monitoring
"""

__version__ = "1.0.0"
__author__ = "OKR Team"

from .okr_evaluator import (
    OKREvaluatorService,
    OKRRuleEngine,
    OKRLLMEvaluator,
    LLMConfig,
    OKREvaluation,
    QualityLabel,
    calculate_rule_score,
    call_llm,
    get_llm_critique,
)

from .okr_utils import (
    OKRFileHandler,
    OKRFormatter,
    OKRValidator,
    OKRReporter,
    load_okr_from_json,
    save_okr_to_json,
    json_to_markdown,
)

from .okr_tracker import (
    OKRTracker,
    KeyResultTracker,
    OKRStatus,
    AlertLevel,
    HealthAlert,
    ProgressSnapshot,
    calculate_okr_health_score,
    format_tracker_report,
    create_tracker_from_json,
    load_tracker_from_json_file,
)

__all__ = [
    # Main service
    "OKREvaluatorService",
    
    # Evaluation engines
    "OKRRuleEngine",
    "OKRLLMEvaluator",
    
    # Configuration
    "LLMConfig",
    
    # Data models
    "OKREvaluation",
    "QualityLabel",
    
    # Utilities
    "OKRFileHandler",
    "OKRFormatter",
    "OKRValidator",
    "OKRReporter",
    
    # Tracking
    "OKRTracker",
    "KeyResultTracker",
    "OKRStatus",
    "AlertLevel",
    "HealthAlert",
    "ProgressSnapshot",
    
    # Convenience functions
    "calculate_rule_score",
    "call_llm",
    "get_llm_critique",
    "load_okr_from_json",
    "save_okr_to_json",
    "json_to_markdown",
    "calculate_okr_health_score",
    "format_tracker_report",
    "create_tracker_from_json",
    "load_tracker_from_json_file",
]
