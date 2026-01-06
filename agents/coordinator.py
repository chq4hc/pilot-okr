"""
Agent Coordinator - Microsoft Swarm Implementation

This module provides coordination between multiple agents (Epic Planning and OKR Planning)
to execute complete planning sessions with context sharing and handoffs.
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import (
    Epic, Objective, PlanningContext, PlanningResult, Department, TimeFrame
)
from .epic_agent import EpicPlanningAgent
from .okr_agent import OKRPlanningAgent


class AgentCoordinator:
    """
    Coordinates multi-agent planning workflow following Microsoft Swarm patterns.
    
    This coordinator manages the handoff between Epic Planning and OKR Planning agents,
    maintains context, and ensures proper sequencing of agent activities.
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the Agent Coordinator.
        
        Args:
            api_key: OpenAI API key (if None, reads from environment)
            model: OpenAI model to use for agents
            temperature: Creativity level (0.0-1.0)
        """
        self.config = config    
        self.epic_agent = EpicPlanningAgent(
            config=self.config
        )
        self.okr_agent = OKRPlanningAgent(
            config=self.config
        )
        self.context_history: List[Dict[str, Any]] = []
    
    def execute_planning_session(
        self,
        context: PlanningContext,
        num_epics: int = 3,
        num_objectives_per_epic: int = 3,
        auto_refine: bool = True
    ) -> PlanningResult:
        """
        Execute a complete planning session with multiple agents.
        
        This method orchestrates the full workflow:
        1. Epic Planning Agent generates epics
        2. OKR Planning Agent creates objectives for each epic
        3. Optional refinement based on validation
        
        Args:
            context: Planning context with department info
            num_epics: Number of epics to generate
            num_objectives_per_epic: Number of objectives per epic
            auto_refine: Whether to automatically refine based on validation
        
        Returns:
            PlanningResult with all epics and OKRs
        """
        print(f"🚀 Starting planning session for {context.department.name}")
        print(f"   Timeframe: {context.timeframe.value}")
        
        # Step 1: Generate epics
        print(f"\n📋 Step 1: Generating {num_epics} epics...")
        epics = self.epic_agent.plan_epics(context, num_epics)
        print(f"   ✓ Generated {len(epics)} epics")
        
        # Step 2: Prioritize epics
        print(f"\n🎯 Step 2: Prioritizing epics...")
        epics = self.epic_agent.suggest_prioritization(epics, context)
        
        # Step 3: Generate OKRs for each epic
        print(f"\n📊 Step 3: Generating OKRs for each epic...")
        for i, epic in enumerate(epics, 1):
            print(f"   Processing Epic {i}/{len(epics)}: {epic.title}")
            
            objectives = self.okr_agent.generate_okrs_for_epic(
                epic,
                context,
                num_objectives_per_epic
            )
            
            # Validate and optionally refine
            if auto_refine:
                objectives = self._validate_and_refine_objectives(
                    objectives,
                    epic,
                    context
                )
            
            epic.objectives = objectives
            print(f"   ✓ Added {len(objectives)} objectives with {sum(len(obj.key_results) for obj in objectives)} key results")
        
        # Step 4: Build result
        result = PlanningResult(
            epics=epics,
            context=context,
            created_at=datetime.now(),
            agent_metadata={
                "epic_agent": self.epic_agent.agent_name,
                "okr_agent": self.okr_agent.agent_name,
                "num_epics": len(epics),
                "total_objectives": sum(len(epic.objectives) for epic in epics),
                "total_key_results": sum(
                    len(obj.key_results) 
                    for epic in epics 
                    for obj in epic.objectives
                )
            }
        )
        
        print(f"\n✅ Planning session complete!")
        print(f"   Total: {len(epics)} epics, {result.agent_metadata['total_objectives']} objectives, {result.agent_metadata['total_key_results']} key results")
        
        return result
    
    def refine_with_feedback(
        self,
        result: PlanningResult,
        epic_id: str,
        feedback: str
    ) -> PlanningResult:
        """
        Refine a specific epic and its OKRs based on feedback.
        
        Args:
            result: Current planning result
            epic_id: ID of epic to refine
            feedback: Feedback for refinement
        
        Returns:
            Updated PlanningResult
        """
        # Find the epic
        epic_index = None
        for i, epic in enumerate(result.epics):
            if epic.id == epic_id:
                epic_index = i
                break
        
        if epic_index is None:
            print(f"Epic {epic_id} not found")
            return result
        
        epic = result.epics[epic_index]
        
        # Refine the epic
        print(f"🔄 Refining epic: {epic.title}")
        refined_epic = self.epic_agent.refine_epic(epic, feedback, result.context)
        
        # Regenerate OKRs for refined epic
        print(f"📊 Regenerating OKRs...")
        objectives = self.okr_agent.generate_okrs_for_epic(
            refined_epic,
            result.context,
            len(epic.objectives) or 3
        )
        refined_epic.objectives = objectives
        
        # Update result
        result.epics[epic_index] = refined_epic
        
        print(f"✓ Refinement complete")
        return result
    
    def _validate_and_refine_objectives(
        self,
        objectives: List[Objective],
        epic: Epic,
        context: PlanningContext
    ) -> List[Objective]:
        """Validate objectives and refine if needed."""
        refined_objectives = []
        
        for obj in objectives:
            validation = self.okr_agent.validate_key_results(obj.key_results)
            
            if validation["score"] >= 80:
                refined_objectives.append(obj)
            else:
                # Build feedback from validation issues
                feedback = "Issues found:\n"
                feedback += "\n".join(f"- {issue}" for issue in validation["issues"])
                if validation["suggestions"]:
                    feedback += "\n\nSuggestions:\n"
                    feedback += "\n".join(f"- {sug}" for sug in validation["suggestions"])
                
                print(f"      ⚠️  Validation score: {validation['score']}/100 - Refining...")
                refined_obj = self.okr_agent.refine_objective(obj, feedback, epic)
                refined_objectives.append(refined_obj)
        
        return refined_objectives
    
    def export_to_file(
        self,
        result: PlanningResult,
        output_path: str,
        format: str = "json"
    ):
        """
        Export planning result to file.
        
        Args:
            result: Planning result to export
            output_path: Output file path
            format: Export format ("json" or "markdown")
        """
        if format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result.to_json())
        elif format == "markdown":
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result.to_markdown())
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        print(f"✓ Exported to {output_path}")


class PlanningSession:
    """
    High-level interface for conducting planning sessions.
    
    This class provides a simple API for common planning workflows while
    hiding the complexity of agent coordination.
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a Planning Session.
        
        Args:
            api_key: OpenAI API key (if None, reads from environment)
            model: OpenAI model to use
        """
        self.config = config 
        self.coordinator = AgentCoordinator(config=self.config)
        self.current_result: Optional[PlanningResult] = None
    
    def start(
        self,
        department_name: str,
        strategic_goals: List[str],
        timeframe: TimeFrame,
        team_size: Optional[int] = None,
        budget: Optional[float] = None,
        focus_areas: Optional[List[str]] = None,
        constraints: Optional[List[str]] = None,
        company_okrs: Optional[List[str]] = None,
        num_epics: int = 3,
        num_objectives_per_epic: int = 3
    ) -> PlanningResult:
        """
        Start a new planning session.
        
        Args:
            department_name: Name of the department
            strategic_goals: List of strategic goals
            timeframe: Planning timeframe (Q1, Q2, H1, etc.)
            team_size: Number of team members
            budget: Available budget
            focus_areas: Specific focus areas
            constraints: Known constraints
            company_okrs: Company-level OKRs for alignment
            num_epics: Number of epics to generate
            num_objectives_per_epic: Number of objectives per epic
        
        Returns:
            PlanningResult with epics and OKRs
        """
        # Build context
        department = Department(
            name=department_name,
            strategic_goals=strategic_goals,
            team_size=team_size,
            budget=budget
        )
        
        context = PlanningContext(
            department=department,
            timeframe=timeframe,
            focus_areas=focus_areas or [],
            constraints=constraints or [],
            company_okrs=company_okrs or []
        )
        
        # Execute planning
        self.current_result = self.coordinator.execute_planning_session(
            context=context,
            num_epics=num_epics,
            num_objectives_per_epic=num_objectives_per_epic
        )
        
        return self.current_result
    
    def refine_epic(self, epic_id: str, feedback: str) -> PlanningResult:
        """
        Refine a specific epic based on feedback.
        
        Args:
            epic_id: ID of epic to refine
            feedback: Refinement feedback
        
        Returns:
            Updated PlanningResult
        """
        if self.current_result is None:
            raise ValueError("No active planning session. Call start() first.")
        
        self.current_result = self.coordinator.refine_with_feedback(
            self.current_result,
            epic_id,
            feedback
        )
        
        return self.current_result
    
    def export(self, output_path: str, format: str = "json"):
        """
        Export current planning result to file.
        
        Args:
            output_path: Output file path
            format: Export format ("json" or "markdown")
        """
        if self.current_result is None:
            raise ValueError("No planning result to export. Call start() first.")
        
        self.coordinator.export_to_file(self.current_result, output_path, format)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the current planning result."""
        if self.current_result is None:
            return {"status": "No active session"}
        
        return {
            "department": self.current_result.context.department.name,
            "timeframe": self.current_result.context.timeframe.value,
            "num_epics": len(self.current_result.epics),
            "num_objectives": sum(len(epic.objectives) for epic in self.current_result.epics),
            "num_key_results": sum(
                len(obj.key_results)
                for epic in self.current_result.epics
                for obj in epic.objectives
            ),
            "epics": [
                {
                    "id": epic.id,
                    "title": epic.title,
                    "priority": epic.priority.value,
                    "num_objectives": len(epic.objectives),
                    "progress": f"{epic.overall_progress:.1f}%"
                }
                for epic in self.current_result.epics
            ]
        }
    
    def print_summary(self):
        """Print a formatted summary of the current planning result."""
        summary = self.get_summary()
        
        if summary.get("status") == "No active session":
            print("No active planning session")
            return
        
        print(f"\n{'='*60}")
        print(f"Planning Summary: {summary['department']}")
        print(f"{'='*60}")
        print(f"Timeframe: {summary['timeframe']}")
        print(f"Total Epics: {summary['num_epics']}")
        print(f"Total Objectives: {summary['num_objectives']}")
        print(f"Total Key Results: {summary['num_key_results']}")
        print(f"\nEpics:")
        
        for epic in summary['epics']:
            print(f"\n  [{epic['priority'].upper()}] {epic['title']}")
            print(f"  ID: {epic['id']} | Objectives: {epic['num_objectives']} | Progress: {epic['progress']}")
        
        print(f"\n{'='*60}\n")
