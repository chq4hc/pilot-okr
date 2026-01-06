"""
Planning Session Example - Complete Workflow

This example demonstrates a complete planning session using the multi-agent
system to generate epics and OKRs for a department.
"""

import os
# from agents import PlanningSession, TimeFrame
from ..coordinator import PlanningSession
from ..models import TimeFrame

@dataclass
class LLMConfig:
    """Configuration for LLM API connection."""
    api_key: str = "sk-bgsv-ai-team"
    base_url: str = "https://sx-bgsv-llm.agreeablerock-77e2087d.southeastasia.azurecontainerapps.io/"
    model: str = "azure-gpt-5"
    temperature: float = 1.0
    max_tokens: int = 2000
    timeout: int = 30


def main():
    """Run a complete planning session example."""
    
    # Initialize session with OpenAI API key
    # Make sure to set OPENAI_API_KEY environment variable
    
    print("🎯 Multi-Agent Epic & OKR Planning System")
    print("="*60)
    
    config_ = LLMConfig()
    # Create a planning session
    session = PlanningSession(config=config_)
    
    # Start planning for Engineering department
    result = session.start(
        department_name="Engineering",
        strategic_goals=[
            "Scale platform to support 1 million concurrent users",
            "Improve system reliability and uptime to 99.99%",
            "Reduce technical debt by 30%",
            "Enhance developer productivity and CI/CD pipeline"
        ],
        timeframe=TimeFrame.Q2,
        team_size=25,
        budget=500000.0,
        focus_areas=[
            "Infrastructure scalability",
            "Performance optimization",
            "Code quality",
            "Developer experience"
        ],
        constraints=[
            "Limited hiring budget",
            "Must maintain backwards compatibility",
            "Zero downtime deployments required"
        ],
        company_okrs=[
            "Achieve $10M ARR",
            "Expand to 3 new markets",
            "Reach 95% customer satisfaction"
        ],
        num_epics=3,
        num_objectives_per_epic=3
    )
    
    # Print summary
    print("\n" + "="*60)
    print("Planning Session Complete!")
    print("="*60)
    session.print_summary()
    
    # Export results
    print("\n📄 Exporting results...")
    session.export("planning_result.json", format="json")
    session.export("planning_result.md", format="markdown")
    print("✓ Exported to planning_result.json and planning_result.md")
    
    # Example: Refine an epic based on feedback
    if result.epics:
        print("\n🔄 Example: Refining first epic...")
        epic_id = result.epics[0].id
        feedback = """
        Please adjust this epic to:
        1. Include more specific performance metrics
        2. Add monitoring and observability as key components
        3. Consider cost optimization alongside performance
        """
        
        refined_result = session.refine_epic(epic_id, feedback)
        print(f"✓ Refined epic: {refined_result.epics[0].title}")
        
        # Export refined version
        session.export("planning_result_refined.json", format="json")
        print("✓ Exported refined version")
    
    # Display detailed epic information
    print("\n" + "="*60)
    print("Detailed Epic Information")
    print("="*60)
    
    for i, epic in enumerate(result.epics, 1):
        print(f"\n{'─'*60}")
        print(f"Epic {i}: {epic.title}")
        print(f"{'─'*60}")
        print(f"Priority: {epic.priority.value.upper()}")
        print(f"Estimated Effort: {epic.estimated_effort}")
        print(f"Progress: {epic.overall_progress:.1f}%")
        print(f"\nDescription:")
        print(f"  {epic.description}")
        print(f"\nBusiness Value:")
        print(f"  {epic.business_value}")
        
        if epic.dependencies:
            print(f"\nDependencies:")
            for dep in epic.dependencies:
                print(f"  - {dep}")
        
        if epic.stakeholders:
            print(f"\nStakeholders:")
            for stakeholder in epic.stakeholders:
                print(f"  - {stakeholder}")
        
        print(f"\nObjectives ({len(epic.objectives)}):")
        for j, obj in enumerate(epic.objectives, 1):
            print(f"\n  {j}. {obj.title}")
            print(f"     Priority: {obj.priority.value} | Progress: {obj.overall_progress:.1f}%")
            print(f"     {obj.description}")
            
            print(f"\n     Key Results ({len(obj.key_results)}):")
            for k, kr in enumerate(obj.key_results, 1):
                progress_bar = "█" * int(kr.progress_percentage / 10) + "░" * (10 - int(kr.progress_percentage / 10))
                print(f"       {k}. {kr.description}")
                print(f"          Metric: {kr.metric}")
                print(f"          Target: {kr.baseline} → {kr.target} {kr.unit}")
                print(f"          Progress: [{progress_bar}] {kr.progress_percentage:.1f}%")
                if kr.owner:
                    print(f"          Owner: {kr.owner}")
    
    print("\n" + "="*60)
    print("✅ Planning session example complete!")
    print("="*60)


if __name__ == "__main__":
    main()
