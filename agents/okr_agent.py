"""
OKR Planning Agent - Microsoft Swarm Implementation

This agent specializes in creating measurable Objectives and Key Results (OKRs)
for epics. It ensures OKRs follow best practices and are aligned with strategic goals.
"""

import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from .models import Epic, Objective, KeyResult, Priority, TimeFrame, PlanningContext


class OKRPlanningAgent:
    """
    Agent responsible for generating OKRs (Objectives and Key Results) for epics.
    
    This agent acts as an OKR expert, creating measurable objectives with 
    well-defined key results that track progress toward epic completion.
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the OKR Planning Agent.
        
        Args:
            api_key: OpenAI API key (if None, reads from environment)
            model: OpenAI model to use
            temperature: Creativity level (0.0-1.0)
        """
        self.config = config or LLMConfig()
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url
        )
        self.model = self.config.model
        self.temperature = self.config.temperature
        self.agent_name = "OKR Planning Agent"
    
    def generate_okrs_for_epic(
        self,
        epic: Epic,
        context: PlanningContext,
        num_objectives: int = 3
    ) -> List[Objective]:
        """
        Generate OKRs for a specific epic.
        
        Args:
            epic: Epic to create OKRs for
            context: Planning context
            num_objectives: Number of objectives to generate (default: 3)
        
        Returns:
            List of Objective objects with Key Results
        """
        prompt = self._build_okr_generation_prompt(epic, context, num_objectives)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            objectives = self._parse_okr_response(result, epic, context)
            
            return objectives
            
        except Exception as e:
            print(f"Error generating OKRs: {e}")
            return []
    
    def refine_objective(
        self,
        objective: Objective,
        feedback: str,
        epic: Epic
    ) -> Objective:
        """
        Refine an existing objective based on feedback.
        
        Args:
            objective: Objective to refine
            feedback: Feedback or requirements
            epic: Parent epic for context
        
        Returns:
            Refined Objective
        """
        prompt = f"""
        Refine the following objective based on feedback.
        
        **Epic Context:**
        {epic.title}: {epic.description}
        
        **Current Objective:**
        {objective.title}
        {objective.description}
        
        **Current Key Results:**
        {chr(10).join(f'- {kr.description}: {kr.baseline} → {kr.target} {kr.unit}' for kr in objective.key_results)}
        
        **Feedback:**
        {feedback}
        
        Provide a refined version addressing the feedback while maintaining 
        measurability and alignment with the epic. Return as JSON.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            objectives = self._parse_okr_response(result, epic, None)
            
            return objectives[0] if objectives else objective
            
        except Exception as e:
            print(f"Error refining objective: {e}")
            return objective
    
    def validate_key_results(self, key_results: List[KeyResult]) -> Dict[str, Any]:
        """
        Validate key results for quality and measurability.
        
        Args:
            key_results: List of key results to validate
        
        Returns:
            Validation report with issues and suggestions
        """
        issues = []
        suggestions = []
        
        if len(key_results) < 2:
            issues.append("Too few key results (minimum 2 recommended)")
        elif len(key_results) > 5:
            issues.append("Too many key results (maximum 5 recommended)")
        
        for i, kr in enumerate(key_results, 1):
            # Check if metric is measurable
            if not kr.metric or not kr.unit:
                issues.append(f"KR {i}: Missing metric or unit")
            
            # Check if target is realistic
            if kr.target == kr.baseline:
                issues.append(f"KR {i}: Target equals baseline - no growth expected")
            
            # Check if description is clear
            if len(kr.description.split()) < 3:
                suggestions.append(f"KR {i}: Description could be more detailed")
            
            # Check if metric matches unit
            common_units = ['%', 'users', 'days', 'hours', 'dollars', 'count']
            if kr.unit.lower() not in common_units and kr.unit not in kr.metric.lower():
                suggestions.append(f"KR {i}: Verify metric '{kr.metric}' matches unit '{kr.unit}'")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "score": max(0, 100 - (len(issues) * 20) - (len(suggestions) * 5))
        }
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the OKR Planning Agent."""
        return """You are an expert OKR Planning Agent specializing in creating 
effective Objectives and Key Results. Your role is to:

1. Create inspiring, qualitative objectives that align with epic goals
2. Define 2-5 measurable key results for each objective
3. Ensure key results are SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
4. Use appropriate metrics and units of measurement
5. Set realistic baselines and ambitious but achievable targets

OKR Best Practices:
- Objectives should be qualitative, inspiring, and action-oriented
- Key Results must be quantitative and measurable
- Each KR should have a clear metric, baseline, target, and unit
- Targets should be ambitious (60-70% achievement is excellent)
- Avoid activity-based metrics; focus on outcomes
- Ensure alignment with parent epic and strategic goals

Key Result Guidelines:
- Use concrete numbers (e.g., "Increase from 100 to 500 users")
- Include units (%, users, days, $, etc.)
- Baseline should reflect current state
- Target should be stretch but realistic
- Metrics should be objectively measurable

Always return responses in valid JSON format matching the schema."""
    
    def _build_okr_generation_prompt(
        self,
        epic: Epic,
        context: PlanningContext,
        num_objectives: int
    ) -> str:
        """Build the prompt for OKR generation."""
        return f"""
Generate {num_objectives} Objectives with Key Results for the following epic:

**Epic:** {epic.title}
**Description:** {epic.description}
**Business Value:** {epic.business_value}
**Priority:** {epic.priority.value}
**Timeframe:** {epic.timeframe.value if epic.timeframe else context.timeframe.value}

**Department:** {context.department.name}
**Strategic Goals:**
{chr(10).join(f'- {goal}' for goal in context.department.strategic_goals)}

Create {num_objectives} objectives that:
1. Directly contribute to the epic's success
2. Are inspiring and qualitative
3. Each have 2-5 measurable key results
4. Cover different aspects of the epic (e.g., adoption, quality, efficiency)
5. Are achievable within the timeframe

For each Key Result, provide:
- Clear description of what's being measured
- Specific metric name
- Current baseline value
- Target value to achieve
- Unit of measurement
- Owner (if known)

Return as JSON with this structure:
{{
    "objectives": [
        {{
            "id": "obj-001",
            "title": "Inspiring objective title",
            "description": "What this objective aims to achieve",
            "priority": "high|medium|low|critical",
            "owner": "Team or person name",
            "timeframe": "{epic.timeframe.value if epic.timeframe else context.timeframe.value}",
            "epic_id": "{epic.id}",
            "key_results": [
                {{
                    "id": "kr-001",
                    "description": "What will be measured",
                    "metric": "Specific metric name",
                    "baseline": 100.0,
                    "target": 500.0,
                    "current": 100.0,
                    "unit": "users",
                    "owner": "Person responsible",
                    "due_date": "YYYY-MM-DD"
                }}
            ]
        }}
    ]
}}
"""
    
    def _parse_okr_response(
        self,
        response: Dict[str, Any],
        epic: Epic,
        context: Optional[PlanningContext]
    ) -> List[Objective]:
        """Parse the LLM response into Objective objects."""
        objectives = []
        
        for obj_data in response.get("objectives", []):
            try:
                # Map priority string to enum
                priority_str = obj_data.get("priority", "medium").lower()
                priority_map = {
                    "critical": Priority.CRITICAL,
                    "high": Priority.HIGH,
                    "medium": Priority.MEDIUM,
                    "low": Priority.LOW
                }
                priority = priority_map.get(priority_str, Priority.MEDIUM)
                
                # Map timeframe string to enum
                timeframe_str = obj_data.get("timeframe", "").upper()
                timeframe = None
                try:
                    timeframe = TimeFrame[timeframe_str] if timeframe_str else None
                except KeyError:
                    timeframe = epic.timeframe
                
                # Parse key results
                key_results = []
                for kr_data in obj_data.get("key_results", []):
                    try:
                        kr = KeyResult(
                            id=kr_data.get("id", f"kr-{len(key_results) + 1:03d}"),
                            description=kr_data["description"],
                            metric=kr_data["metric"],
                            baseline=float(kr_data["baseline"]),
                            target=float(kr_data["target"]),
                            current=float(kr_data.get("current", kr_data["baseline"])),
                            unit=kr_data["unit"],
                            owner=kr_data.get("owner"),
                            due_date=kr_data.get("due_date")
                        )
                        key_results.append(kr)
                    except (KeyError, ValueError) as e:
                        print(f"Error parsing key result: {e}")
                        continue
                
                # Create objective
                objective = Objective(
                    id=obj_data.get("id", f"obj-{len(objectives) + 1:03d}"),
                    title=obj_data["title"],
                    description=obj_data["description"],
                    key_results=key_results,
                    priority=priority,
                    owner=obj_data.get("owner"),
                    timeframe=timeframe,
                    epic_id=obj_data.get("epic_id", epic.id)
                )
                
                objectives.append(objective)
                
            except KeyError as e:
                print(f"Missing required field in objective data: {e}")
                continue
            except Exception as e:
                print(f"Error parsing objective: {e}")
                continue
        
        return objectives
    
    def suggest_metrics(self, objective_title: str) -> List[str]:
        """
        Suggest appropriate metrics for an objective.
        
        Args:
            objective_title: Title of the objective
        
        Returns:
            List of suggested metric names
        """
        prompt = f"""
        Suggest 5 specific, measurable metrics for this objective:
        "{objective_title}"
        
        Return only the metric names as a JSON array of strings.
        Example: {{"metrics": ["Active user count", "Customer satisfaction score", ...]}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in defining measurable metrics for OKRs."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("metrics", [])
            
        except Exception as e:
            print(f"Error suggesting metrics: {e}")
            return []
    
    def calculate_objective_health(self, objective: Objective) -> Dict[str, Any]:
        """
        Calculate the health status of an objective based on KR progress.
        
        Args:
            objective: Objective to analyze
        
        Returns:
            Health report with status and recommendations
        """
        if not objective.key_results:
            return {
                "status": "unknown",
                "score": 0,
                "message": "No key results defined"
            }
        
        progress = objective.overall_progress
        on_track_count = sum(1 for kr in objective.key_results if kr.progress_percentage >= 70)
        at_risk_count = sum(1 for kr in objective.key_results if kr.progress_percentage < 30)
        
        if progress >= 70:
            status = "on-track"
            message = "Objective is progressing well"
        elif progress >= 40:
            status = "at-risk"
            message = f"{at_risk_count} key result(s) need attention"
        else:
            status = "critical"
            message = "Objective is significantly behind target"
        
        return {
            "status": status,
            "score": progress,
            "message": message,
            "on_track_krs": on_track_count,
            "at_risk_krs": at_risk_count,
            "total_krs": len(objective.key_results)
        }
