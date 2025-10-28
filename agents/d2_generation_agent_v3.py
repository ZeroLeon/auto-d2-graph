"""
D2 Generation Agent - Version 3.0

Enhanced D2 generation with professional shapes, layouts, and styling.
Ensures all generated D2 code is syntactically correct and renderable.
"""

import re
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from data_models import (
    CodeComponent as Component,
    Relationship,
    DiagramDesign,
    ValidationResult,
    ComponentType
)
from agents.shape_intelligence_agent import ShapeIntelligenceAgent, ShapeMapping
from shape_library import ProfessionalShapeLibrary

@dataclass
class D2GenerationResult:
    """Result of D2 generation with metadata"""
    d2_code: str
    shapes_used: Set[str]
    layout_engine: str
    theme_used: str
    validation_errors: List[str]
    generation_time: float

class D2GenerationAgentV3:
    """
    Enhanced D2 generation agent with professional shapes and layouts.
    Focuses on generating syntactically correct, renderable D2 code.
    """

    def __init__(self):
        self.shape_intelligence = ShapeIntelligenceAgent()
        self.shape_library = ProfessionalShapeLibrary()
        self.generation_stats = {
            'total_generated': 0,
            'successful_renders': 0,
            'failed_renders': 0
        }

    def generate_d2(self, design: DiagramDesign, components: List[Component],
                   relationships: List[Relationship]) -> D2GenerationResult:
        """
        Generate professional D2 code with correct syntax

        Args:
            design: Diagram design with layout information
            components: List of components to include
            relationships: List of relationships between components

        Returns:
            D2GenerationResult with generated code and metadata
        """
        import time
        start_time = time.time()

        try:
            # Analyze components and determine shapes
            component_shapes = self._analyze_component_shapes(components)

            # Generate D2 code sections
            d2_sections = []

            # 1. Header and configuration
            d2_sections.append(self._generate_header(design))

            # 2. Layout configuration
            d2_sections.append(self._generate_layout_config(design))

            # 3. Professional classes definition
            d2_sections.append(self._generate_classes(component_shapes))

            # 4. Component definitions
            components_d2 = self._generate_components(components, component_shapes)
            d2_sections.append(components_d2)

            # 5. Relationships
            relationships_d2 = self._generate_relationships(relationships, component_shapes)
            d2_sections.append(relationships_d2)

            # 6. Groupings and hierarchy
            groupings_d2 = self._generate_groupings(components, design)
            d2_sections.append(groupings_d2)

            # 7. Legend
            legend_d2 = self._generate_legend(component_shapes)
            d2_sections.append(legend_d2)

            # Combine all sections
            d2_code = '\n\n'.join(filter(None, d2_sections))

            # Validate the generated D2 code
            validation_errors = self._validate_d2_code(d2_code)

            shapes_used = {mapping.shape for mapping in component_shapes.values()}

            generation_time = time.time() - start_time
            self.generation_stats['total_generated'] += 1

            if not validation_errors:
                self.generation_stats['successful_renders'] += 1
            else:
                self.generation_stats['failed_renders'] += 1

            return D2GenerationResult(
                d2_code=d2_code,
                shapes_used=shapes_used,
                layout_engine=design.layout_strategy,
                theme_used=design.style_theme,
                validation_errors=validation_errors,
                generation_time=generation_time
            )

        except Exception as e:
            return D2GenerationResult(
                d2_code=self._generate_fallback_d2(components, relationships),
                shapes_used={'rectangle'},
                layout_engine='hierarchical',
                theme_used='professional_blue',
                validation_errors=[f"Generation error: {str(e)}"],
                generation_time=time.time() - start_time
            )

    def _analyze_component_shapes(self, components: List[Component]) -> Dict[str, ShapeMapping]:
        """Analyze all components and determine appropriate shapes"""
        component_shapes = {}

        for component in components:
            # Build context for shape analysis
            # Handle both old Method objects and new string lists
            if component.methods and hasattr(component.methods[0], 'name'):
                methods = [method.name for method in component.methods]
            else:
                methods = component.methods or []

            context = {
                'methods': methods,
                'imports': component.imports if hasattr(component, 'imports') else []
            }

            # Get shape mapping
            shape_mapping = self.shape_intelligence.analyze_component_shape(component, context)
            component_shapes[component.name] = shape_mapping

        return component_shapes

    def _generate_header(self, design: DiagramDesign) -> str:
        """Generate D2 header with metadata"""
        header_lines = [
            "# D2 Diagram generated by Agentic D2 Diagram Generator v3.0",
            f"# Diagram Type: {design.diagram_type}",
            f"# Layout Strategy: {design.layout_strategy}",
            f"# Theme: {design.style_theme}",
            "",
            "# Global Configuration"
        ]

        return '\n'.join(header_lines)

    def _generate_layout_config(self, design: DiagramDesign) -> str:
        """Generate layout configuration with proper D2 syntax"""
        config_lines = []
        layout_config = self.shape_library.get_layout_config(design.layout_strategy)

        # Direction setting
        if layout_config.get('direction'):
            config_lines.append(f'direction: {layout_config["direction"]}')

        # Layout engine configuration (simplified for compatibility)
        if layout_config.get('engine') and layout_config['engine'] != 'default':
            config_lines.append('vars: {')
            config_lines.append('  d2-config: {')
            config_lines.append(f'    layout-engine: {layout_config["engine"]}')
            config_lines.append('  }')
            config_lines.append('}')

        # Global styling
        config_lines.extend([
            '',
            '# Global Styling',
            'style.font-size: 12',
            'gap: 60'
        ])

        return '\n'.join(config_lines)

    def _generate_classes(self, component_shapes: Dict[str, ShapeMapping]) -> str:
        """Generate class definitions for consistent styling"""
        classes_lines = ["# Professional Shape Classes"]

        # Define classes based on shapes used
        for component_name, shape_mapping in component_shapes.items():
            shape = shape_mapping.shape
            class_name = f"{shape}_class"

            # Get professional styling
            style_def = self.shape_library.get_class_definition(class_name)
            if style_def:
                classes_lines.append(f'{class_name}: {{')
                for key, value in style_def.items():
                    classes_lines.append(f'  {key}: {value}')
                classes_lines.append('}')
                classes_lines.append('')

        return '\n'.join(classes_lines).strip()

    def _generate_components(self, components: List[Component],
                           component_shapes: Dict[str, ShapeMapping]) -> str:
        """Generate component definitions with professional shapes"""
        components_lines = ["# Component Definitions"]

        for component in components:
            shape_mapping = component_shapes[component.name]
            shape = shape_mapping.shape

            # Component definition
            component_def = f'"{component.name}" {{'

            # Label with methods
            label_lines = [component.name]
            if component.methods:
                method_lines = []
                # Handle both Method objects and strings
                for method in component.methods[:5]:  # Limit to 5 methods
                    if hasattr(method, 'name'):
                        method_lines.append(f"+ {method.name}()")
                    else:
                        method_lines.append(f"+ {method}()")
                if method_lines:
                    label_lines.append("---")
                    label_lines.extend(method_lines)

            label = '\\n'.join(label_lines)
            component_def += f'\n  label: "{label}"'

            # Shape definition
            if shape != 'rectangle':  # Rectangle is default
                component_def += f'\n  shape: {shape}'

            # Apply professional styling
            style = self.shape_library.get_shape_style(shape)
            component_def += '\n  style {'
            component_def += f'\n    fill: "{style.fill}"'
            component_def += f'\n    stroke: "{style.stroke}"'
            component_def += f'\n    stroke-width: {style.stroke_width}'
            component_def += f'\n    font-color: "{style.font_color}"'

            if style.border_radius > 0:
                component_def += f'\n    border-radius: {style.border_radius}'

            if style.shadow:
                component_def += '\n    shadow: true'

            if style.opacity < 1.0:
                component_def += f'\n    opacity: {style.opacity}'

            # Additional styles (fix nested style syntax)
            if style.additional_styles:
                for key, value in style.additional_styles.items():
                    if key.startswith('style.'):
                        # Remove style. prefix and fix syntax
                        clean_key = key.replace('style.', '')
                        if isinstance(value, str) and not value.isnumeric():
                            component_def += f'\n    {clean_key}: "{value}"'
                        else:
                            component_def += f'\n    {clean_key}: {value}'

            component_def += '\n  }'    # Close style block
            component_def += '\n}'      # Close component block

            components_lines.append(component_def)
            components_lines.append('')

        return '\n'.join(components_lines).strip()

    def _generate_relationships(self, relationships: List[Relationship],
                               component_shapes: Dict[str, ShapeMapping]) -> str:
        """Generate relationship definitions with simplified D2 syntax"""
        if not relationships:
            return ""

        relationships_lines = ["# Relationships"]

        for rel in relationships:
            # Simple relationship definition - D2 will handle default styling
            rel_def = f'"{rel.source}" -> "{rel.target}"'

            # Add label if present
            if hasattr(rel, 'label') and rel.label:
                rel_def += f': "{rel.label}"'

            # Add basic style block with only essential, D2-compatible attributes
            rel_def += ' {'
            rel_def += '\n  style {'
            rel_def += '\n    stroke-width: 1'
            rel_def += '\n    stroke: "#4caf50"'
            rel_def += '\n  }'
            rel_def += '\n}'

            relationships_lines.append(rel_def)

        return '\n'.join(relationships_lines)

    def _generate_groupings(self, components: List[Component], design: DiagramDesign) -> str:
        """Generate logical groupings for components"""
        groupings_lines = ["# Logical Groupings"]

        # Group by module/package
        modules = {}
        for component in components:
            module = getattr(component, 'module', 'default')
            if module not in modules:
                modules[module] = []
            modules[module].append(component.name)

        # Create module groups
        for module_name, component_names in modules.items():
            if len(component_names) > 1:  # Only group modules with multiple components
                group_def = f'"{module_name}_group" {{'
                group_def += f'\n  label: "Module: {module_name}"'

                for comp_name in component_names:
                    group_def += f'\n  "{comp_name}"'

                group_def += '\n}'
                groupings_lines.append(group_def)
                groupings_lines.append('')

        return '\n'.join(groupings_lines).strip()

    def _generate_legend(self, component_shapes: Dict[str, ShapeMapping]) -> str:
        """Generate legend for shapes used"""
        shapes_used = {mapping.shape for mapping in component_shapes.values()}
        legend_items = self.shape_library.generate_legend_items(shapes_used)

        if not legend_items:
            return ""

        legend_lines = ["# Diagram Legend"]
        legend_lines.append('vars: {')
        legend_lines.append('  d2-legend: {')

        for key, item in legend_items.items():
            legend_lines.append(f'    {key}: {{')
            legend_lines.append(f'      label: "{item["label"]}"')
            if item.get('shape') and item['shape'] != 'rectangle':
                legend_lines.append(f'      shape: {item["shape"]}')
            if item.get('style.fill'):
                legend_lines.append(f'      style.fill: "{item["style.fill"]}"')
            if item.get('style.stroke'):
                legend_lines.append(f'      style.stroke: "{item["style.stroke"]}"')
            if item.get('style.font-color'):
                legend_lines.append(f'      style.font-color: "{item["style.font-color"]}"')
            legend_lines.append('    }')

        legend_lines.append('  }')
        legend_lines.append('}')

        return '\n'.join(legend_lines)

    def _validate_d2_code(self, d2_code: str) -> List[str]:
        """Validate D2 code for common syntax issues"""
        errors = []
        lines = d2_code.split('\n')

        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Check for quote issues
            if 'label:' in line:
                # Ensure labels are properly quoted
                label_match = re.search(r'label:\s*(.+)', line)
                if label_match:
                    label_value = label_match.group(1).strip()
                    if not (label_value.startswith('"') and label_value.endswith('"')):
                        errors.append(f"Line {i}: Label should be quoted: {line}")

            # Check for style syntax
            if 'style:' in line and '{' in line:
                # Check if style block is properly formatted
                if not line.rstrip().endswith('{'):
                    errors.append(f"Line {i}: Style block should end with '}}': {line}")

            # Check for proper attribute syntax
            if ':' in line and not line.startswith('#'):
                # Ensure values are properly quoted when needed
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    if key.startswith('style.') and not value.isnumeric() and not value in ['true', 'false']:
                        if not (value.startswith('"') and value.endswith('"')):
                            errors.append(f"Line {i}: Style value should be quoted: {line}")

        return errors

    def _generate_fallback_d2(self, components: List[Component],
                             relationships: List[Relationship]) -> str:
        """Generate simple fallback D2 if generation fails"""
        d2_lines = [
            "# Fallback D2 Diagram",
            "direction: down",
            "",
            "# Components"
        ]

        for component in components[:10]:  # Limit components in fallback
            d2_lines.append(f'"{component.name}" {{')
            d2_lines.append(f'  label: "{component.name}"')
            d2_lines.append(f'  shape: rectangle')
            d2_lines.append('}')

        if relationships:
            d2_lines.append("")
            d2_lines.append("# Relationships")
            for rel in relationships[:5]:  # Limit relationships in fallback
                d2_lines.append(f'"{rel.source}" -> "{rel.target}"')

        return '\n'.join(d2_lines)

    def get_generation_stats(self) -> Dict[str, int]:
        """Get generation statistics"""
        return self.generation_stats.copy()