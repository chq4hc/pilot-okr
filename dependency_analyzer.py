"""
Module Dependency Visualization

Analyzes and displays dependencies across agents modules and their relationships.
"""

import os
import ast
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass


@dataclass
class ModuleInfo:
    """Information about a Python module."""
    name: str
    path: Path
    imports: List[str]
    classes: List[str]
    functions: List[str]
    external_deps: Set[str]


class DependencyAnalyzer:
    """Analyze Python module dependencies."""
    
    def __init__(self, root_dir: str = "agents"):
        """Initialize analyzer with root directory."""
        self.root_dir = Path(root_dir).resolve()  # Convert to absolute path
        self.project_root = Path.cwd()  # Store project root for display
        self.modules: Dict[str, ModuleInfo] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
    
    def analyze(self):
        """Analyze all Python files in the directory."""
        print(f"🔍 Analyzing dependencies in: {self.root_dir}")
        print("="*80)
        
        # Find all Python files
        py_files = list(self.root_dir.rglob("*.py"))
        print(f"\nFound {len(py_files)} Python files")
        
        # Analyze each file
        for py_file in py_files:
            if "__pycache__" in str(py_file):
                continue
            
            module_name = self._get_module_name(py_file)
            module_info = self._analyze_file(py_file, module_name)
            self.modules[module_name] = module_info
            
            # Build dependency graph
            for imp in module_info.imports:
                if imp.startswith("agents.") or imp in self.modules:
                    self.dependency_graph[module_name].add(imp)
        
        print(f"✓ Analyzed {len(self.modules)} modules")
    
    def _get_module_name(self, file_path: Path) -> str:
        """Convert file path to module name."""
        try:
            # Get relative path from project root
            rel_path = file_path.relative_to(self.project_root)
        except ValueError:
            # If file is not in project root, use relative to root_dir
            rel_path = file_path.relative_to(self.root_dir.parent)
        
        # Convert path to module name
        module_parts = list(rel_path.parts[:-1]) + [rel_path.stem]
        return ".".join(module_parts)
    
    def _get_display_path(self, file_path: Path) -> str:
        """Get display path relative to project root."""
        try:
            return str(file_path.relative_to(self.project_root))
        except ValueError:
            # If not relative to project root, just use the name
            return str(file_path)
    
    def _analyze_file(self, file_path: Path, module_name: str) -> ModuleInfo:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            imports = []
            classes = []
            functions = []
            external_deps = set()
            
            for node in ast.walk(tree):
                # Extract imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                        if not alias.name.startswith("agents"):
                            external_deps.add(alias.name.split('.')[0])
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        if not node.module.startswith("agents"):
                            external_deps.add(node.module.split('.')[0])
                
                # Extract classes
                elif isinstance(node, ast.ClassDef):
                    if node.col_offset == 0:  # Top-level class
                        classes.append(node.name)
                
                # Extract functions
                elif isinstance(node, ast.FunctionDef):
                    if node.col_offset == 0:  # Top-level function
                        functions.append(node.name)
            
            return ModuleInfo(
                name=module_name,
                path=file_path,
                imports=imports,
                classes=classes,
                functions=functions,
                external_deps=external_deps
            )
        
        except Exception as e:
            print(f"⚠️  Error analyzing {file_path}: {e}")
            return ModuleInfo(module_name, file_path, [], [], [], set())
    
    def display_module_summary(self):
        """Display summary of all modules."""
        print("\n" + "="*80)
        print("📦 MODULE SUMMARY")
        print("="*80)
        
        for module_name, info in sorted(self.modules.items()):
            print(f"\n📄 {module_name}")
            print(f"   Path: {self._get_display_path(info.path)}")
            
            if info.classes:
                print(f"   Classes ({len(info.classes)}): {', '.join(info.classes)}")
            
            if info.functions:
                print(f"   Functions ({len(info.functions)}): {', '.join(info.functions[:5])}")
                if len(info.functions) > 5:
                    print(f"                       + {len(info.functions) - 5} more...")
            
            if info.external_deps:
                print(f"   External Deps: {', '.join(sorted(info.external_deps))}")
    
    def display_dependency_graph(self):
        """Display module dependencies as a graph."""
        print("\n" + "="*80)
        print("🔗 DEPENDENCY GRAPH")
        print("="*80)
        
        for module, deps in sorted(self.dependency_graph.items()):
            if deps:
                print(f"\n{module}")
                for dep in sorted(deps):
                    print(f"  └─→ {dep}")
    
    def display_external_dependencies(self):
        """Display all external package dependencies."""
        print("\n" + "="*80)
        print("📚 EXTERNAL DEPENDENCIES")
        print("="*80)
        
        all_external = set()
        for info in self.modules.values():
            all_external.update(info.external_deps)
        
        # Categorize dependencies
        standard_lib = {'os', 'sys', 'json', 'datetime', 'logging', 'typing', 
                       'pathlib', 'dataclasses', 'enum', 'collections', 'ast'}
        
        third_party = all_external - standard_lib
        
        print("\n🐍 Standard Library:")
        for dep in sorted(standard_lib & all_external):
            print(f"  - {dep}")
        
        print("\n📦 Third-Party Packages:")
        for dep in sorted(third_party):
            # Count modules using this dependency
            count = sum(1 for m in self.modules.values() if dep in m.external_deps)
            print(f"  - {dep} (used in {count} modules)")
    
    def display_dependency_matrix(self):
        """Display dependency matrix showing which modules depend on which."""
        print("\n" + "="*80)
        print("📊 DEPENDENCY MATRIX")
        print("="*80)
        
        # Get all module names (shortened)
        module_names = sorted(self.modules.keys())
        short_names = [m.split('.')[-1] for m in module_names]
        
        # Calculate column width
        max_name_len = max(len(name) for name in short_names) if short_names else 10
        col_width = max(max_name_len + 2, 12)
        
        # Print header
        print("\n" + " " * (col_width + 2), end="")
        for name in short_names:
            print(f"{name[:col_width-2]:^{col_width}}", end="")
        print()
        
        print(" " * (col_width + 2) + "─" * (col_width * len(short_names)))
        
        # Print rows
        for i, module in enumerate(module_names):
            print(f"{short_names[i]:<{col_width}} │", end="")
            
            for j, dep_module in enumerate(module_names):
                if dep_module in self.dependency_graph[module]:
                    print(f"{'  ✓':^{col_width}}", end="")
                else:
                    print(f"{'':^{col_width}}", end="")
            print()
    
    def find_circular_dependencies(self):
        """Find circular dependencies in the module graph."""
        print("\n" + "="*80)
        print("🔄 CIRCULAR DEPENDENCY CHECK")
        print("="*80)
        
        def has_path(start: str, end: str, visited: Set[str]) -> bool:
            """Check if there's a path from start to end."""
            if start == end:
                return True
            if start in visited:
                return False
            
            visited.add(start)
            for neighbor in self.dependency_graph.get(start, set()):
                if has_path(neighbor, end, visited):
                    return True
            return False
        
        circular = []
        modules = list(self.dependency_graph.keys())
        
        for i, module1 in enumerate(modules):
            for module2 in modules[i+1:]:
                if (module2 in self.dependency_graph.get(module1, set()) and
                    has_path(module2, module1, set())):
                    circular.append((module1, module2))
        
        if circular:
            print("\n⚠️  Circular dependencies found:")
            for mod1, mod2 in circular:
                print(f"  - {mod1} ⟷ {mod2}")
        else:
            print("\n✅ No circular dependencies found!")
    
    def display_usage_stats(self):
        """Display statistics about module usage."""
        print("\n" + "="*80)
        print("📈 USAGE STATISTICS")
        print("="*80)
        
        # Count how many modules import each module
        import_count = defaultdict(int)
        for deps in self.dependency_graph.values():
            for dep in deps:
                import_count[dep] += 1
        
        print("\n🔝 Most Imported Modules:")
        sorted_imports = sorted(import_count.items(), key=lambda x: x[1], reverse=True)
        for module, count in sorted_imports[:10]:
            print(f"  {count:2d} imports: {module}")
        
        # Find leaf modules (not imported by anyone)
        all_modules = set(self.modules.keys())
        imported_modules = set(import_count.keys())
        leaf_modules = all_modules - imported_modules
        
        if leaf_modules:
            print("\n🍃 Leaf Modules (not imported by others):")
            for module in sorted(leaf_modules):
                print(f"  - {module}")


def main():
    """Run dependency analysis."""
    print("🔍 Python Module Dependency Analyzer")
    print("="*80)
    
    # Analyze agents package
    analyzer = DependencyAnalyzer("agents")
    analyzer.analyze()
    
    # Display various reports
    analyzer.display_module_summary()
    analyzer.display_dependency_graph()
    analyzer.display_dependency_matrix()
    analyzer.display_external_dependencies()
    analyzer.find_circular_dependencies()
    analyzer.display_usage_stats()
    
    print("\n" + "="*80)
    print("✅ Dependency analysis complete!")
    print("="*80)


if __name__ == "__main__":
    main()