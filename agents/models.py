"""
Data Models for Multi-Agent Epic and OKR Planning System

This module defines the core data structures used across the multi-agent planning
system for Epics and OKRs. All models use Pydantic v2 for validation.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class Priority(str, Enum):
    """Priority levels for epics and objectives"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TimeFrame(str, Enum):
    """Standard time frames for planning"""
    Q1 = "Q1"
    Q2 = "Q2"
    Q3 = "Q3"
    Q4 = "Q4"
    H1 = "H1"
    H2 = "H2"
    ANNUAL = "Annual"


class Department(BaseModel):
    """Department information for strategic alignment"""
    name: str = Field(..., description="Department name")
    strategic_goals: List[str] = Field(
        default_factory=list,
        description="High-level strategic goals for the department"
    )
    team_size: Optional[int] = Field(None, description="Number of team members")
    budget: Optional[float] = Field(None, description="Available budget")
    current_initiatives: List[str] = Field(
        default_factory=list,
        description="Ongoing initiatives or projects"
    )


class KeyResult(BaseModel):
    """Key Result - measurable outcome for an Objective"""
    id: str = Field(..., description="Unique identifier")
    description: str = Field(..., description="What will be measured")
    metric: str = Field(..., description="The specific metric (e.g., 'Number of users', '% uptime')")
    baseline: float = Field(..., description="Starting value")
    target: float = Field(..., description="Target value to achieve")
    current: float = Field(0.0, description="Current progress value")
    unit: str = Field(..., description="Unit of measurement (e.g., 'users', '%', 'days')")
    owner: Optional[str] = Field(None, description="Person responsible")
    due_date: Optional[str] = Field(None, description="Target completion date")
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress as a percentage"""
        if self.target == self.baseline:
            return 100.0 if self.current >= self.target else 0.0
        return min(100.0, max(0.0, ((self.current - self.baseline) / (self.target - self.baseline)) * 100))


class Objective(BaseModel):
    """Objective - qualitative goal with measurable Key Results"""
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Clear, inspiring objective statement")
    description: str = Field(..., description="Detailed explanation of the objective")
    key_results: List[KeyResult] = Field(
        default_factory=list,
        description="Measurable outcomes (2-5 recommended)"
    )
    priority: Priority = Field(Priority.MEDIUM, description="Priority level")
    owner: Optional[str] = Field(None, description="Person accountable for this objective")
    timeframe: Optional[TimeFrame] = Field(None, description="Target timeframe")
    epic_id: Optional[str] = Field(None, description="Associated epic identifier")
    
    @property
    def overall_progress(self) -> float:
        """Calculate overall progress across all key results"""
        if not self.key_results:
            return 0.0
        return sum(kr.progress_percentage for kr in self.key_results) / len(self.key_results)


class Epic(BaseModel):
    """Epic - large body of work with multiple objectives"""
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Epic title")
    description: str = Field(..., description="Comprehensive description of the epic")
    business_value: str = Field(..., description="Expected business value and impact")
    objectives: List[Objective] = Field(
        default_factory=list,
        description="Related objectives (OKRs)"
    )
    priority: Priority = Field(Priority.MEDIUM, description="Priority level")
    estimated_effort: Optional[str] = Field(
        None,
        description="Estimated effort (e.g., '3 months', '5 person-months')"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="Dependencies on other epics or systems"
    )
    stakeholders: List[str] = Field(
        default_factory=list,
        description="Key stakeholders"
    )
    department: Optional[str] = Field(None, description="Owning department")
    timeframe: Optional[TimeFrame] = Field(None, description="Target timeframe")
    
    @property
    def overall_progress(self) -> float:
        """Calculate overall progress across all objectives"""
        if not self.objectives:
            return 0.0
        return sum(obj.overall_progress for obj in self.objectives) / len(self.objectives)


class PlanningContext(BaseModel):
    """Context information for the planning session"""
    department: Department = Field(..., description="Department information")
    timeframe: TimeFrame = Field(..., description="Planning timeframe")
    focus_areas: List[str] = Field(
        default_factory=list,
        description="Specific focus areas or themes"
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="Known constraints or limitations"
    )
    company_okrs: List[str] = Field(
        default_factory=list,
        description="Company-level OKRs for alignment"
    )
    additional_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Any additional context information"
    )


class PlanningResult(BaseModel):
    """Result of a complete planning session"""
    epics: List[Epic] = Field(default_factory=list, description="Generated epics")
    context: PlanningContext = Field(..., description="Planning context used")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    agent_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata from agent execution"
    )
    
    def to_json(self) -> str:
        """Export to JSON string"""
        return self.model_dump_json(indent=2)
    
    def to_markdown(self) -> str:
        """Export to markdown format"""
        lines = [
            f"# Planning Results - {self.context.department.name}",
            f"\n**Timeframe:** {self.context.timeframe.value}",
            f"\n**Generated:** {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n## Strategic Goals",
        ]
        
        for goal in self.context.department.strategic_goals:
            lines.append(f"- {goal}")
        
        lines.append("\n## Epics\n")
        
        for epic in self.epics:
            lines.extend([
                f"### {epic.title}",
                f"\n**Priority:** {epic.priority.value.upper()}",
                f"\n**Description:** {epic.description}",
                f"\n**Business Value:** {epic.business_value}",
                f"\n**Estimated Effort:** {epic.estimated_effort or 'TBD'}",
                f"\n**Progress:** {epic.overall_progress:.1f}%",
            ])
            
            if epic.dependencies:
                lines.append(f"\n**Dependencies:** {', '.join(epic.dependencies)}")
            
            if epic.objectives:
                lines.append("\n#### Objectives\n")
                for obj in epic.objectives:
                    lines.extend([
                        f"**{obj.title}**",
                        f"\n- Priority: {obj.priority.value}",
                        f"- Progress: {obj.overall_progress:.1f}%",
                        f"- Owner: {obj.owner or 'TBD'}",
                    ])
                    
                    if obj.key_results:
                        lines.append("\nKey Results:")
                        for kr in obj.key_results:
                            lines.append(
                                f"- {kr.description}: {kr.current}/{kr.target} {kr.unit} "
                                f"({kr.progress_percentage:.1f}%)"
                            )
                    lines.append("")
            
            lines.append("\n---\n")
        
        return "\n".join(lines)
