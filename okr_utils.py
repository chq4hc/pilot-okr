"""
OKR Utilities Module

Provides utility functions for OKR data handling, formatting, and persistence.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


# ============================================================================
# File I/O Operations
# ============================================================================

class OKRFileHandler:
    """Handle file operations for OKR data."""
    
    @staticmethod
    def load_okr(file_path: Union[str, Path]) -> Dict:
        """
        Load OKR data from a JSON file.
        
        Args:
            file_path: Path to the JSON file
        
        Returns:
            Dictionary containing OKR data
        
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
            ValueError: If OKR structure is invalid
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                okr_data = json.load(f)
            
            # Validate basic structure
            OKRFileHandler._validate_okr_structure(okr_data)
            
            logger.info(f"Successfully loaded OKR from {file_path}")
            logger.info(f"  Objective: '{okr_data.get('objective', 'N/A')}'")
            logger.info(f"  Key Results: {len(okr_data.get('key_results', []))}")
            
            return okr_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading OKR from {file_path}: {e}")
            raise
    
    @staticmethod
    def load_multiple_okrs(file_path: Union[str, Path]) -> List[Dict]:
        """
        Load multiple OKRs from a JSON file (expects array).
        
        Args:
            file_path: Path to the JSON file
        
        Returns:
            List of OKR dictionaries
        """
        file_path = Path(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("File must contain an array of OKR objects")
        
        # Validate each OKR
        for i, okr in enumerate(data):
            try:
                OKRFileHandler._validate_okr_structure(okr)
            except ValueError as e:
                logger.warning(f"OKR at index {i} failed validation: {e}")
        
        logger.info(f"Successfully loaded {len(data)} OKR(s) from {file_path}")
        return data
    
    @staticmethod
    def save_okr(okr_data: Dict, file_path: Union[str, Path], pretty: bool = True) -> None:
        """
        Save OKR data to a JSON file.
        
        Args:
            okr_data: Dictionary containing OKR data
            file_path: Path where the file will be saved
            pretty: Whether to format JSON with indentation
        """
        file_path = Path(file_path)
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(okr_data, f, indent=4, ensure_ascii=False)
            else:
                json.dump(okr_data, f, ensure_ascii=False)
        
        logger.info(f"Successfully saved OKR to {file_path}")
    
    @staticmethod
    def _validate_okr_structure(okr_data: Dict) -> None:
        """Validate basic OKR structure."""
        if not isinstance(okr_data, dict):
            raise ValueError("OKR data must be a dictionary")
        
        if "objective" not in okr_data:
            raise ValueError("OKR must contain 'objective' field")
        
        if "key_results" not in okr_data:
            raise ValueError("OKR must contain 'key_results' field")
        
        if not isinstance(okr_data["key_results"], list):
            raise ValueError("'key_results' must be a list")


# ============================================================================
# Formatting and Display
# ============================================================================

class OKRFormatter:
    """Format OKR data and evaluation results for display."""
    
    @staticmethod
    def format_okr_markdown(okr_data: Dict) -> str:
        """
        Format OKR data as Markdown.
        
        Args:
            okr_data: OKR dictionary
        
        Returns:
            Markdown-formatted string
        """
        md = f"# Objective\n\n"
        md += f"**{okr_data.get('objective', 'No objective specified')}**\n\n"
        
        md += f"## Key Results\n\n"
        
        key_results = okr_data.get('key_results', [])
        if not key_results:
            md += "_No key results defined_\n"
        else:
            for i, kr in enumerate(key_results, 1):
                md += f"### {i}. {kr.get('text', 'Undefined')}\n\n"
                
                if kr.get('baseline'):
                    md += f"- **Baseline:** {kr['baseline']}\n"
                if kr.get('target'):
                    md += f"- **Target:** {kr['target']}\n"
                if kr.get('deadline'):
                    md += f"- **Deadline:** {kr['deadline']}\n"
                if kr.get('owner'):
                    md += f"- **Owner:** {kr['owner']}\n"
                
                md += "\n"
        
        return md
    
    @staticmethod
    def format_evaluation_markdown(evaluation_data: Dict) -> str:
        """
        Format evaluation results as Markdown.
        
        Args:
            evaluation_data: Evaluation result dictionary (or JSON string)
        
        Returns:
            Markdown-formatted report
        """

      
        md = f"# OKR Evaluation Report\n\n"
        md += f"**Quality Label:** `{evaluation_data.get('quality_label', 'N/A')}`  \n"
        md += f"**Total Score:** `{evaluation_data.get('total_score', 0)}/10`\n\n"
        
        # Critique section
        md += "## Detailed Critique\n\n"
        critique = evaluation_data.get('critique', {})
        critique = critique.__dict__
                    
        # Extract the three key attributes in order
        for dimension, feedback in critique.items():
            feedback = critique[dimension]
            md += f" **{dimension.capitalize()}** : {feedback} \n"
     
        md += "\n"
        
        # Improvement suggestions
        md += "## Improvement Suggestions\n\n"
        suggestions = evaluation_data.get('improvement_suggestions', [])
        
        if suggestions:
            for i, suggestion in enumerate(suggestions, 1):
                md += f"{i}. {suggestion}\n"
        else:
            md += "_No suggestions available_\n"
        
        md += "\n"
        
        # Action plan (if available)
        action_plan = evaluation_data.get('action_plan', [])
        if action_plan:
            md += "## Action Plan\n\n"
            for i, item in enumerate(action_plan, 1):
                md += f"### {i}. {item.get('task', 'Task undefined')}\n\n"
                md += f"- **Owner:** {item.get('owner', 'Not assigned')}\n"
                md += f"- **Cadence:** {item.get('cadence', 'Not specified')}\n"
                md += f"- **Blockers:** {item.get('blockers', 'None identified')}\n\n"
        
        return md
    
    @staticmethod
    def format_okr_summary(okr_data: Dict) -> str:
        """
        Create a concise summary of an OKR.
        
        Args:
            okr_data: OKR dictionary
        
        Returns:
            Summary string
        """
        objective = okr_data.get('objective', 'No objective')
        kr_count = len(okr_data.get('key_results', []))
        
        summary = f"Objective: {objective}\n"
        summary += f"Key Results: {kr_count}\n"
        
        # Count complete KRs (with baseline, target, deadline)
        complete_krs = sum(
            1 for kr in okr_data.get('key_results', [])
            if all(kr.get(field) for field in ['baseline', 'target', 'deadline'])
        )
        
        summary += f"Complete KRs: {complete_krs}/{kr_count}\n"
        
        return summary


# ============================================================================
# Data Validation and Sanitization
# ============================================================================

class OKRValidator:
    """Validate and sanitize OKR data."""
    
    @staticmethod
    def validate_okr(okr_data: Dict, strict: bool = False) -> tuple[bool, List[str]]:
        """
        Validate OKR data structure and content.
        
        Args:
            okr_data: OKR dictionary to validate
            strict: If True, enforce stricter validation rules
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check basic structure
        if not isinstance(okr_data, dict):
            return False, ["OKR data must be a dictionary"]
        
        # Check objective
        if 'objective' not in okr_data:
            issues.append("Missing 'objective' field")
        elif not okr_data['objective'] or not okr_data['objective'].strip():
            issues.append("Objective is empty")
        
        # Check key results
        if 'key_results' not in okr_data:
            issues.append("Missing 'key_results' field")
        else:
            key_results = okr_data['key_results']
            
            if not isinstance(key_results, list):
                issues.append("'key_results' must be a list")
            elif len(key_results) == 0:
                issues.append("No key results defined")
            elif strict and not (3 <= len(key_results) <= 5):
                issues.append(f"Optimal number of key results is 3-5 (found {len(key_results)})")
            
            # Validate each key result
            for i, kr in enumerate(key_results):
                if not isinstance(kr, dict):
                    issues.append(f"Key result #{i+1} must be a dictionary")
                    continue
                
                if 'text' not in kr or not kr['text']:
                    issues.append(f"Key result #{i+1} missing or empty 'text' field")
                
                if strict:
                    missing_fields = [
                        field for field in ['baseline', 'target', 'deadline']
                        if field not in kr or not kr[field]
                    ]
                    if missing_fields:
                        issues.append(
                            f"Key result #{i+1} missing: {', '.join(missing_fields)}"
                        )
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    @staticmethod
    def sanitize_okr(okr_data: Dict) -> Dict:
        """
        Clean and normalize OKR data.
        
        Args:
            okr_data: Raw OKR dictionary
        
        Returns:
            Sanitized OKR dictionary
        """
        sanitized = {}
        
        # Clean objective
        sanitized['objective'] = str(okr_data.get('objective', '')).strip()
        
        # Clean key results
        key_results = okr_data.get('key_results', [])
        sanitized['key_results'] = []
        
        for kr in key_results:
            if isinstance(kr, dict):
                clean_kr = {
                    'text': str(kr.get('text', '')).strip(),
                    'baseline': str(kr.get('baseline', '')).strip() if kr.get('baseline') else None,
                    'target': str(kr.get('target', '')).strip() if kr.get('target') else None,
                    'deadline': str(kr.get('deadline', '')).strip() if kr.get('deadline') else None,
                }
                
                # Add optional fields if present
                if 'owner' in kr:
                    clean_kr['owner'] = str(kr['owner']).strip()
                
                sanitized['key_results'].append(clean_kr)
        
        return sanitized


# ============================================================================
# Reporting
# ============================================================================

class OKRReporter:
    """Generate reports for OKR evaluations."""
    
    @staticmethod
    def generate_evaluation_report(
        okr_data: Dict,
        rule_result: Dict,
        llm_result: Optional[Dict] = None,
        output_path: Optional[Union[str, Path]] = None
    ) -> str:
        """
        Generate a comprehensive evaluation report.
        
        Args:
            okr_data: The OKR data
            rule_result: Rule-based evaluation result
            llm_result: LLM evaluation result (optional)
            output_path: If provided, save report to this file
        
        Returns:
            Report as Markdown string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"# OKR Evaluation Report\n\n"
        report += f"**Generated:** {timestamp}\n\n"
        report += "---\n\n"
        
        # OKR Summary
        report += "## OKR Summary\n\n"
        report += OKRFormatter.format_okr_markdown(okr_data)
        report += "\n---\n\n"
        
        # Rule-based score
        report += "## Rule-Based Assessment\n\n"
        report += f"**Score:** {rule_result.get('numeric_score', 0)}/4\n\n"
        
        breakdown = rule_result.get('rule_breakdown', {})
        if breakdown:
            report += "### Breakdown\n\n"
            for criterion, feedback in breakdown.items():
                report += f"- **{criterion.replace('_', ' ').title()}:** {feedback}\n"
        
        report += "\n"
        
        # LLM evaluation (if available)
        if llm_result:
            report += "---\n\n"
            report += "## AI-Powered Evaluation\n\n"
            report += OKRFormatter.format_evaluation_markdown(llm_result)
        
        # Save to file if requested
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report saved to {output_path}")
        
        return report


# ============================================================================
# Convenience Functions
# ============================================================================

def load_okr_from_json(file_path: str) -> Dict:
    """Load OKR from JSON file (convenience function)."""
    return OKRFileHandler.load_okr(file_path)


def save_okr_to_json(okr_data: Dict, file_path: str) -> None:
    """Save OKR to JSON file (convenience function)."""
    return OKRFileHandler.save_okr(okr_data, file_path)


def json_to_markdown(json_data: Union[str, Dict]) -> str:
    """Convert evaluation JSON to Markdown (convenience function)."""
    return OKRFormatter.format_evaluation_markdown(json_data)
