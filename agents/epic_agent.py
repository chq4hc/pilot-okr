"""
Epic Planning Agent - Microsoft Swarm Implementation

This agent specializes in breaking down departmental strategic goals into 
actionable epics. It uses LLM-based reasoning to create comprehensive epic 
definitions with proper prioritization and scoping.
"""

import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from .models import Department, Epic, Priority, TimeFrame, PlanningContext


class EpicPlanningAgent:
    """
    Agent responsible for analyzing departmental goals and generating epics.
    
    This agent acts as a strategic planner, taking high-level goals and 
    breaking them down into executable epics with clear business value.
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Epic Planning Agent.
        
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
        self.agent_name = "Epic Planning Agent"
    
    def plan_epics(
        self,
        context: PlanningContext,
        num_epics: int = 3
    ) -> List[Epic]:
        """
        Generate epics based on department context.
        
        Args:
            context: Planning context with department info and goals
            num_epics: Number of epics to generate (default: 3)
        
        Returns:
            List of Epic objects
        """
        prompt = self._build_epic_planning_prompt(context, num_epics)
        
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
            epics = self._parse_epic_response(result, context)
            
            return epics
            
        except Exception as e:
            print(f"Error in epic planning: {e}")
            return []
    
    def refine_epic(
        self,
        epic: Epic,
        feedback: str,
        context: PlanningContext
    ) -> Epic:
        """
        Refine an existing epic based on feedback.
        
        Args:
            epic: Epic to refine
            feedback: Feedback or requirements for refinement
            context: Planning context
        
        Returns:
            Refined Epic object
        """
        prompt = f"""
        Refine the following epic based on the feedback provided.
        
        **Current Epic:**
        Title: {epic.title}
        Description: {epic.description}
        Business Value: {epic.business_value}
        Priority: {epic.priority.value}
        
        **Feedback:**
        {feedback}
        
        **Department Context:**
        {context.department.name}
        Strategic Goals: {', '.join(context.department.strategic_goals)}
        
        Provide a refined version that addresses the feedback while maintaining
        alignment with strategic goals. Return as JSON with the same structure.
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
            refined_epics = self._parse_epic_response(result, context)
            
            return refined_epics[0] if refined_epics else epic
            
        except Exception as e:
            print(f"Error refining epic: {e}")
            return epic
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Epic Planning Agent."""
        return """You are an expert Epic Planning Agent specializing in strategic 
planning and product management. Your role is to:

1. Analyze departmental strategic goals and break them into actionable epics
2. Ensure each epic has clear business value and measurable outcomes
3. Prioritize epics based on strategic impact and dependencies
4. Consider resource constraints and team capacity
5. Align epics with company-wide objectives

Guidelines:
- Each epic should be substantial but achievable within 1-6 months
- Focus on customer value and business outcomes
- Include realistic effort estimates
- Identify dependencies early
- Use clear, non-technical language for business value
- Ensure epics are SMART (Specific, Measurable, Achievable, Relevant, Time-bound)

Always return responses in valid JSON format matching the Epic schema."""
    
    def _build_epic_planning_prompt(
        self,
        context: PlanningContext,
        num_epics: int
    ) -> str:
        """Build the prompt for epic planning."""
        return f"""
Plan {num_epics} strategic epics for the following department context:

**Department:** {context.department.name}
**Team Size:** {context.department.team_size or 'Not specified'}
**Budget:** {context.department.budget or 'Not specified'}

**Strategic Goals:**
{chr(10).join(f'- {goal}' for goal in context.department.strategic_goals)}

**Current Initiatives:**
{chr(10).join(f'- {init}' for init in context.department.current_initiatives) if context.department.current_initiatives else 'None specified'}

**Timeframe:** {context.timeframe.value}

**Focus Areas:**
{chr(10).join(f'- {area}' for area in context.focus_areas) if context.focus_areas else 'None specified'}

**Constraints:**
{chr(10).join(f'- {constraint}' for constraint in context.constraints) if context.constraints else 'None specified'}

**Company-Level OKRs for Alignment:**
{chr(10).join(f'- {okr}' for okr in context.company_okrs) if context.company_okrs else 'None specified'}

