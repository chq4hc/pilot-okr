"""
Advanced Agent Usage Example - Direct Agent Interaction

This example demonstrates advanced usage patterns including:
- Direct agent instantiation and control
- Custom context building
- Manual agent coordination
- Validation and refinement loops
- Custom metrics and analysis
"""

import os
from agents import (
    EpicPlanningAgent,
    OKRPlanningAgent,
    Department,
    PlanningContext,
    TimeFrame,
    Priority
)


def advanced_epic_planning_example():
    """Demonstrate advanced epic planning with custom controls."""
    print("\n" + "="*60)
    print("Advanced Epic Planning Example")
    print("="*60)
    
    # Initialize agent
    api_key = os.getenv("OPENAI_API_KEY")
    epic_agent = EpicPlanningAgent(
        api_key=api_key,
        model="gpt-4o",
        temperature=0.8  # Higher temperature for more creative epics
    )
    
    # Build custom context
    department = Department(
        name="Data Science",
        strategic_goals=[
            "Build ML models for customer churn prediction",
            "Implement real-time recommendation engine",
            "Establish data governance framework"
        ],
        team_size=12,
        budget=750000.0,
        current_initiatives=["Customer segmentation project", "Data lake migration"]
    )
    
    context = PlanningContext(
        department=department,
        timeframe=TimeFrame.H2,
        focus_areas=[
            "Machine Learning",
            "Data Infrastructure",
            "Data Quality"
        ],
        constraints=[
            "Must use existing AWS infrastructure",
            "GDPR compliance required",
            "Limited ML engineering resources"
        ],
        company_okrs=[
            "Increase customer retention by 15%",
            "Reduce operational costs by 20%"
        ]
    )
    
    # Generate epics
    print("\n🤖 Generating epics with Epic Planning Agent...")
    epics = epic_agent.plan_epics(context, num_epics=4)
    
    # Analyze dependencies
    print("\n🔍 Analyzing epic dependencies...")
    dependencies = epic_agent.analyze_dependencies(epics)
    if dependencies:
        print("Dependencies found:")
        for epic_id, deps in dependencies.items():
            epic = next(e for e in epics if e.id == epic_id)
            print(f"  {epic.title} depends on: {deps}")
    
    # Get prioritized order
    print("\n🎯 Suggested prioritization:")
    prioritized_epics = epic_agent.suggest_prioritization(epics, context)
    for i, epic in enumerate(prioritized_epics, 1):
        print(f"  {i}. [{epic.priority.value.upper()}] {epic.title}")
    
    # Refine the first epic
    print("\n🔄 Refining top priority epic...")
    feedback = """
    Please enhance this epic to:
    1. Include specific ML model performance metrics
    2. Add monitoring and MLOps considerations
    3. Consider model explainability requirements
    4. Include cost optimization strategies
    """
    refined_epic = epic_agent.refine_epic(prioritized_epics[0], feedback, context)
    print(f"✓ Refined: {refined_epic.title}")
    print(f"  Updated description: {refined_epic.description[:100]}...")
    
    return prioritized_epics


