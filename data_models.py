"""
Data models for the D2 diagram generator.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ComponentType(str, Enum):
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    MODULE = "module"
    VARIABLE = "variable"
    IMPORT = "import"


class RelationshipType(str, Enum):
    INHERITANCE = "inheritance"
    COMPOSITION = "composition"
    DEPENDENCY = "dependency"
    ASSOCIATION = "association"
    METHOD_CALL = "method_call"


class Relationship(BaseModel):
    """Represents a relationship between code components."""
    source: str
    target: str
    type: RelationshipType
    description: Optional[str] = None


class CodeComponent(BaseModel):
    """Represents a code component (class, function, etc.)."""
    name: str
    type: ComponentType
    file_path: str
    line_number: int
    methods: List[str] = []
    properties: List[str] = []
    imports: List[str] = []
    relationships: List[Relationship] = []
    metadata: Dict[str, Any] = {}


class CodeAnalysisResult(BaseModel):
    """Result from code analysis agent."""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    components: List[CodeComponent] = Field(default_factory=list)
    file_count: int = 0
    language: str = "python"
    complexity_score: float = 0.0


class DiagramType(str, Enum):
    CLASS = "class"
    ARCHITECTURE = "architecture"
    FLOW = "flow"
    SEQUENCE = "sequence"


class LayoutStrategy(str, Enum):
    HIERARCHICAL = "hierarchical"
    CIRCULAR = "circular"
    LAYERED = "layered"
    GRID = "grid"


class DiagramDesign(BaseModel):
    """Design specification for the diagram."""
    diagram_type: DiagramType
    layout_strategy: LayoutStrategy
    components_to_include: List[str] = []
    grouping_strategy: Dict[str, List[str]] = Field(default_factory=dict)
    visual_settings: Dict[str, Any] = Field(default_factory=dict)


class D2Generation(BaseModel):
    """Generated D2 code and metadata."""
    d2_code: str
    diagram_type: DiagramType
    layout_strategy: LayoutStrategy
    components_used: List[str] = []
    generation_metadata: Dict[str, Any] = Field(default_factory=dict)


class ValidationResult(BaseModel):
    """Result from reflection agent validation."""
    is_valid: bool
    can_render: bool
    syntax_errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    render_time_ms: Optional[float] = None
    validation_details: Dict[str, Any] = Field(default_factory=dict)


class AgentMessage(BaseModel):
    """Message passed between agents."""
    sender: str
    receiver: str
    message_type: str
    data: Dict[str, Any]
    timestamp: Optional[str] = None