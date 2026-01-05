"""
OKR Evaluator Module

This module provides comprehensive OKR (Objectives and Key Results) evaluation capabilities,
including rule-based scoring, LLM-powered critique, and automated revision suggestions.

Author: OKR Team
Date: December 2025
"""

import json
import re
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, ValidationError
import openai
from openai import OpenAI


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class LLMConfig:
    """Configuration for LLM API connection."""
    api_key: str = "sk-bgsv-ai-team"
    base_url: str = "https://sx-bgsv-llm.agreeablerock-77e2087d.southeastasia.azurecontainerapps.io/"
    model: str = "azure-gpt-5"
    temperature: float = 1.0
    max_tokens: int = 2000
    timeout: int = 30


# ============================================================================
# Data Models
# ============================================================================

class QualityLabel(str, Enum):
    """Quality assessment labels for OKRs."""
    HIGH = "High"
    NEUTRAL = "Neutral"
    LOW = "Low"


class ActionItem(BaseModel):
    """Action item for OKR execution plan."""
    task: str = Field(..., description="Specific task to be completed")
    owner: str = Field(..., description="Person or role responsible")
    cadence: str = Field(..., description="Frequency or timeline for completion")
    blockers: str = Field(..., description="Potential obstacles or dependencies")


class Critique(BaseModel):
    """Detailed critique of OKR quality."""
    clarity: str = Field(..., description="Assessment of objective clarity")
    alignment: str = Field(..., description="Assessment of strategic alignment")
    balance: str = Field(..., description="Assessment of leading/lagging indicators balance")


class OKREvaluation(BaseModel):
    """Complete OKR evaluation result."""
    quality_label: QualityLabel = Field(..., description="Overall quality assessment")
    total_score: int = Field(..., ge=0, le=10, description="Numeric score out of 10")
    critique: Critique = Field(..., description="Detailed critique by dimension")
    improvement_suggestions: List[str] = Field(
        default_factory=list,
        description="Actionable improvement recommendations"
    )
    action_plan: Optional[List[ActionItem]] = Field(
        default=None,
        description="Execution action plan"
    )


class KeyResult(BaseModel):
    """Structure for a Key Result."""
    text: str = Field(..., description="Description of the key result")
    baseline: Optional[str] = Field(None, description="Starting point or current state")
    target: Optional[str] = Field(None, description="Desired outcome or goal")
    deadline: Optional[str] = Field(None, description="Due date or timeframe")
    owner: Optional[str] = Field(None, description="Person or team responsible")


class OKR(BaseModel):
    """Structure for an OKR (Objective and Key Results)."""
    objective: str = Field(..., description="The overarching goal")
    key_results: List[KeyResult] = Field(
        default_factory=list,
        description="Measurable results that define success"
    )


@dataclass
class RuleScoreResult:
    """Result of rule-based scoring."""
    numeric_score: int
    rule_breakdown: Dict[str, str]
    max_score: int = 4


# ============================================================================
# Rule-Based Scoring Engine
# ============================================================================

