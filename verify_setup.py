"""
Setup Verification Script

Run this script to verify that the multi-agent OKR planning system is properly installed
and configured.
"""

import sys
import os


def check_imports():
    """Check if all required modules can be imported."""
    print("🔍 Checking imports...")
    errors = []
    
    try:
        import openai
        print("  ✓ openai")
    except ImportError:
        errors.append("openai not installed")
        print("  ✗ openai - Not installed")
    
    try:
        import pydantic
        print("  ✓ pydantic")
    except ImportError:
        errors.append("pydantic not installed")
        print("  ✗ pydantic - Not installed")
    
    try:
        from agents import (
            PlanningSession,
            EpicPlanningAgent,
            OKRPlanningAgent,
            AgentCoordinator,
            TimeFrame,
            Department,
            Epic,
            Objective,
            KeyResult
        )
        print("  ✓ agents package")
    except ImportError as e:
        errors.append(f"agents package error: {e}")
        print(f"  ✗ agents package - {e}")
    
    return errors


def check_api_key():
    """Check if OpenAI API key is configured."""
    print("\n🔑 Checking API key...")
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("  ✗ OPENAI_API_KEY not set")
        print("    Set it with: export OPENAI_API_KEY='your-key'")
        return False
    else:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"  ✓ OPENAI_API_KEY is set ({masked_key})")
        return True


def check_file_structure():
    """Check if all required files exist."""
    print("\n📁 Checking file structure...")
    errors = []
    
    required_files = [
        "agents/__init__.py",
        "agents/models.py",
        "agents/epic_agent.py",
        "agents/okr_agent.py",
        "agents/coordinator.py",
        "agents/README.md",
        "agents/examples/__init__.py",
        "agents/examples/planning_session_example.py",
        "agents/examples/advanced_usage.py",
        "agents/examples/README.md",
        "requirements.txt",
        "README.md"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            errors.append(f"Missing file: {file_path}")
            print(f"  ✗ {file_path}")
    
    return errors


def check_existing_modules():
    """Check if existing OKR modules are available."""
    print("\n📦 Checking existing OKR modules...")
    
    try:
        import okr_evaluator
        print("  ✓ okr_evaluator")
    except ImportError:
        print("  ⚠️  okr_evaluator - Not found (optional)")
    
    try:
        import okr_tracker
        print("  ✓ okr_tracker")
    except ImportError:
        print("  ⚠️  okr_tracker - Not found (optional)")
    
    try:
        import okr_utils
        print("  ✓ okr_utils")
    except ImportError:
        print("  ⚠️  okr_utils - Not found (optional)")


def test_basic_functionality():
    """Test basic functionality without making API calls."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from agents import Department, PlanningContext, TimeFrame
        
        # Create a department
        dept = Department(
            name="Test Department",
            strategic_goals=["Goal 1", "Goal 2"],
            team_size=10
        )
        print("  ✓ Can create Department")
        
        # Create planning context
        context = PlanningContext(
            department=dept,
            timeframe=TimeFrame.Q1
        )
        print("  ✓ Can create PlanningContext")
        
        # Check TimeFrame enum
        assert TimeFrame.Q1.value == "Q1"
        print("  ✓ TimeFrame enum works")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Run all verification checks."""
    print("="*60)
    print("🎯 Multi-Agent OKR Planning System - Setup Verification")
    print("="*60)
    
    all_errors = []
    
    # Check imports
    import_errors = check_imports()
    all_errors.extend(import_errors)
    
    # Check API key
    has_api_key = check_api_key()
    
    # Check file structure
    file_errors = check_file_structure()
    all_errors.extend(file_errors)
    
    # Check existing modules
    check_existing_modules()
    
    # Test basic functionality
    if not import_errors:
        test_basic_functionality()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Verification Summary")
    print("="*60)
    
    if all_errors:
        print("\n❌ Issues found:")
        for error in all_errors:
            print(f"  - {error}")
        print("\n🔧 To fix:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Ensure all files are present")
        print("  3. Set OPENAI_API_KEY environment variable")
    else:
        print("\n✅ All checks passed!")
        
        if not has_api_key:
            print("\n⚠️  Note: OPENAI_API_KEY is not set")
            print("  You'll need to set it before running examples:")
            print("  export OPENAI_API_KEY='your-key'")
        
        print("\n🚀 Ready to use!")
        print("\nNext steps:")
        print("  1. Run example: python agents/examples/planning_session_example.py")
        print("  2. Read documentation: agents/README.md")
        print("  3. Check examples guide: agents/examples/README.md")
    
    print("\n" + "="*60)
    
    return 0 if not all_errors else 1


if __name__ == "__main__":
    sys.exit(main())
