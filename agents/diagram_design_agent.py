"""
Diagram Design Agent - Decides optimal diagram types and layouts.
"""

from typing import List, Dict, Any, Set
from data_models import (
    CodeAnalysisResult, DiagramDesign, CodeComponent,
    DiagramType, LayoutStrategy, ComponentType, RelationshipType
)


class DiagramDesignAgent:
    """Analyzes code structure to determine optimal diagram design."""

    def __init__(self):
        self.name = "DiagramDesignAgent"

    def design_diagram(self, analysis_result: CodeAnalysisResult) -> DiagramDesign:
        """Design the optimal diagram based on code analysis."""
        # Determine diagram type
        diagram_type = self._determine_diagram_type(analysis_result)

        # Determine layout strategy
        layout_strategy = self._determine_layout_strategy(analysis_result, diagram_type)

        # Select components to include
        components_to_include = self._select_components(analysis_result)

        # Create grouping strategy
        grouping_strategy = self._create_grouping_strategy(analysis_result, components_to_include)

        # Set visual settings
        visual_settings = self._create_visual_settings(diagram_type, layout_strategy)

        return DiagramDesign(
            diagram_type=diagram_type,
            layout_strategy=layout_strategy,
            components_to_include=components_to_include,
            grouping_strategy=grouping_strategy,
            visual_settings=visual_settings
        )

    def _determine_diagram_type(self, analysis_result: CodeAnalysisResult) -> DiagramType:
        """Determine the most appropriate diagram type."""
        components = analysis_result.components
        class_count = sum(1 for c in components if c.type == ComponentType.CLASS)
        function_count = sum(1 for c in components if c.type == ComponentType.FUNCTION)
        total_relationships = sum(len(c.relationships) for c in components)

        # Heuristics for diagram type selection
        if class_count > 0:
            if class_count >= 3 or total_relationships > 5:
                return DiagramType.CLASS
            else:
                return DiagramType.ARCHITECTURE
        elif function_count > 2:
            return DiagramType.FLOW
        else:
            return DiagramType.ARCHITECTURE

    def _determine_layout_strategy(self, analysis_result: CodeAnalysisResult,
                                 diagram_type: DiagramType) -> LayoutStrategy:
        """Determine the best layout strategy."""
        components = analysis_result.components
        component_count = len(components)

        if diagram_type == DiagramType.CLASS:
            # For class diagrams, use hierarchical if there's inheritance
            has_inheritance = any(
                r.type == RelationshipType.INHERITANCE
                for comp in components
                for r in comp.relationships
            )
            return LayoutStrategy.HIERARCHICAL if has_inheritance else LayoutStrategy.LAYERED

        elif diagram_type == DiagramType.ARCHITECTURE:
            if component_count > 10:
                return LayoutStrategy.LAYERED
            else:
                return LayoutStrategy.GRID

        elif diagram_type == DiagramType.FLOW:
            return LayoutStrategy.HIERARCHICAL

        else:  # Default fallback
            return LayoutStrategy.LAYERED

    def _select_components(self, analysis_result: CodeAnalysisResult) -> List[str]:
        """Select which components to include in the diagram."""
        components = analysis_result.components

        # Filter out very simple components and prioritize meaningful ones
        selected_components = []

        for comp in components:
            # Include classes always
            if comp.type == ComponentType.CLASS:
                selected_components.append(comp.name)
            # Include functions with relationships or documentation
            elif comp.type == ComponentType.FUNCTION:
                if comp.relationships or comp.metadata.get("docstring"):
                    selected_components.append(comp.name)
            # Include variables that might be important (module-level)
            elif comp.type == ComponentType.VARIABLE:
                if len(comp.name) > 1 and not comp.name.startswith('_'):
                    selected_components.append(comp.name)

        # Limit number of components for readability (Version 2.0 improvement)
        max_components = 15  # Reduced from 20 for better readability
        if len(selected_components) > max_components:
            # Prioritize components with most relationships
            component_scores = {}
            for comp in components:
                if comp.name in selected_components:
                    score = len(comp.relationships)
                    if comp.type == ComponentType.CLASS:
                        score += 15  # Higher bonus for classes
                    elif comp.type == ComponentType.FUNCTION:
                        score += 5   # Small bonus for functions
                    component_scores[comp.name] = score

            selected_components.sort(key=lambda x: component_scores.get(x, 0), reverse=True)
            selected_components = selected_components[:max_components]

        return selected_components

    def _create_grouping_strategy(self, analysis_result: CodeAnalysisResult,
                                components_to_include: List[str]) -> Dict[str, List[str]]:
        """Create grouping strategy for related components."""
        components = {c.name: c for c in analysis_result.components if c.name in components_to_include}
        groups = {}

        # Group classes by inheritance hierarchy
        inheritance_groups = self._group_by_inheritance(components)
        groups.update(inheritance_groups)

        # Group components by file/module
        file_groups = self._group_by_file(components)
        groups.update(file_groups)

        # Group components by functionality (based on naming patterns)
        functional_groups = self._group_by_functionality(components)
        groups.update(functional_groups)

        return groups

    def _group_by_inheritance(self, components: Dict[str, CodeComponent]) -> Dict[str, List[str]]:
        """Group components by inheritance relationships."""
        groups = {}

        for comp in components.values():
            if comp.type == ComponentType.CLASS:
                # Find base classes
                base_classes = []
                for rel in comp.relationships:
                    if rel.type == RelationshipType.INHERITANCE:
                        base_classes.append(rel.target)

                if base_classes:
                    group_name = f"hierarchy_{comp.name}"
                    groups[group_name] = [comp.name] + base_classes

        return groups

    def _group_by_file(self, components: Dict[str, CodeComponent]) -> Dict[str, List[str]]:
        """Group components by the file they belong to."""
        file_groups = {}

        for comp in components.values():
            file_name = comp.file_path.split('/')[-1].replace('.py', '')
            group_name = f"module_{file_name}"

            if group_name not in file_groups:
                file_groups[group_name] = []
            file_groups[group_name].append(comp.name)

        # Only keep groups with multiple components
        return {k: v for k, v in file_groups.items() if len(v) > 1}

    def _group_by_functionality(self, components: Dict[str, CodeComponent]) -> Dict[str, List[str]]:
        """Group components by functionality based on naming patterns."""
        groups = {}

        # Common naming patterns
        patterns = {
            "user_management": ["user", "customer", "admin", "auth"],
            "data_processing": ["process", "parse", "transform", "convert"],
            "payment": ["payment", "billing", "invoice", "transaction"],
            "database": ["database", "db", "storage", "repository"],
            "api": ["api", "endpoint", "request", "response"],
            "utils": ["util", "helper", "common", "shared"]
        }

        for group_name, keywords in patterns.items():
            group_components = []
            for comp_name in components:
                if any(keyword in comp_name.lower() for keyword in keywords):
                    group_components.append(comp_name)

            if len(group_components) > 1:
                groups[group_name] = group_components

        return groups

    def _create_visual_settings(self, diagram_type: DiagramType,
                              layout_strategy: LayoutStrategy) -> Dict[str, Any]:
        """Create visual settings for the diagram."""
        base_settings = {
            "theme": "neutral",
            "font_size": 14,
            "edge_style": "solid",
            "show_labels": True,
            "show_metadata": False
        }

        if diagram_type == DiagramType.CLASS:
            base_settings.update({
                "shape": "class",
                "show_methods": True,
                "show_properties": True,
                "class_color": "#E3F2FD",
                "interface_color": "#FFF3E0"
            })
        elif diagram_type == DiagramType.ARCHITECTURE:
            base_settings.update({
                "shape": "rectangle",
                "show_layer_boundaries": True,
                "layer_colors": ["#F5F5F5", "#EEEEEE", "#E0E0E0"]
            })
        elif diagram_type == DiagramType.FLOW:
            base_settings.update({
                "shape": "rounded_rectangle",
                "flow_direction": "TB",  # Top to Bottom
                "decision_color": "#FFEBEE",
                "process_color": "#E8F5E8"
            })

        if layout_strategy == LayoutStrategy.HIERARCHICAL:
            base_settings.update({
                "direction": "TB",
                "spacing": "100"
            })
        elif layout_strategy == LayoutStrategy.LAYERED:
            base_settings.update({
                "direction": "LR",
                "layer_spacing": "150"
            })

        return base_settings