class OKRRuleEngine:
    """Rule-based scoring engine for OKR quality assessment."""
    
    OPTIMAL_KR_MIN = 3
    OPTIMAL_KR_MAX = 5
    MAX_STRUCTURE_POINTS = 2
    MAX_FORMAT_POINTS = 2
    REQUIRED_KR_FIELDS = ("baseline", "target", "deadline")
    
    @classmethod
    def calculate_score(cls, okr_data: Dict) -> RuleScoreResult:
        """
        Calculate rule-based score for an OKR.
        
        Scoring criteria:
        1. KR Count (0-2 points):
           - 3-5 KRs: 2 points (optimal)
           - 1-2 or 6+ KRs: 1 point (suboptimal)
           - 0 KRs: 0 points
        
        2. KR Format (0-2 points):
           - All KRs have baseline, target, deadline: 2 points
           - Some KRs have all fields: 1 point
           - No KRs have all fields: 0 points
        
        Args:
            okr_data: Dictionary containing 'objective' and 'key_results'
        
        Returns:
            RuleScoreResult with score and breakdown
        """
        score = 0
        breakdown = {}
        
        # Validate input
        if not isinstance(okr_data, dict):
            raise ValueError("okr_data must be a dictionary")
        
        key_results = okr_data.get("key_results", [])
        kr_count = len(key_results)
        
        # 1. Evaluate KR count
        structure_points, structure_msg = cls._evaluate_kr_count(kr_count)
        score += structure_points
        breakdown["kr_structure"] = structure_msg
        
        # 2. Evaluate KR format completeness
        format_points, format_msg = cls._evaluate_kr_format(key_results, kr_count)
        score += format_points
        breakdown["kr_format"] = format_msg
        
        logger.info(f"Rule-based score calculated: {score}/4 for OKR with {kr_count} KRs")
        
        return RuleScoreResult(
            numeric_score=score,
            rule_breakdown=breakdown,
            max_score=4
        )
    
    @classmethod
    def _evaluate_kr_count(cls, kr_count: int) -> Tuple[int, str]:
        """Evaluate the number of key results."""
        if cls.OPTIMAL_KR_MIN <= kr_count <= cls.OPTIMAL_KR_MAX:
            return 2, f"Optimal number of KRs ({kr_count}/3-5)."
        elif kr_count > 0:
            return 1, f"Suboptimal number of KRs ({kr_count}). Aim for 3-5."
        else:
            return 0, "No KRs defined."
    
    @classmethod
    def _evaluate_kr_format(cls, key_results: List, kr_count: int) -> Tuple[int, str]:
        """Evaluate the completeness of KR fields."""
        if kr_count == 0:
            return 0, "No KRs to evaluate."
        
        complete_krs = sum(
            1 for kr in key_results
            if all(k in kr for k in cls.REQUIRED_KR_FIELDS)
        )
        
        if complete_krs == kr_count:
            return 2, f"All {kr_count} KRs have baseline, target, and deadline."
        elif complete_krs > 0:
            return 1, f"Only {complete_krs}/{kr_count} KRs have all required fields."
        else:
            return 0, "No KRs have all required fields (baseline, target, deadline)."


# ============================================================================
# LLM Integration
# ============================================================================

class OKRLLMEvaluator:
    """LLM-powered OKR evaluator for advanced assessment."""
    
    SYSTEM_PROMPT = "You are a professional OKR strategist and quality auditor with expertise in organizational goal-setting frameworks."
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM evaluator.
        
        Args:
            config: LLM configuration (uses default if not provided)
        """
        self.config = config or LLMConfig()
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url
        )
        logger.info(f"Initialized LLM evaluator with model: {self.config.model}")
    
    def create_evaluation_prompt(self, okr_data: Dict, rule_score: int) -> str:
        """
        Create a structured prompt for OKR evaluation.
        
        Args:
            okr_data: The OKR data to evaluate
            rule_score: The rule-based score (0-4)
        
        Returns:
            Formatted prompt string
        """
        prompt = f"""
            Evaluate the following OKR based on these criteria:

            1. **Objective Clarity**: Is the objective outcome-focused (not activity-focused)? Is it inspiring and clear?
            2. **Leading/Lagging Balance**: Do the key results include both leading (predictive) and lagging (outcome) indicators?
            3. **Ambition vs Attainability**: Are the targets ambitious yet achievable? (70% success rate is ideal)
            4. **Dependency Clarity**: Are dependencies and ownership clear?

            **OKR Data:**
            {json.dumps(okr_data, indent=2)}

            **Base Rule Score:** {rule_score}/4

            **Scoring Guide:**
            - Total score is out of 10
            - Rule score contributes {rule_score}/4 points (already calculated)
            - Your LLM assessment should contribute 0-6 additional points based on the four criteria above
            - llm_score = LLM assessment, maximum of 6
            - total_score = rule_score + llm_score (maximum of 10)

            **Quality Labels:**
            - High: 8-10 points (well-structured, clear, measurable)
            - Neutral: 5-7 points (acceptable but needs improvement)
            - Low: 0-4 points (significant issues, requires major revision)

            Return ONLY a JSON object with this exact schema:
            {{
                "quality_label": "High" | "Neutral" | "Low",
                "llm_score": int,
                "total_score": rule_score + llm_score,
                "critique": {{
                    "clarity": "Assessment of objective clarity and outcome-focus",
                    "alignment": "Assessment of strategic alignment and balance",
                    "balance": "Assessment of leading/lagging indicators and ambition"
                }},
                "improvement_suggestions": ["specific actionable suggestion 1", "suggestion 2", ...]
            }}
            """
        return prompt
    
    def evaluate(self, okr_data: Dict, rule_score: int) -> Optional[OKREvaluation]:
        """
        Evaluate OKR using LLM.
        
        Args:
            okr_data: The OKR data to evaluate
            rule_score: The rule-based score
        
        Returns:
            OKREvaluation object or None if evaluation fails
        """
        try:
            prompt = self.create_evaluation_prompt(okr_data, rule_score)
            
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            
            logger.info("Sending evaluation request to LLM")
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages
            )

            
            response_text = response.choices[0].message.content
            logger.debug(f"LLM response: {response_text}")
            
            # Clean markdown code blocks if present
            if response_text:
                response_text = response_text.strip()
                response_text = re.sub(r'^```json\s*', '', response_text)
                response_text = re.sub(r'^```\s*', '', response_text)
                response_text = re.sub(r'\s*```$', '', response_text)
            else:
                logger.error("Received empty response from LLM")
                return None
                
            
            # Parse and validate response
            evaluation_data = json.loads(response_text)
            evaluation = OKREvaluation(
                    quality_label=QualityLabel.NEUTRAL,
                    total_score=evaluation_data['total_score'],
                    critique=Critique(
                        clarity=evaluation_data['critique']['clarity'],
                        alignment=evaluation_data['critique']['alignment'],
                        balance=evaluation_data['critique']['balance']
                    ),
                    improvement_suggestions=evaluation_data.get('improvement_suggestions', [])
                )
            
            logger.info(f"LLM evaluation completed: {evaluation.quality_label} ({evaluation.total_score}/10)")
            return evaluation
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return None
        except ValidationError as e:
            logger.error(f"LLM response validation failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error during LLM evaluation: {e}")
            return None
    
    def revise_okr(self, okr_data: Dict, evaluation: OKREvaluation) -> Optional[OKR]:
        """
        Generate a revised OKR based on improvement suggestions.
        
        Args:
            okr_data: Original OKR data
            evaluation: The evaluation result with improvement suggestions
        
        Returns:
            Revised OKR object or None if revision fails
        """
        try:
            revision_prompt = f"""