def advanced_okr_planning_example(epics):
    """Demonstrate advanced OKR planning with validation."""
    print("\n" + "="*60)
    print("Advanced OKR Planning Example")
    print("="*60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    okr_agent = OKRPlanningAgent(
        api_key=api_key,
        model="gpt-4o",
        temperature=0.6  # Slightly lower for more precise metrics
    )
    
    # Use the first epic
    epic = epics[0]
    
    context = PlanningContext(
        department=Department(
            name="Data Science",
            strategic_goals=["ML-driven customer insights"]
        ),
        timeframe=epic.timeframe or TimeFrame.Q2
    )
    
    # Generate OKRs
    print(f"\n📊 Generating OKRs for: {epic.title}")
    objectives = okr_agent.generate_okrs_for_epic(epic, context, num_objectives=3)
    
    # Validate each objective
    print("\n✅ Validating OKRs...")
    for i, objective in enumerate(objectives, 1):
        print(f"\nObjective {i}: {objective.title}")
        
        validation = okr_agent.validate_key_results(objective.key_results)
        print(f"  Validation Score: {validation['score']}/100")
        
        if validation['issues']:
            print("  ⚠️  Issues:")
            for issue in validation['issues']:
                print(f"    - {issue}")
        
        if validation['suggestions']:
            print("  💡 Suggestions:")
            for suggestion in validation['suggestions']:
                print(f"    - {suggestion}")
        
        # Refine if quality is low
        if validation['score'] < 80:
            print(f"  🔄 Refining objective {i} due to low quality score...")
            feedback = "\n".join(validation['issues'] + validation['suggestions'])
            refined_obj = okr_agent.refine_objective(objective, feedback, epic)
            
            # Re-validate
            new_validation = okr_agent.validate_key_results(refined_obj.key_results)
            print(f"  ✓ New validation score: {new_validation['score']}/100")
            objectives[i-1] = refined_obj
    
    # Calculate health for each objective
    print("\n🏥 Objective Health Assessment:")
    for objective in objectives:
        health = okr_agent.calculate_objective_health(objective)
        status_emoji = {
            "on-track": "🟢",
            "at-risk": "🟡",
            "critical": "🔴",
            "unknown": "⚪"
        }
        print(f"  {status_emoji.get(health['status'], '⚪')} {objective.title}")
        print(f"     Status: {health['status']} | Score: {health['score']:.1f}%")
        print(f"     {health['message']}")
    
    # Suggest metrics for a new objective
    print("\n💡 Metric Suggestions for Custom Objective:")
    custom_objective = "Improve data quality and accuracy"
    suggested_metrics = okr_agent.suggest_metrics(custom_objective)
    print(f"  Objective: \"{custom_objective}\"")
    print("  Suggested metrics:")
    for metric in suggested_metrics:
        print(f"    - {metric}")
    
    return objectives


def custom_coordination_example():
    """Demonstrate manual coordination between agents."""
    print("\n" + "="*60)
    print("Custom Agent Coordination Example")
    print("="*60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Initialize both agents
    epic_agent = EpicPlanningAgent(api_key=api_key)
    okr_agent = OKRPlanningAgent(api_key=api_key)
    
    # Build context
    context = PlanningContext(
        department=Department(
            name="Platform Engineering",
            strategic_goals=[
                "Modernize CI/CD pipeline",
                "Improve deployment frequency"
            ],
            team_size=8
        ),
        timeframe=TimeFrame.Q3
    )
    
    # Step 1: Generate one epic
    print("\n📋 Step 1: Generate epic...")
    epics = epic_agent.plan_epics(context, num_epics=1)
    epic = epics[0]
    print(f"  ✓ Created: {epic.title}")
    
    # Step 2: Generate OKRs for the epic
    print("\n📊 Step 2: Generate OKRs...")
    objectives = okr_agent.generate_okrs_for_epic(epic, context, num_objectives=2)
    print(f"  ✓ Created {len(objectives)} objectives")
    
    # Step 3: Validate OKRs
    print("\n✅ Step 3: Validate OKRs...")
    all_valid = True
    for objective in objectives:
        validation = okr_agent.validate_key_results(objective.key_results)
        if validation['score'] < 70:
            all_valid = False
            print(f"  ⚠️  Low quality objective: {objective.title}")
    
    # Step 4: Refine if needed
    if not all_valid:
        print("\n🔄 Step 4: Refining low-quality OKRs...")
        for i, objective in enumerate(objectives):
            validation = okr_agent.validate_key_results(objective.key_results)
            if validation['score'] < 70:
                feedback = "Improve metric specificity and ensure measurability"
                objectives[i] = okr_agent.refine_objective(objective, feedback, epic)
        print("  ✓ Refinement complete")
    else:
        print("\n✓ Step 4: All OKRs meet quality standards")
    
    # Step 5: Attach OKRs to epic
    epic.objectives = objectives
    print(f"\n✅ Complete! Epic '{epic.title}' has {len(objectives)} objectives with {sum(len(o.key_results) for o in objectives)} key results")
    
    return epic


def main():
    """Run all advanced examples."""
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        return
    
    print("🎯 Advanced Agent Usage Examples")
    print("="*60)
    
    # Example 1: Advanced epic planning
    epics = advanced_epic_planning_example()
    
    # Example 2: Advanced OKR planning with validation
    objectives = advanced_okr_planning_example(epics)
    
    # Example 3: Custom coordination
    custom_epic = custom_coordination_example()
    
    print("\n" + "="*60)
    print("✅ All advanced examples complete!")
    print("="*60)
    
    # Summary
    print("\n📊 Summary:")
    print(f"  - Generated {len(epics)} epics with priority ranking")
    print(f"  - Created and validated {len(objectives)} objectives")
    print(f"  - Demonstrated custom coordination workflow")
    print("\nThese examples show how to:")
    print("  ✓ Fine-tune agent parameters (temperature, model)")
    print("  ✓ Build custom planning contexts")
    print("  ✓ Validate and refine OKRs programmatically")
    print("  ✓ Coordinate agents manually for complex workflows")
    print("  ✓ Analyze dependencies and prioritization")


if __name__ == "__main__":
    main()
