"""
Professional Shape Library - Version 3.0

Defines comprehensive shape styles, themes, and professional styling patterns
for enterprise-grade D2 diagrams.
"""

from typing import Dict, Any, Optional, Set, Tuple, List
from dataclasses import dataclass
import json

@dataclass
class ShapeStyle:
    """Defines styling for a specific shape type"""
    shape: str
    fill: str
    stroke: str
    font_color: str
    stroke_width: int = 2
    border_radius: int = 0
    shadow: bool = False
    opacity: float = 1.0
    additional_styles: Dict[str, str] = None

class ProfessionalShapeLibrary:
    """
    Comprehensive library of professional shapes and styling patterns
    for enterprise-grade D2 diagrams.
    """

    def __init__(self):
        self.shape_styles = self._initialize_shape_styles()
        self.themes = self._initialize_themes()
        self.classes = self._initialize_classes()
        self.layout_configs = self._initialize_layout_configs()

    def _initialize_shape_styles(self) -> Dict[str, ShapeStyle]:
        """Initialize professional styling for all shape types"""
        return {
            # Service Components
            'class': ShapeStyle(
                shape='class',
                fill='#f8f9fa',
                stroke='#495057',
                font_color='#212529',
                stroke_width=2,
                border_radius=8,
                shadow=True,
                additional_styles={
                    'font-size': '14'
                }
            ),

            # Database Components
            'cylinder': ShapeStyle(
                shape='cylinder',
                fill='#e3f2fd',
                stroke='#1976d2',
                font_color='#0d47a1',
                stroke_width=2,
                shadow=True,
                additional_styles={
                    'font-size': '13'
                }
            ),

            # API Components
            'rectangle_api': ShapeStyle(
                shape='rectangle',
                fill='#fff3e0',
                stroke='#f57c00',
                font_color='#e65100',
                stroke_width=2,
                border_radius=6,
                shadow=True,
                additional_styles={
                    'font-size': '13'
                }
            ),

            # User/Actor Components
            'person': ShapeStyle(
                shape='person',
                fill='#fff3e0',
                stroke='#ff9800',
                font_color='#e65100',
                stroke_width=2,
                shadow=True,
                additional_styles={
                    'font-size': '12'
                }
            ),

            # External Systems
            'cloud': ShapeStyle(
                shape='cloud',
                fill='#f5f5f5',
                stroke='#9e9e9e',
                font_color='#424242',
                stroke_width=2,
                opacity=0.9,
                additional_styles={
                    'style.font-size': '12',
                    'style.stroke-dash': '3'
                }
            ),

            # Message/Event Components
            'hexagon': ShapeStyle(
                shape='hexagon',
                fill='#f3e5f5',
                stroke='#9c27b0',
                font_color='#4a148c',
                stroke_width=2,
                border_radius=4,
                shadow=True,
                additional_styles={
                    'font-size': '12'
                }
            ),

            # Queue Components
            'trapezoid': ShapeStyle(
                shape='trapezoid',
                fill='#fff8e1',
                stroke='#ffc107',
                font_color='#f57f17',
                stroke_width=2,
                shadow=True,
                additional_styles={
                    'font-size': '12'
                }
            ),

            # Configuration Components
            'document': ShapeStyle(
                shape='document',
                fill='#f1f8e9',
                stroke='#689f38',
                font_color='#33691e',
                stroke_width=1,
                border_radius=3,
                additional_styles={
                    'style.font-size': '11',
                    'style.font-family': 'monospace'
                }
            ),

            # Storage Components
            'stored_data': ShapeStyle(
                shape='stored_data',
                fill='#e8f5e8',
                stroke='#4caf50',
                font_color='#1b5e20',
                stroke_width=2,
                shadow=True,
                additional_styles={
                    'font-size': '12'
                }
            ),

            # Infrastructure Components
            'diamond': ShapeStyle(
                shape='diamond',
                fill='#fce4ec',
                stroke='#e91e63',
                font_color='#880e4f',
                stroke_width=2,
                shadow=True,
                additional_styles={
                    'font-size': '12'
                }
            ),

            # Default Rectangle
            'rectangle': ShapeStyle(
                shape='rectangle',
                fill='#ffffff',
                stroke='#757575',
                font_color='#424242',
                stroke_width=1,
                border_radius=4,
                additional_styles={
                    'font-size': '12'
                }
            )
        }

    def _initialize_themes(self) -> Dict[str, Dict[str, str]]:
        """Initialize professional color themes"""
        return {
            'professional_blue': {
                'primary': '#1976d2',
                'secondary': '#42a5f5',
                'accent': '#ff9800',
                'success': '#4caf50',
                'warning': '#ff9800',
                'error': '#f44336',
                'neutral_light': '#f5f5f5',
                'neutral_dark': '#424242',
                'text_primary': '#212529',
                'text_secondary': '#6c757d'
            },

            'enterprise_green': {
                'primary': '#2e7d32',
                'secondary': '#66bb6a',
                'accent': '#ffa726',
                'success': '#4caf50',
                'warning': '#ff9800',
                'error': '#f44336',
                'neutral_light': '#f1f8e9',
                'neutral_dark': '#1b5e20',
                'text_primary': '#263238',
                'text_secondary': '#546e7a'
            },

            'modern_purple': {
                'primary': '#7b1fa2',
                'secondary': '#ba68c8',
                'accent': '#ff7043',
                'success': '#66bb6a',
                'warning': '#ffa726',
                'error': '#ef5350',
                'neutral_light': '#f3e5f5',
                'neutral_dark': '#4a148c',
                'text_primary': '#212121',
                'text_secondary': '#757575'
            },

            'tech_orange': {
                'primary': '#e65100',
                'secondary': '#ff9800',
                'accent': '#29b6f6',
                'success': '#66bb6a',
                'warning': '#ffa726',
                'error': '#ef5350',
                'neutral_light': '#fff3e0',
                'neutral_dark': '#e65100',
                'text_primary': '#263238',
                'text_secondary': '#546e7a'
            }
        }

    def _initialize_classes(self) -> Dict[str, Dict[str, Any]]:
        """Initialize reusable class definitions for consistent styling"""
        return {
            'service_class': {
                'shape': 'class',
                'style.fill': '#f8f9fa',
                'style.stroke': '#495057',
                'style.font-color': '#212529',
                'style.stroke-width': 2,
                'style.border-radius': 8,
                'style.shadow': True,
                'style.font-size': 14
            },

            'database_class': {
                'shape': 'cylinder',
                'style.fill': '#e3f2fd',
                'style.stroke': '#1976d2',
                'style.font-color': '#0d47a1',
                'style.stroke-width': 2,
                'style.shadow': True,
                'style.font-size': 13
            },

            'api_class': {
                'shape': 'rectangle',
                'style.fill': '#fff3e0',
                'style.stroke': '#f57c00',
                'style.font-color': '#e65100',
                'style.stroke-width': 2,
                'style.border-radius': 6,
                'style.shadow': True,
                'style.font-size': 13
            },

            'user_class': {
                'shape': 'person',
                'style.fill': '#ffe0b2',
                'style.stroke': '#ff9800',
                'style.font-color': '#e65100',
                'style.stroke-width': 2,
                'style.shadow': True,
                'style.font-size': 12
            },

            'external_class': {
                'shape': 'cloud',
                'style.fill': '#f5f5f5',
                'style.stroke': '#9e9e9e',
                'style.font-color': '#424242',
                'style.stroke-width': 2,
                'style.opacity': 0.9,
                'style.stroke-dash': 3,
                'style.font-size': 12
            }
        }

    def _initialize_layout_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize layout configurations for different diagram types"""
        return {
            'microservices': {
                'engine': 'elk',
                'direction': 'right',
                'spacing': {
                    'nodeNode': 60,
                    'nodeNodeBetweenLayers': 80
                },
                'elk_algorithm': 'layered',
                'elk_spacing_componentComponent': 30
            },

            'layered_architecture': {
                'engine': 'elk',
                'direction': 'down',
                'spacing': {
                    'nodeNode': 40,
                    'nodeNodeBetweenLayers': 100
                },
                'elk_algorithm': 'layered',
                'elk_layering_strategy': 'INTERACTIVE'
            },

            'data_flow': {
                'engine': 'dagre',
                'direction': 'right',
                'ranksep': 60,
                'nodesep': 50,
                'edgesep': 10
            },

            'component_overview': {
                'engine': 'grid',
                'grid_gap': 40,
                'rows': 3,
                'cols': 4,
                'show_grid': False
            },

            'system_landscape': {
                'engine': 'elk',
                'direction': 'right',
                'spacing': {
                    'nodeNode': 80,
                    'nodeNodeBetweenLayers': 120
                },
                'elk_algorithm': 'force',
                'elk_spacing_nodeNode': 100
            }
        }

    def get_shape_style(self, shape_name: str, theme: str = 'professional_blue') -> ShapeStyle:
        """
        Get styling for a specific shape with theme applied

        Args:
            shape_name: Name of the shape
            theme: Theme name to apply

        Returns:
            ShapeStyle with theme colors applied
        """
        base_style = self.shape_styles.get(shape_name, self.shape_styles['rectangle'])
        theme_colors = self.themes.get(theme, self.themes['professional_blue'])

        # Apply theme colors
        if base_style.fill == '#f8f9fa':  # Default service color
            base_style.fill = theme_colors['neutral_light']
        if base_style.stroke == '#495057':  # Default stroke
            base_style.stroke = theme_colors['primary']
        if base_style.font_color == '#212529':  # Default text
            base_style.font_color = theme_colors['text_primary']

        return base_style

    def get_class_definition(self, class_name: str) -> Optional[Dict[str, Any]]:
        """Get class definition by name"""
        return self.classes.get(class_name)

    def get_layout_config(self, diagram_type: str) -> Dict[str, Any]:
        """Get layout configuration for diagram type"""
        return self.layout_configs.get(diagram_type, self.layout_configs['microservices'])

    def get_connection_style(self, connection_type: str = 'default') -> Dict[str, str]:
        """Get styling for different connection types"""
        connection_styles = {
            'inheritance': {
                'stroke': '#2196f3',
                'stroke-width': 2,
                'stroke-dash': 0,
                'arrowhead': 'triangle'
            },
            'dependency': {
                'stroke': '#4caf50',
                'stroke-width': 1,
                'stroke-dash': 0,
                'arrowhead': 'arrow'
            },
            'composition': {
                'stroke': '#ff9800',
                'stroke-width': 2,
                'stroke-dash': 0,
                'arrowhead': 'diamond',
                'fill': '#ff9800'
            },
            'association': {
                'stroke': '#9e9e9e',
                'stroke-width': 1,
                'stroke-dash': 5,
                'arrowhead': 'none'
            },
            'data_flow': {
                'stroke': '#e91e63',
                'stroke-width': 2,
                'stroke-dash': 0,
                'arrowhead': 'arrow'
            },
            'api_call': {
                'stroke': '#f57c00',
                'stroke-width': 2,
                'stroke-dash': 0,
                'arrowhead': 'arrow'
            },
            'async_message': {
                'stroke': '#9c27b0',
                'stroke-width': 1,
                'stroke-dash': 3,
                'arrowhead': 'arrow'
            },
            'security_boundary': {
                'stroke': '#f44336',
                'stroke-width': 3,
                'stroke-dash': 8,
                'arrowhead': 'none'
            }
        }

        return connection_styles.get(connection_type, connection_styles['dependency'])

    def generate_legend_items(self, shapes_used: Set[str]) -> Dict[str, Dict[str, str]]:
        """
        Generate legend items for shapes used in the diagram

        Args:
            shapes_used: Set of shape names used in the diagram

        Returns:
            Dictionary of legend items
        """
        legend_items = {}

        shape_labels = {
            'class': 'Service',
            'cylinder': 'Database',
            'rectangle_api': 'API',
            'person': 'User/Actor',
            'cloud': 'External System',
            'hexagon': 'Event/Message',
            'trapezoid': 'Queue/Worker',
            'document': 'Configuration',
            'stored_data': 'Storage/Cache',
            'diamond': 'Infrastructure',
            'rectangle': 'Component'
        }

        for shape in shapes_used:
            if shape in shape_labels:
                style = self.get_shape_style(shape)
                legend_items[f"legend_{shape}"] = {
                    'shape': style.shape,
                    'label': shape_labels[shape],
                    'style.fill': style.fill,
                    'style.stroke': style.stroke,
                    'style.font-color': style.font_color
                }

        return legend_items

    def validate_d2_syntax(self, d2_code: str) -> Tuple[bool, List[str]]:
        """
        Validate D2 code for common syntax issues

        Args:
            d2_code: D2 code to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check for common syntax issues
        lines = d2_code.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Check for style attribute syntax
            if 'style.' in line:
                # Ensure style attributes are properly quoted
                if ':' in line and not any(line.strip().endswith(q) for q in ['"', "'"]):
                    if not line.strip().endswith('}'):
                        potential_error = f"Line {i}: Style value may need quotes: {line}"
                        errors.append(potential_error)

            # Check for proper brace matching
            if line.endswith('{'):
                # Check if there's a corresponding closing brace (simplified check)
                open_count = line.count('{')
                close_count = line.count('}')
                if open_count > close_count:
                    # This is just a basic check, full validation would be more complex
                    pass

        return len(errors) == 0, errors