You are an OKR expert. Revise the following OKR based on the improvement suggestions.

**Original OKR:**
{json.dumps(okr_data, indent=2)}

**Improvement Suggestions:**
{json.dumps(evaluation.improvement_suggestions, indent=2)}

**Requirements for the revised OKR:**
1. Clear, outcome-focused objective (not activity-focused)
2. 3-5 measurable key results
3. Each KR must have: text, baseline, target, deadline, and owner
4. Address all improvement suggestions
5. Maintain SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)

Return ONLY a JSON object with this structure:
{{
    "objective": "Clear, inspiring, outcome-focused objective",
    "key_results": [
        {{
            "text": "Measurable key result description",
            "baseline": "Specific current state (e.g., '100 users', 'Current NPS: 45')",
            "target": "Specific target (e.g., '500 users', 'Target NPS: 70')",
            "deadline": "Specific date or timeframe (e.g., 'Q2 2026', 'June 30, 2026')",
            "owner": "Person or role responsible (e.g., 'Product Manager', 'John Doe')"
        }}
    ]
}}
"""
            
            messages = [
                {"role": "system", "content": "You are a professional OKR strategist specializing in creating high-quality, measurable objectives and key results."},
                {"role": "user", "content": revision_prompt}
            ]
            
            logger.info("Requesting OKR revision from LLM")
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature
            )
            
            response_text = response.choices[0].message.content
            
            # Clean markdown code blocks if present
            response_text = re.sub(r'^```json\s*', '', response_text.strip())
            response_text = re.sub(r'\s*```$', '', response_text.strip())
            
            # Parse and validate
            revised_data = json.loads(response_text)
            revised_okr = OKR(**revised_data)
            
            logger.info("OKR revision completed successfully")
            return revised_okr
            
        except Exception as e:
            logger.error(f"Error during OKR revision: {e}")
            return None


# ============================================================================
# Main Evaluator Class
# ============================================================================

class OKREvaluatorService:
    """
    Comprehensive OKR evaluation service combining rule-based and LLM evaluation.
    """
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """
        Initialize the OKR evaluator service.
        
        Args:
            llm_config: Optional LLM configuration
        """
        self.rule_engine = OKRRuleEngine()
        self.llm_evaluator = OKRLLMEvaluator(llm_config)
        logger.info("OKR Evaluator Service initialized")
    
    def evaluate_okr(self, okr_data: Dict) -> Tuple[RuleScoreResult, Optional[OKREvaluation]]:
        """
        Perform complete OKR evaluation using both rule-based and LLM methods.
        
        Args:
            okr_data: Dictionary containing OKR data
        
        Returns:
            Tuple of (RuleScoreResult, OKREvaluation)
        """
        logger.info("Starting comprehensive OKR evaluation")
        
        # Step 1: Rule-based scoring
        rule_result = self.rule_engine.calculate_score(okr_data)
        logger.info(f"Rule-based score: {rule_result.numeric_score}/{rule_result.max_score}")
        
        # Step 2: LLM evaluation
        llm_result = self.llm_evaluator.evaluate(okr_data, rule_result.numeric_score)
        
        return rule_result, llm_result
    
    def evaluate_and_revise(self, okr_data: Dict) -> Tuple[RuleScoreResult, Optional[OKREvaluation], Optional[OKR]]:
        """
        Evaluate an OKR and generate a revised version if needed.
        
        Args:
            okr_data: Dictionary containing OKR data
        
        Returns:
            Tuple of (RuleScoreResult, OKREvaluation, revised OKR)
        """
        rule_result, llm_result = self.evaluate_okr(okr_data)
        
        revised_okr = None
        if llm_result and llm_result.improvement_suggestions:
            logger.info("Generating revised OKR based on improvement suggestions")
            revised_okr = self.llm_evaluator.revise_okr(okr_data, llm_result)
        
        return rule_result, llm_result, revised_okr


# ============================================================================
# Convenience Functions (Backward Compatibility)
# ============================================================================

def calculate_rule_score(okr_data: Dict) -> Dict:
    """
    Calculate rule-based score for an OKR (legacy interface).
    
    Args:
        okr_data: Dictionary containing OKR data
    
    Returns:
        Dictionary with 'numeric_score' and 'rule_breakdown'
    """
    result = OKRRuleEngine.calculate_score(okr_data)
    return {
        "numeric_score": result.numeric_score,
        "rule_breakdown": result.rule_breakdown
    }


def call_llm(prompt_text: str, config: Optional[LLMConfig] = None) -> Optional[str]:
    """
    Call LLM with a custom prompt (legacy interface).
    
    Args:
        prompt_text: The prompt to send
        config: Optional LLM configuration
    
    Returns:
        Response text or None if call fails
    """
    try:
        cfg = config or LLMConfig()
        client = OpenAI(api_key=cfg.api_key, base_url=cfg.base_url)
        
        messages = [
            {"role": "system", "content": OKRLLMEvaluator.SYSTEM_PROMPT},
            {"role": "user", "content": prompt_text}
        ]
        
        response = client.chat.completions.create(
            model=cfg.model,
            messages=messages
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        return None


def get_llm_critique(okr_data: Dict, rule_score: int) -> str:
    """
    Generate critique prompt for an OKR (legacy interface).
    
    Args:
        okr_data: The OKR data
        rule_score: Rule-based score
    
    Returns:
        Formatted prompt string
    """
    evaluator = OKRLLMEvaluator()
    return evaluator.create_evaluation_prompt(okr_data, rule_score)


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example OKR
    example_okr = {
        "objective": "Double sales over the next two years",
        "key_results": [
            {
                "text": "Identify a new ICP (Ideal Customer Profile) to target",
                "baseline": "none",
                "target": "1 new ICP",
                "deadline": "October 2022"
            },
            {
                "text": "Boost engagement on digital platforms",
                "baseline": "Current engagement level",
                "target": "25% increase",
                "deadline": "Each quarter"
            },
            {
                "text": "Expand the sales team",
                "baseline": "Current team size",
                "target": "30% increase",
                "deadline": "One year from start"
            }
        ]
    }
    
    # Initialize service
    service = OKREvaluatorService()
    
    # Evaluate
    rule_result, llm_result = service.evaluate_okr(example_okr)
    
    print(f"\n{'='*60}")
    print("OKR EVALUATION RESULTS")
    print(f"{'='*60}")
    print(f"\nRule-based Score: {rule_result.numeric_score}/{rule_result.max_score}")
    print(f"Breakdown: {json.dumps(rule_result.rule_breakdown, indent=2)}")
    
    if llm_result:
        print(f"\nLLM Evaluation:")
        print(f"  Quality: {llm_result.quality_label}")
        print(f"  Total Score: {llm_result.total_score}/10")
        print(f"\nImprovement Suggestions:")
        for i, suggestion in enumerate(llm_result.improvement_suggestions, 1):
            print(f"  {i}. {suggestion}")
