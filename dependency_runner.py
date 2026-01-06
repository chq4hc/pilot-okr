"""
Run all dependency analysis and visualization tools.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dependency_analyzer import main as run_analyzer
from dependency_visualizer import save_dependency_report, generate_ascii_tree


def main():
    print("🚀 Running Complete Dependency Analysis\n")
    
    # Run main analyzer
    print("="*80)
    print("PART 1: Detailed Analysis")
    print("="*80)
    run_analyzer()
    
    # Generate visual reports
    print("\n" + "="*80)
    print("PART 2: Visual Reports")
    print("="*80)
    save_dependency_report("DEPENDENCIES.md")
    
    print("\n✅ Analysis complete! Check DEPENDENCIES.md for full report.")


if __name__ == "__main__":
    main()