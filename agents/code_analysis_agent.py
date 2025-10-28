"""
Code Analysis Agent - Analyzes Python code and extracts structural information.
"""

import ast
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from data_models import (
    CodeAnalysisResult, CodeComponent, Relationship,
    ComponentType, RelationshipType
)


class CodeAnalysisAgent:
    """Analyzes Python code to extract structural information for diagram generation."""

    def __init__(self):
        self.name = "CodeAnalysisAgent"
        self.components: List[CodeComponent] = []
        self.imports_graph: Dict[str, List[str]] = {}

    def analyze_file(self, file_path: str) -> CodeAnalysisResult:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            self._process_ast_tree(tree, file_path)

            return CodeAnalysisResult(
                metadata={
                    "file_path": file_path,
                    "lines_of_code": len(content.splitlines()),
                    "analysis_timestamp": self._get_timestamp()
                },
                components=self.components.copy(),
                file_count=1,
                language="python",
                complexity_score=self._calculate_complexity()
            )

        except Exception as e:
            return CodeAnalysisResult(
                metadata={"error": str(e), "file_path": file_path},
                language="python",
                complexity_score=0.0
            )

    def analyze_repository(self, repo_path: str) -> CodeAnalysisResult:
        """Analyze an entire Python repository."""
        python_files = self._find_python_files(repo_path)
        total_components = []

        for file_path in python_files:
            result = self.analyze_file(file_path)
            total_components.extend(result.components)

        return CodeAnalysisResult(
            metadata={
                "repository_path": repo_path,
                "files_analyzed": len(python_files),
                "analysis_timestamp": self._get_timestamp()
            },
            components=total_components,
            file_count=len(python_files),
            language="python",
            complexity_score=self._calculate_repo_complexity(total_components)
        )

    def _find_python_files(self, repo_path: str) -> List[str]:
        """Find all Python files in the repository."""
        python_files = []
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]

            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files

    def _process_ast_tree(self, tree: ast.AST, file_path: str):
        """Process AST tree to extract components and relationships."""
        visitor = CodeVisitor(file_path)
        visitor.visit(tree)
        self.components.extend(visitor.components)

    def _calculate_complexity(self) -> float:
        """Calculate complexity score based on components and relationships."""
        if not self.components:
            return 0.0

        total_relationships = sum(len(comp.relationships) for comp in self.components)
        component_count = len(self.components)

        # Simple complexity heuristic
        if component_count == 0:
            return 0.0

        complexity = (total_relationships / component_count) * 0.3 + (component_count / 10) * 0.7
        return min(complexity, 1.0)  # Normalize to 0-1

    def _calculate_repo_complexity(self, components: List[CodeComponent]) -> float:
        """Calculate complexity for entire repository."""
        if not components:
            return 0.0

        total_relationships = sum(len(comp.relationships) for comp in components)
        component_count = len(components)

        if component_count == 0:
            return 0.0

        complexity = (total_relationships / component_count) * 0.3 + (component_count / 50) * 0.7
        return min(complexity, 1.0)

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


class CodeVisitor(ast.NodeVisitor):
    """AST visitor to extract code components and relationships."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.components: List[CodeComponent] = []
        self.current_class: Optional[str] = None
        self.imports: List[str] = []

    def visit_Import(self, node: ast.Import):
        """Handle import statements."""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Handle from-import statements."""
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        """Handle class definitions."""
        # Extract inheritance relationships
        relationships = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                relationships.append(Relationship(
                    source=node.name,
                    target=base.id,
                    type=RelationshipType.INHERITANCE,
                    description=f"{node.name} inherits from {base.id}"
                ))

        # Extract methods and properties
        methods = []
        properties = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append(item.name)
                # Check if it's a property
                for decorator in item.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'property':
                        properties.append(item.name)

        component = CodeComponent(
            name=node.name,
            type=ComponentType.CLASS,
            file_path=self.file_path,
            line_number=node.lineno,
            methods=methods,
            properties=properties,
            imports=self.imports.copy(),
            relationships=relationships,
            metadata={
                "docstring": ast.get_docstring(node),
                "is_abstract": any(
                    isinstance(item, ast.FunctionDef) and
                    any(isinstance(d, ast.Name) and d.id == 'abstractmethod' for d in item.decorator_list)
                    for item in node.body
                )
            }
        )

        self.components.append(component)

        # Visit child nodes
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Handle function definitions."""
        if self.current_class is None:  # It's a standalone function
            # Analyze function calls to detect dependencies
            relationships = self._analyze_function_dependencies(node)

            component = CodeComponent(
                name=node.name,
                type=ComponentType.FUNCTION,
                file_path=self.file_path,
                line_number=node.lineno,
                imports=self.imports.copy(),
                relationships=relationships,
                metadata={
                    "docstring": ast.get_docstring(node),
                    "arguments": [arg.arg for arg in node.args.args]
                }
            )

            self.components.append(component)

        self.generic_visit(node)

    def _analyze_function_dependencies(self, node: ast.FunctionDef) -> List[Relationship]:
        """Analyze function to find dependencies and method calls."""
        relationships = []

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    # Function call
                    func_name = child.func.id
                    if func_name != node.name:  # Don't count self-calls
                        relationships.append(Relationship(
                            source=node.name,
                            target=func_name,
                            type=RelationshipType.METHOD_CALL,
                            description=f"{node.name} calls {func_name}"
                        ))
                elif isinstance(child.func, ast.Attribute):
                    # Method call on object
                    if isinstance(child.func.value, ast.Name):
                        relationships.append(Relationship(
                            source=node.name,
                            target=child.func.attr,
                            type=RelationshipType.METHOD_CALL,
                            description=f"{node.name} calls {child.func.value.id}.{child.func.attr}"
                        ))

        return relationships

    def visit_Assign(self, node: ast.Assign):
        """Handle variable assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                component = CodeComponent(
                    name=target.id,
                    type=ComponentType.VARIABLE,
                    file_path=self.file_path,
                    line_number=node.lineno,
                    imports=self.imports.copy(),
                    metadata={"type": "variable"}
                )
                self.components.append(component)

        self.generic_visit(node)