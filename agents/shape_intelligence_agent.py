"""
Shape Intelligence Agent - Version 3.0

Intelligently analyzes Python code components and maps them to appropriate D2 shapes
based on semantic patterns, naming conventions, and architectural roles.
"""

import re
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from data_models import (
    CodeComponent as Component,
    ComponentType
)

@dataclass
class ShapeMapping:
    """Represents a mapping from component to D2 shape"""
    shape: str
    confidence: float
    reasoning: str
    style_overrides: Dict[str, str] = None

class ShapeIntelligenceAgent:
    """
    Analyzes components and determines the most appropriate D2 shapes
    based on semantic patterns and architectural context.
    """

    def __init__(self):
        self.shape_mappings = self._initialize_shape_mappings()
        self.pattern_weights = self._initialize_pattern_weights()

    def _initialize_shape_mappings(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize comprehensive shape mapping patterns"""
        return {
            # Service Layer
            'class': {
                'patterns': [
                    r'.*Service$', r'.*Manager$', r'.*Handler$', r'.*Processor$',
                    r'.*Controller$', r'.*Orchestrator$', r'.*Coordinator$',
                    r'.*Engine$', r'.*Facade$', r'.*Builder$', r'.*Factory$'
                ],
                'reasoning': 'Service/Manager/Handler patterns represent business logic components'
            },

            # Database Layer
            'cylinder': {
                'patterns': [
                    r'.*Model$', r'.*Entity$', r'.*Repository$', r'.*DAO$',
                    r'.*Record$', r'.*Table$', r'.*Schema$', r'.*Mapper$',
                    r'.*Database$', r'.*DB.*$', r'.*Storage.*$'
                ],
                'reasoning': 'Model/Entity/Repository patterns represent data persistence'
            },

            # API Layer
            'rectangle': {
                'api_patterns': [
                    r'.*API$', r'.*Endpoint$', r'.*Route$', r'.*REST.*$',
                    r'.*GraphQL.*$', r'.*Webhook.*$', r'.*Interface.*$',
                    r'.*Gateway$', r'.*Proxy.*$', r'.*Adapter.*$'
                ],
                'reasoning': 'API/Endpoint/Route patterns represent interface components'
            },

            # User/Actor Layer
            'person': {
                'patterns': [
                    r'.*User$', r'.*Client$', r'.*Customer$', r'.*Actor$',
                    r'.*Participant$', r'.*Owner$', r'.*Member.*$', r'.*Profile.*$'
                ],
                'reasoning': 'User/Client/Actor patterns represent people or external actors'
            },

            # External Systems
            'cloud': {
                'patterns': [
                    r'.*External.*$', r'.*Third.*$', r'.*Vendor.*$', r'.*Partner.*$',
                    r'.*Remote.*$', r'.*Outbound.*$', r'.*Foreign.*$', r'.*ExternalAPI.*$'
                ],
                'reasoning': 'External/Third/Vendor patterns represent external systems'
            },

            # Queue/Message Systems
            'queue': {
                'patterns': [
                    r'.*Queue$', r'.*Worker$', r'.*Task$', r'.*Job.*$',
                    r'.*Message.*$', r'.*Event.*$', r'.*Channel.*$', r'.*Broker.*$'
                ],
                'reasoning': 'Queue/Worker/Message patterns represent asynchronous processing'
            },

            # Configuration/Data
            'document': {
                'patterns': [
                    r'.*Config$', r'.*Settings?', r'.*Properties$', r'.*Config.*$',
                    r'.*Environment$', r'.*Constants?', r'.*Defaults?$', r'.*Options.*$'
                ],
                'reasoning': 'Config/Settings patterns represent configuration data'
            },

            # Storage/Cache
            'stored_data': {
                'patterns': [
                    r'.*Cache$', r'.*Store$', r'.*Buffer$', r'.*Session.*$',
                    r'.*Temp.*$', r'.*Memory.*$', r'.*State.*$', r'.*Context.*$'
                ],
                'reasoning': 'Cache/Store/Buffer patterns represent temporary storage'
            },

            # Security/Authentication
            'hexagon': {
                'patterns': [
                    r'.*Auth.*$', r'.*Security$', r'.*Permission.*$', r'.*Role.*$',
                    r'.*Access.*$', r'.*Login.*$', r'.*Token.*$', r'.*OAuth.*$'
                ],
                'reasoning': 'Auth/Security patterns represent security components'
            },

            # Infrastructure
            'diamond': {
                'patterns': [
                    r'.*LoadBalancer.*$', r'.*Balancer.*$', r'.*Router.*$', r'.*Switch.*$',
                    r'.*Firewall.*$', r'.*Gateway.*$', r'.*Middleware.*$', r'.*Filter.*$'
                ],
                'reasoning': 'Infrastructure patterns represent network/middleware components'
            }
        }

    def _initialize_pattern_weights(self) -> Dict[str, float]:
        """Initialize confidence weights for different pattern types"""
        return {
            'exact_match': 1.0,
            'suffix_match': 0.9,
            'contains_match': 0.7,
            'class_name_match': 0.8,
            'method_name_match': 0.6,
            'import_analysis_match': 0.5
        }

    def analyze_component_shape(self, component: Component, context: Dict = None) -> ShapeMapping:
        """
        Analyze a component and determine the most appropriate D2 shape

        Args:
            component: The component to analyze
            context: Additional context (imports, methods, etc.)

        Returns:
            ShapeMapping with shape, confidence, and reasoning
        """
        best_match = ShapeMapping('rectangle', 0.5, 'Default rectangular shape')

        # Analyze component name against patterns
        name_matches = self._analyze_name_patterns(component.name)

        # Analyze component type
        type_match = self._analyze_component_type(component)

        # Analyze methods if available
        method_matches = self._analyze_methods(context.get('methods', []))

        # Analyze imports if available
        import_matches = self._analyze_imports(context.get('imports', []))

        # Combine all matches and select best
        all_matches = name_matches + [type_match] + method_matches + import_matches
        best_match = max(all_matches, key=lambda x: x.confidence)

        # Apply style overrides based on shape
        best_match.style_overrides = self._get_style_overrides(best_match.shape)

        return best_match

    def _analyze_name_patterns(self, name: str) -> List[ShapeMapping]:
        """Analyze component name against all pattern libraries"""
        matches = []

        for shape, config in self.shape_mappings.items():
            patterns = config.get('patterns', []) + config.get('api_patterns', [])

            for pattern in patterns:
                if re.match(pattern, name, re.IGNORECASE):
                    matches.append(ShapeMapping(
                        shape=shape,
                        confidence=self.pattern_weights['exact_match'],
                        reasoning=f"Name '{name}' matches pattern '{pattern}': {config['reasoning']}"
                    ))
                elif re.search(pattern, name, re.IGNORECASE):
                    matches.append(ShapeMapping(
                        shape=shape,
                        confidence=self.pattern_weights['contains_match'],
                        reasoning=f"Name '{name}' contains pattern '{pattern}': {config['reasoning']}"
                    ))

        return matches

    def _analyze_component_type(self, component: Component) -> ShapeMapping:
        """Analyze component type for shape determination"""
        if component.type == ComponentType.CLASS:
            return ShapeMapping(
                shape='class',
                confidence=0.8,
                reasoning='Class components use class shape for better representation'
            )
        elif component.type == ComponentType.FUNCTION:
            return ShapeMapping(
                shape='rectangle',
                confidence=0.7,
                reasoning='Function components use rectangle shape'
            )
        else:
            return ShapeMapping(
                shape='rectangle',
                confidence=0.5,
                reasoning='Unknown component type uses default rectangle'
            )

    def _analyze_methods(self, methods: List[str]) -> List[ShapeMapping]:
        """Analyze method names to infer component purpose"""
        matches = []

        if not methods:
            return matches

        method_indicators = {
            'database': [r'save', r'load', r'delete', r'find', r'query', r'insert', r'update'],
            'cylinder': [r'persist', r'retrieve', r'remove', r'fetch', r'store'],
            'api': [r'get', r'post', r'put', r'delete', r'patch', r'request', r'response'],
            'service': [r'process', r'handle', r'execute', r'run', r'perform', r'operate'],
            'queue': [r'queue', r'dequeue', r'publish', r'subscribe', r'send', r'receive']
        }

        method_text = ' '.join(methods).lower()

        for shape, patterns in method_indicators.items():
            for pattern in patterns:
                if re.search(pattern, method_text):
                    matches.append(ShapeMapping(
                        shape=shape,
                        confidence=self.pattern_weights['method_name_match'],
                        reasoning=f"Method names indicate {shape} functionality"
                    ))
                    break

        return matches

    def _analyze_imports(self, imports: List[str]) -> List[ShapeMapping]:
        """Analyze import statements to infer component type"""
        matches = []

        if not imports:
            return matches

        import_indicators = {
            'database': [r'sqlalchemy', r'django\.db', r'psycopg2', r'mysql', r'mongodb'],
            'cloud': [r'aws', r'azure', r'gcp', r'boto3', r'google\.cloud'],
            'queue': [r'celery', r'rq', r'pika', r'kafka', r'redis'],
            'api': [r'flask', r'django', r'fastapi', r'requests', r'httpx'],
            'document': [r'yaml', r'json', r'toml', r'configparser']
        }

        import_text = ' '.join(imports).lower()

        for shape, patterns in import_indicators.items():
            for pattern in patterns:
                if re.search(pattern, import_text):
                    matches.append(ShapeMapping(
                        shape=shape,
                        confidence=self.pattern_weights['import_analysis_match'],
                        reasoning=f"Import statements indicate {shape} dependencies"
                    ))
                    break

        return matches

    def _get_style_overrides(self, shape: str) -> Dict[str, str]:
        """Get style overrides for specific shapes"""
        style_overrides = {
            'class': {
                'style.fill': '#f2f2f2',
                'style.stroke': '#a3a3a3',
                'style.shadow': 'true',
                'style.font-color': '#333333',
                'style.border-radius': '8'
            },
            'cylinder': {
                'style.fill': '#e0f2f7',
                'style.stroke': '#7fc8e0',
                'style.shadow': 'true',
                'style.font-color': '#333333'
            },
            'person': {
                'style.fill': '#ffe0b2',
                'style.stroke': '#ff9800',
                'style.font-color': '#333333'
            },
            'cloud': {
                'style.fill': '#e0e0e0',
                'style.stroke': '#9e9e9e',
                'style.font-color': '#333333'
            },
            'hexagon': {
                'style.fill': '#f3e5f5',
                'style.stroke': '#9c27b0',
                'style.font-color': '#333333'
            },
            'queue': {
                'shape': 'trapezoid',
                'style.fill': '#fff3e0',
                'style.stroke': '#ff9800',
                'style.font-color': '#333333'
            },
            'document': {
                'style.fill': '#fff8e1',
                'style.stroke': '#ffc107',
                'style.font-color': '#333333'
            },
            'stored_data': {
                'style.fill': '#e8f5e8',
                'style.stroke': '#4caf50',
                'style.font-color': '#333333'
            },
            'diamond': {
                'style.fill': '#fce4ec',
                'style.stroke': '#e91e63',
                'style.font-color': '#333333'
            }
        }

        return style_overrides.get(shape, {})

    def get_shape_hierarchy(self, components: List[Component]) -> Dict[str, List[str]]:
        """
        Determine hierarchical relationships between components based on their shapes

        Args:
            components: List of components to analyze

        Returns:
            Dictionary mapping parent shapes to child shapes
        """
        hierarchy = {}

        # Group components by shape
        shape_groups = {}
        for component in components:
            shape_mapping = self.analyze_component_shape(component)
            shape = shape_mapping.shape

            if shape not in shape_groups:
                shape_groups[shape] = []
            shape_groups[shape].append(component.name)

        # Define hierarchical relationships
        shape_hierarchy = {
            'person': ['cloud', 'class'],  # Users interact with external systems and services
            'cloud': ['class'],            # External systems contain services
            'class': ['cylinder', 'queue', 'stored_data'],  # Services use databases and queues
            'diamond': ['class'],          # Infrastructure manages services
            'hexagon': ['class'],          # Security components protect services
        }

        # Build hierarchy based on relationships
        for parent_shape, child_shapes in shape_hierarchy.items():
            if parent_shape in shape_groups:
                hierarchy[parent_shape] = []
                for child_shape in child_shapes:
                    if child_shape in shape_groups:
                        hierarchy[parent_shape].extend(shape_groups[child_shape])

        return hierarchy