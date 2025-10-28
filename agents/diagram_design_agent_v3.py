"""
Diagram Design Agent - Version 3.0

Enhanced diagram design with intelligent layout engine selection,
pattern detection, and professional design principles.
"""

import re
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict
import networkx as nx

from data_models import (
    CodeComponent as Component,
    Relationship,
    DiagramDesign,
    ComponentType,
    LayoutStrategy,
    DiagramType
)
from agents.shape_intelligence_agent import ShapeIntelligenceAgent
from shape_library import ProfessionalShapeLibrary

@dataclass
class LayoutAnalysis:
    """Analysis result for layout determination"""
    recommended_engine: str
    confidence: float
    reasoning: str
    diagram_type: str
    layout_config: Dict

class DiagramDesignAgentV3:
    """
    Enhanced diagram design agent with intelligent layout selection
    and professional design patterns.
    """

    def __init__(self):
        self.shape_intelligence = ShapeIntelligenceAgent()
        self.shape_library = ProfessionalShapeLibrary()
        self.layout_patterns = self._initialize_layout_patterns()

    def _initialize_layout_patterns(self) -> Dict[str, Dict]:
        """Initialize layout pattern detection rules"""
        return {
            'microservices': {
                'indicators': [
                    r'.*Service.*$', r'.*API.*$', r'.*Gateway.*$', r'.*Controller.*$'
                ],
                'relationship_patterns': ['api_call', 'dependency'],
                'component_threshold': 5,
                'preferred_engine': 'elk',
                'direction': 'right'
            },
            'layered_architecture': {
                'indicators': [
                    r'.*Controller.*$', r'.*Service.*$', r'.*Repository.*$', r'.*Model.*$'
                ],
                'relationship_patterns': ['dependency', 'inheritance'],
                'component_threshold': 4,
                'preferred_engine': 'elk',
                'direction': 'down'
            },
            'data_flow': {
                'indicators': [
                    r'.*Processor.*$', r'.*Transformer.*$', r'.*Pipeline.*$', r'.*Flow.*$'
                ],
                'relationship_patterns': ['data_flow', 'async_message'],
                'component_threshold': 3,
                'preferred_engine': 'dagre',
                'direction': 'right'
            },
            'system_landscape': {
                'indicators': [
                    r'.*External.*$', r'.*System.*$', r'.*Integration.*$', r'.*Partner.*$'
                ],
                'relationship_patterns': ['association', 'api_call'],
                'component_threshold': 8,
                'preferred_engine': 'elk',
                'direction': 'right'
            },
            'component_overview': {
                'indicators': [],  # Default pattern
                'relationship_patterns': ['dependency'],
                'component_threshold': 0,
                'preferred_engine': 'grid',
                'direction': 'right'
            }
        }

    def design_diagram(self, components: List[Component], relationships: List[Relationship] = None,
                      user_preferences: Dict = None) -> DiagramDesign:
        """
        Design diagram with intelligent layout selection and professional styling

        Args:
            components: List of components to include
            relationships: List of relationships between components
            user_preferences: User preferences for layout and styling

        Returns:
            DiagramDesign with layout and styling decisions
        """
        relationships = relationships or []
        user_preferences = user_preferences or {}

        # Analyze component patterns
        layout_analysis = self._analyze_layout_patterns(components, relationships)

        # Determine optimal component selection
        selected_components = self._select_optimal_components(components, relationships)

        # Analyze component relationships for layout optimization
        relationship_analysis = self._analyze_relationships(selected_components, relationships)

        # Determine styling theme
        theme = self._determine_theme(selected_components, user_preferences)

        # Map V3.0 values to V2.0 compatible values
        diagram_type_map = {
            'microservices': 'architecture',
            'layered_architecture': 'class',
            'data_flow': 'flow',
            'system_landscape': 'architecture',
            'component_overview': 'class'
        }

        layout_strategy_map = {
            'elk': 'hierarchical',
            'dagre': 'hierarchical',
            'grid': 'grid'
        }

        # Create diagram design with V2.0 compatible values
        design = DiagramDesign(
            diagram_type=DiagramType(diagram_type_map.get(layout_analysis.diagram_type, 'class')),
            layout_strategy=LayoutStrategy(layout_strategy_map.get(layout_analysis.recommended_engine, 'hierarchical')),
            components_to_include=[comp.name for comp in selected_components],
            grouping_strategy={},  # V2.0 format
            visual_settings={  # V2.0 format
                'theme': theme,
                'v3_config': {
                    'layout_engine': layout_analysis.recommended_engine,
                    'layout_config': layout_analysis.layout_config,
                    'selected_components': selected_components,
                    'relationships': relationships
                }
            }
        )

        return design

    def _analyze_layout_patterns(self, components: List[Component],
                               relationships: List[Relationship]) -> LayoutAnalysis:
        """Analyze components and relationships to determine optimal layout"""
        component_names = [comp.name for comp in components]
        relationship_types = [getattr(rel, 'type', 'dependency') for rel in relationships]

        best_match = None
        best_confidence = 0.0

        for pattern_name, pattern_config in self.layout_patterns.items():
            confidence = self._calculate_pattern_confidence(
                component_names, relationship_types, pattern_config
            )

            if confidence > best_confidence:
                best_confidence = confidence
                best_match = pattern_name

        if not best_match:
            best_match = 'component_overview'
            best_confidence = 0.5

        pattern_config = self.layout_patterns[best_match]
        layout_config = self.shape_library.get_layout_config(best_match)

        return LayoutAnalysis(
            recommended_engine=pattern_config['preferred_engine'],
            confidence=best_confidence,
            reasoning=f"Pattern '{best_match}' detected with {best_confidence:.2f} confidence",
            diagram_type=best_match,
            layout_config=layout_config
        )

    def _calculate_pattern_confidence(self, component_names: List[str],
                                     relationship_types: List[str],
                                     pattern_config: Dict) -> float:
        """Calculate confidence score for a layout pattern"""
        confidence = 0.0
        total_checks = 0

        # Check component name patterns
        if pattern_config['indicators']:
            pattern_matches = 0
            for name in component_names:
                for indicator in pattern_config['indicators']:
                    if re.search(indicator, name, re.IGNORECASE):
                        pattern_matches += 1
                        break

            if component_names:
                pattern_score = pattern_matches / len(component_names)
                confidence += pattern_score * 0.6  # Weight patterns more heavily
                total_checks += 0.6

        # Check relationship patterns
        if pattern_config['relationship_patterns'] and relationship_types:
            pattern_matches = sum(1 for rel_type in relationship_types
                               if rel_type in pattern_config['relationship_patterns'])
            rel_score = pattern_matches / len(relationship_types)
            confidence += rel_score * 0.4  # Weight relationships
            total_checks += 0.4

        # Check component threshold
        if pattern_config['component_threshold'] > 0:
            threshold_met = len(component_names) >= pattern_config['component_threshold']
            if threshold_met:
                confidence += 0.2
            total_checks += 0.2

        # Normalize confidence
        if total_checks > 0:
            confidence = confidence / total_checks

        return min(confidence, 1.0)

    def _select_optimal_components(self, components: List[Component],
                                  relationships: List[Relationship]) -> List[Component]:
        """
        Select optimal components for diagram readability
        """
        # Enhanced component selection with shape intelligence
        component_scores = []

        for component in components:
            score = self._calculate_component_importance(component, relationships)
            component_scores.append((component, score))

        # Sort by importance score
        component_scores.sort(key=lambda x: x[1], reverse=True)

        # Select top components based on diagram complexity
        max_components = self._determine_optimal_component_count(len(components))
        selected = [comp for comp, score in component_scores[:max_components]]

        return selected

    def _calculate_component_importance(self, component: Component,
                                     relationships: List[Relationship]) -> float:
        """Calculate importance score for a component"""
        score = 0.0

        # Base score for component type
        type_scores = {
            ComponentType.CLASS: 1.0,
            ComponentType.FUNCTION: 0.7,
            ComponentType.MODULE: 0.8
        }
        score += type_scores.get(component.type, 0.5)

        # Score based on relationships (centrality)
        incoming_count = sum(1 for rel in relationships if rel.target == component.name)
        outgoing_count = sum(1 for rel in relationships if rel.source == component.name)
        relationship_score = (incoming_count + outgoing_count) * 0.2
        score += relationship_score

        # Score based on methods (complexity indicator)
        if component.methods:
            method_score = min(len(component.methods) * 0.1, 1.0)
            score += method_score

        # Score based on semantic importance
        name_patterns = {
            r'.*(Service|Manager|Controller)$': 1.0,
            r'.*(Model|Entity|Repository)$': 0.9,
            r'.*(API|Gateway|Router)$': 0.8,
            r'.*(Config|Setting|Constant)$': 0.6
        }

        for pattern, pattern_score in name_patterns.items():
            if re.search(pattern, component.name, re.IGNORECASE):
                score += pattern_score
                break

        return score

    def _determine_optimal_component_count(self, total_components: int) -> int:
        """Determine optimal number of components for readability"""
        # Enhanced limits based on layout capabilities
        if total_components <= 8:
            return total_components
        elif total_components <= 15:
            return 12  # Increased from 10 due to better layouts
        elif total_components <= 30:
            return 15  # Increased from 12
        else:
            return 20  # Increased from 15 for complex systems

    def _analyze_relationships(self, components: List[Component],
                             relationships: List[Relationship]) -> Dict:
        """Analyze relationships for layout optimization"""
        component_names = {comp.name for comp in components}

        # Filter relationships to only include selected components
        filtered_relationships = [
            rel for rel in relationships
            if rel.source in component_names and rel.target in component_names
        ]

        # Build relationship graph for analysis
        graph = nx.DiGraph()
        for component in components:
            graph.add_node(component.name)

        for rel in filtered_relationships:
            graph.add_edge(rel.source, rel.target)

        analysis = {
            'total_relationships': len(filtered_relationships),
            'connected_components': len(graph.nodes()),
            'has_cycles': not nx.is_directed_acyclic_graph(graph),
            'average_connections': 0,
            'hierarchy_depth': 0
        }

        if graph.nodes():
            analysis['average_connections'] = sum(dict(graph.degree()).values()) / len(graph.nodes())

        try:
            analysis['hierarchy_depth'] = nx.dag_longest_path_length(graph) + 1
        except:
            pass

        return analysis

    def _determine_theme(self, components: List[Component],
                        user_preferences: Dict) -> str:
        """Determine appropriate styling theme"""
        if 'theme' in user_preferences:
            return user_preferences['theme']

        # Analyze component patterns for theme selection
        component_names = [comp.name.lower() for comp in components]

        if any('service' in name or 'api' in name for name in component_names):
            return 'professional_blue'
        elif any('data' in name or 'model' in name for name in component_names):
            return 'enterprise_green'
        elif any('user' in name or 'client' in name for name in component_names):
            return 'tech_orange'
        else:
            return 'modern_purple'

    def optimize_layout_for_shapes(self, components: List[Component],
                                 layout_analysis: LayoutAnalysis) -> Dict:
        """Optimize layout configuration based on shapes used"""
        # Analyze shapes that will be used
        shapes_used = set()
        for component in components:
            context = {
                'methods': [method.name for method in component.methods],
                'imports': getattr(component, 'imports', [])
            }
            shape_mapping = self.shape_intelligence.analyze_component_shape(component, context)
            shapes_used.add(shape_mapping.shape)

        # Optimize layout based on shapes
        layout_config = layout_analysis.layout_config.copy()

        # Adjust spacing based on shape complexity
        if 'cylinder' in shapes_used or 'cloud' in shapes_used:
            # Databases and clouds need more space
            if 'spacing' in layout_config:
                layout_config['spacing']['nodeNode'] = int(
                    layout_config['spacing']['nodeNode'] * 1.2
                )

        # Adjust layout for person shapes (usually on edges)
        if 'person' in shapes_used:
            layout_config['edge_placement'] = True

        return layout_config

    def get_design_recommendations(self, components: List[Component],
                                 relationships: List[Relationship]) -> Dict:
        """Get recommendations for diagram design"""
        layout_analysis = self._analyze_layout_patterns(components, relationships)
        relationship_analysis = self._analyze_relationships(components, relationships)

        recommendations = {
            'layout_engine': layout_analysis.recommended_engine,
            'diagram_type': layout_analysis.diagram_type,
            'confidence': layout_analysis.confidence,
            'theme': self._determine_theme(components, {}),
            'component_count': len(components),
            'relationship_count': len(relationships),
            'complexity': 'simple' if len(components) <= 10 else 'complex' if len(components) <= 20 else 'very_complex'
        }

        # Add specific recommendations
        if relationship_analysis['has_cycles']:
            recommendations['layout_suggestion'] = 'Consider using ELK layout engine for cyclic dependencies'

        if relationship_analysis['average_connections'] > 4:
            recommendations['layout_suggestion'] = 'High connectivity detected, consider component grouping'

        if layout_analysis.confidence < 0.6:
            recommendations['layout_suggestion'] = 'Mixed patterns detected, manual layout adjustment may be beneficial'

        return recommendations