Generate {num_epics} epics that:
1. Directly support the strategic goals
2. Are properly scoped for the timeframe
3. Have clear business value
4. Consider team capacity and constraints
5. Align with company-level OKRs

Return as JSON with this structure:
{{
    "epics": [
        {{
            "id": "epic-001",
            "title": "Epic Title",
            "description": "Detailed description",
            "business_value": "Clear business value statement",
            "priority": "high|medium|low|critical",
            "estimated_effort": "X months" or "X person-months",
            "dependencies": ["dependency1", "dependency2"],
            "stakeholders": ["stakeholder1", "stakeholder2"],
            "department": "{context.department.name}",
            "timeframe": "{context.timeframe.value}"
        }}
    ]
}}
"""
    
    def _parse_epic_response(
        self,
        response: Dict[str, Any],
        context: PlanningContext
    ) -> List[Epic]:
        """Parse the LLM response into Epic objects."""
        epics = []
        
        for epic_data in response.get("epics", []):
            try:
                # Map priority string to enum
                priority_str = epic_data.get("priority", "medium").lower()
                priority_map = {
                    "critical": Priority.CRITICAL,
                    "high": Priority.HIGH,
                    "medium": Priority.MEDIUM,
                    "low": Priority.LOW
                }
                priority = priority_map.get(priority_str, Priority.MEDIUM)
                
                # Map timeframe string to enum
                timeframe_str = epic_data.get("timeframe", "").upper()
                timeframe = None
                try:
                    timeframe = TimeFrame[timeframe_str] if timeframe_str else None
                except KeyError:
                    timeframe = context.timeframe
                
                epic = Epic(
                    id=epic_data.get("id", f"epic-{len(epics) + 1:03d}"),
                    title=epic_data["title"],
                    description=epic_data["description"],
                    business_value=epic_data["business_value"],
                    priority=priority,
                    estimated_effort=epic_data.get("estimated_effort"),
                    dependencies=epic_data.get("dependencies", []),
                    stakeholders=epic_data.get("stakeholders", []),
                    department=epic_data.get("department", context.department.name),
                    timeframe=timeframe
                )
                
                epics.append(epic)
                
            except KeyError as e:
                print(f"Missing required field in epic data: {e}")
                continue
            except Exception as e:
                print(f"Error parsing epic: {e}")
                continue
        
        return epics
    
    def analyze_dependencies(self, epics: List[Epic]) -> Dict[str, List[str]]:
        """
        Analyze dependencies between epics.
        
        Args:
            epics: List of epics to analyze
        
        Returns:
            Dictionary mapping epic IDs to their dependent epic IDs
        """
        epic_titles = {epic.id: epic.title for epic in epics}
        dependency_map = {}
        
        for epic in epics:
            dependencies = []
            for dep in epic.dependencies:
                # Try to match dependency to other epic titles
                for epic_id, title in epic_titles.items():
                    if dep.lower() in title.lower() or title.lower() in dep.lower():
                        dependencies.append(epic_id)
                        break
            
            if dependencies:
                dependency_map[epic.id] = dependencies
        
        return dependency_map
    
    def suggest_prioritization(
        self,
        epics: List[Epic],
        context: PlanningContext
    ) -> List[Epic]:
        """
        Suggest optimal prioritization order for epics.
        
        Args:
            epics: List of epics to prioritize
            context: Planning context
        
        Returns:
            Sorted list of epics by suggested priority
        """
        # Analyze dependencies
        deps = self.analyze_dependencies(epics)
        
        # Score each epic
        scored_epics = []
        for epic in epics:
            score = 0
            
            # Priority weight
            priority_weights = {
                Priority.CRITICAL: 100,
                Priority.HIGH: 75,
                Priority.MEDIUM: 50,
                Priority.LOW: 25
            }
            score += priority_weights.get(epic.priority, 50)
            
            # Dependency penalty (epics with dependencies should come later)
            if epic.id in deps:
                score -= len(deps[epic.id]) * 10
            
            # Being a dependency for others increases priority
            for other_deps in deps.values():
                if epic.id in other_deps:
                    score += 15
            
            scored_epics.append((score, epic))
        
        # Sort by score descending
        scored_epics.sort(key=lambda x: x[0], reverse=True)
        
        return [epic for _, epic in scored_epics]
