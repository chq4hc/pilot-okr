"""
Visual Dependency Graph Generator

Creates a visual diagram of module dependencies using graphviz.
"""

import os
from pathlib import Path
from typing import Dict, Set
from collections import defaultdict


def generate_mermaid_diagram(root_dir: str = "agents") -> str:
    """
    Generate a Mermaid diagram of module dependencies.
    
    Returns:
        Mermaid markdown syntax for the dependency graph
    """
    from dependency_analyzer import DependencyAnalyzer
    
    analyzer = DependencyAnalyzer(root_dir)
    analyzer.analyze()
    
    # Start mermaid diagram
    mermaid = ["```mermaid", "graph TD"]
    
    # Define node styles
    mermaid.append("    classDef core fill:#4CAF50,stroke:#2E7D32,color:#fff")
    mermaid.append("    classDef agent fill:#2196F3,stroke:#1565C0,color:#fff")
    mermaid.append("    classDef example fill:#FF9800,stroke:#E65100,color:#fff")
    mermaid.append("    classDef external fill:#9E9E9E,stroke:#424242,color:#fff")
    
    # Create nodes
    node_ids = {}
    node_counter = 0
    
    for module_name, info in sorted(analyzer.modules.items()):
        node_id = f"M{node_counter}"
        node_counter += 1
        
        # Shorten module name for display
        display_name = module_name.split('.')[-1]
        
        # Determine node class
        if 'agent' in module_name:
            node_class = "agent"
        elif 'example' in module_name:
            node_class = "example"
        elif module_name in ['agents.models', 'agents.coordinator', 'agents.__init__']:
            node_class = "core"
        else:
            node_class = "external"
        
        # Add node with classes
        if info.classes:
            class_list = ", ".join(info.classes[:2])
            if len(info.classes) > 2:
                class_list += "..."
            label = f"{display_name}<br/><small>{class_list}</small>"
        else:
            label = display_name
        
        mermaid.append(f'    {node_id}["{label}"]:::{node_class}')
        node_ids[module_name] = node_id
    
    # Create edges
    for module, deps in sorted(analyzer.dependency_graph.items()):
        if module in node_ids:
            source_id = node_ids[module]
            for dep in sorted(deps):
                if dep in node_ids:
                    target_id = node_ids[dep]
                    mermaid.append(f"    {source_id} --> {target_id}")
    
    mermaid.append("```")
    
    return "\n".join(mermaid)


def generate_ascii_tree(root_dir: str = "agents") -> str:
    """
    Generate an ASCII tree visualization of dependencies.
    
    Returns:
        ASCII art representation of the dependency tree
    """
    from dependency_analyzer import DependencyAnalyzer
    
    analyzer = DependencyAnalyzer(root_dir)
    analyzer.analyze()
    
    output = []
    output.append("\n📂 Module Dependency Tree")
    output.append("="*80)
    
    def print_tree(module: str, prefix: str = "", visited: Set[str] = None):
        """Recursively print dependency tree."""
        if visited is None:
            visited = set()
        
        if module in visited:
            return  # Avoid infinite loops
        
        visited.add(module)
        
        deps = sorted(analyzer.dependency_graph.get(module, set()))
        
        for i, dep in enumerate(deps):
            is_last = (i == len(deps) - 1)
            connector = "└── " if is_last else "├── "
            output.append(f"{prefix}{connector}{dep}")
            
            # Recurse with updated prefix
            new_prefix = prefix + ("    " if is_last else "│   ")
            print_tree(dep, new_prefix, visited.copy())
    
    # Start with root modules (those not imported by others)
    import_count = defaultdict(int)
    for deps in analyzer.dependency_graph.values():
        for dep in deps:
            import_count[dep] += 1
    
    all_modules = set(analyzer.modules.keys())
    imported_modules = set(import_count.keys())
    root_modules = sorted(all_modules - imported_modules)
    
    for root in root_modules:
        output.append(f"\n{root}")
        print_tree(root)
    
    return "\n".join(output)


def save_dependency_report(output_file: str = "DEPENDENCIES.md"):
    """
    Generate and save a comprehensive dependency report.
    """
    from dependency_analyzer import DependencyAnalyzer
    
    analyzer = DependencyAnalyzer("agents")
    analyzer.analyze()
    
    report = []
    report.append("# Module Dependencies Report\n")
    report.append(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    report.append("---\n")
    
    # Overview
    report.append("## Overview\n")
    report.append(f"- **Total Modules**: {len(analyzer.modules)}")
    report.append(f"- **Total Dependencies**: {sum(len(deps) for deps in analyzer.dependency_graph.values())}")
    
    # External dependencies
    all_external = set()
    for info in analyzer.modules.values():
        all_external.update(info.external_deps)
    report.append(f"- **External Packages**: {len(all_external)}\n")
    
    # Module list
    report.append("## Modules\n")
    for module_name, info in sorted(analyzer.modules.items()):
        report.append(f"### `{module_name}`\n")
        report.append(f"**Path**: `{info.path.relative_to(Path.cwd())}`\n")
        
        if info.classes:
            report.append(f"**Classes**: {', '.join(f'`{c}`' for c in info.classes)}\n")
        
        if info.functions:
            funcs = ', '.join(f'`{f}`' for f in info.functions[:5])
            if len(info.functions) > 5:
                funcs += f" (+{len(info.functions)-5} more)"
            report.append(f"**Functions**: {funcs}\n")
        
        deps = analyzer.dependency_graph.get(module_name, set())
        if deps:
            report.append("**Internal Dependencies**:")
            for dep in sorted(deps):
                report.append(f"- `{dep}`")
            report.append("")
        
        if info.external_deps:
            report.append(f"**External Dependencies**: {', '.join(f'`{d}`' for d in sorted(info.external_deps))}\n")
        
        report.append("---\n")
    
    # Dependency graph
    report.append("## Dependency Graph\n")
    report.append(generate_mermaid_diagram())
    report.append("\n")
    
    # ASCII tree
    report.append(generate_ascii_tree())
    report.append("\n")
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✅ Dependency report saved to: {output_file}")


if __name__ == "__main__":
    print("📊 Generating dependency visualizations...\n")
    
    # Generate Mermaid diagram
    print("1. Generating Mermaid diagram...")
    mermaid = generate_mermaid_diagram()
    print("✓ Mermaid diagram generated\n")
    
    # Generate ASCII tree
    print("2. Generating ASCII tree...")
    tree = generate_ascii_tree()
    print(tree)
    
    # Save comprehensive report
    print("\n3. Saving comprehensive report...")
    save_dependency_report()
    
    print("\n✅ All visualizations complete!")