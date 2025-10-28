"""
Orchestrator Agent - Version 3.0

Enhanced orchestrator for V3.0 with new agents and improved workflow.
Coordinates all agents to generate professional D2 diagrams.
"""

import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

from data_models import (
    CodeComponent as Component,
    Relationship,
    DiagramDesign,
    ValidationResult,
    DiagramType,
    ComponentType,
    LayoutStrategy
)
from agents.code_analysis_agent import CodeAnalysisAgent
from agents.diagram_design_agent_v3 import DiagramDesignAgentV3
from agents.d2_generation_agent_v3 import D2GenerationAgentV3
from agents.reflection_agent import ReflectionAgent
from agents.evaluation_agent import EvaluationAgent
from agents.shape_intelligence_agent import ShapeIntelligenceAgent
from shape_library import ProfessionalShapeLibrary

@dataclass
class GenerationResult:
    """Simple generation result for V3.0"""
    d2_code: str
    validation_result: ValidationResult
    generation_time: float
    quality_score: float
    success: bool

@dataclass
class SimpleD2Generation:
    """Simple wrapper for D2 generation validation"""
    d2_code: str
    diagram_type: str = "class"
    layout_strategy: str = "hierarchical"
    components_used: List[str] = None
    generation_metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.components_used is None:
            self.components_used = []
        if self.generation_metadata is None:
            self.generation_metadata = {}

@dataclass
class V3GenerationResult:
    """Enhanced generation result for V3.0"""
    generation_result: GenerationResult
    shapes_used: List[str]
    layout_engine: str
    theme_used: str
    quality_breakdown: Dict[str, float]
    generation_stats: Dict[str, Any]
    validation_errors: List[str]

class OrchestratorAgentV3:
    """
    Enhanced orchestrator for V3.0 with professional diagram generation capabilities.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = self._setup_logger()

        # Initialize V3.0 agents
        self.code_analysis_agent = CodeAnalysisAgent()
        self.diagram_design_agent = DiagramDesignAgentV3()
        self.d2_generation_agent = D2GenerationAgentV3()
        self.reflection_agent = ReflectionAgent()
        self.evaluation_agent = EvaluationAgent()

        # V3.0 specific components
        self.shape_intelligence = ShapeIntelligenceAgent()
        self.shape_library = ProfessionalShapeLibrary()

        # Generation statistics
        self.generation_stats = {
            'total_generations': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'average_quality': 0.0,
            'most_used_layouts': {},
            'most_used_themes': {}
        }

    def _setup_logger(self) -> logging.Logger:
        """Setup logging for the orchestrator"""
        logger = logging.getLogger("OrchestratorV3")
        logger.setLevel(logging.INFO if self.verbose else logging.WARNING)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def generate_diagram(self, file_path: str = None, repository_path: str = None,
                        output_path: str = "diagram_v3.d2",
                        user_preferences: Dict = None) -> V3GenerationResult:
        """
        Generate a professional D2 diagram using V3.0 architecture

        Args:
            file_path: Path to single Python file
            repository_path: Path to repository directory
            output_path: Output path for generated diagram
            user_preferences: User preferences for styling and layout

        Returns:
            V3GenerationResult with comprehensive generation information
        """
        start_time = time.time()
        user_preferences = user_preferences or {}

        try:
            self.logger.info(f"Starting V3.0 diagram generation for {file_path or repository_path}")

            # Phase 1: Code Analysis
            self.logger.info("Phase 1: Analyzing code...")
            components, relationships = self._analyze_code(file_path, repository_path)

            if not components:
                raise ValueError("No components found in the provided code")

            # Phase 2: Intelligent Diagram Design
            self.logger.info("Phase 2: Designing diagram layout...")
            design = self._design_diagram(components, relationships, user_preferences)

            # Phase 3: Professional D2 Generation
            self.logger.info("Phase 3: Generating D2 code...")
            d2_result = self._generate_d2(design, components, relationships)

            # Phase 4: Reflection and Validation
            self.logger.info("Phase 4: Validating D2 generation...")
            validation_result = self._validate_generation(d2_result.d2_code, design)

            # Phase 5: Quality Evaluation
            self.logger.info("Phase 5: Evaluating diagram quality...")
            try:
                evaluation_result = self._evaluate_quality(
                    d2_result.d2_code, components, relationships, validation_result, design
                )
            except ZeroDivisionError as e:
                self.logger.error(f"Division by zero in quality evaluation: {e}")
                # Fallback evaluation
                evaluation_result = {
                    'overall_score': 0.5,
                    'quality_breakdown': {
                        'clarity': 0.5,
                        'completeness': 0.5,
                        'structure': 0.5,
                        'readability': 0.5,
                        'semantic_quality': 0.5
                    },
                    'validation_passed': False,
                    'validation_errors': [f"Division by zero error: {str(e)}"]
                }

            # Phase 6: Save Results
            self.logger.info("Phase 6: Saving results...")
            self._save_results(d2_result.d2_code, output_path, validation_result)

            generation_time = time.time() - start_time

            # Update statistics
            self._update_stats(d2_result, evaluation_result, generation_time)

            # Create V3.0 result
            overall_score = evaluation_result.get('overall_score', 0.0)
            quality_breakdown = evaluation_result.get('quality_breakdown', {})

            v3_result = V3GenerationResult(
                generation_result=GenerationResult(
                    d2_code=d2_result.d2_code,
                    validation_result=validation_result,
                    generation_time=generation_time,
                    quality_score=overall_score,
                    success=validation_result.is_valid and overall_score >= 0.7
                ),
                shapes_used=list(d2_result.shapes_used),
                layout_engine=d2_result.layout_engine,
                theme_used=d2_result.theme_used,
                quality_breakdown=quality_breakdown,
                generation_stats=self.generation_stats.copy(),
                validation_errors=d2_result.validation_errors
            )

            self._log_generation_summary(v3_result)
            return v3_result

        except Exception as e:
            self.logger.error(f"Generation failed: {str(e)}")
            self.generation_stats['failed_generations'] += 1

            # Generate fallback result
            return self._generate_fallback_result(str(e), start_time)

    def _analyze_code(self, file_path: str, repository_path: str) -> Tuple[List[Component], List[Relationship]]:
        """Phase 1: Code analysis"""
        if file_path:
            analysis_result = self.code_analysis_agent.analyze_file(file_path)
        elif repository_path:
            analysis_result = self.code_analysis_agent.analyze_repository(repository_path)
        else:
            raise ValueError("Either file_path or repository_path must be provided")

        # Extract relationships from components
        relationships = []
        for component in analysis_result.components:
            if hasattr(component, 'relationships') and component.relationships:
                relationships.extend(component.relationships)

        return analysis_result.components, relationships

    def _design_diagram(self, components: List[Component], relationships: List[Relationship],
                       user_preferences: Dict) -> DiagramDesign:
        """Phase 2: Intelligent diagram design"""
        return self.diagram_design_agent.design_diagram(components, relationships, user_preferences)

    def _generate_d2(self, design: DiagramDesign, components: List[Component],
                     relationships: List[Relationship]) -> Any:
        """Phase 3: Professional D2 generation"""
        # Extract V3.0 config from V2.0 compatible design
        v3_config = design.visual_settings.get('v3_config', {})
        selected_components = v3_config.get('selected_components', components)
        v3_relationships = v3_config.get('relationships', relationships)

        # Create V3.0 compatible design
        class V3DiagramDesign:
            def __init__(self, v2_design, v3_config):
                self.diagram_type = v3_config.get('layout_engine', 'hierarchical')
                self.layout_strategy = v3_config.get('layout_engine', 'hierarchical')
                self.style_theme = v2_design.visual_settings.get('theme', 'professional_blue')
                self.layout_config = v3_config.get('layout_config', {})

        v3_design = V3DiagramDesign(design, v3_config)
        return self.d2_generation_agent.generate_d2(v3_design, selected_components, v3_relationships)

    def _validate_generation(self, d2_code: str, design: DiagramDesign) -> ValidationResult:
        """Phase 4: Reflection and validation"""
        # Create a simple D2Generation wrapper for validation
        d2_gen = SimpleD2Generation(
            d2_code=d2_code,
            diagram_type=design.diagram_type,
            layout_strategy=design.layout_strategy,
            components_used=design.components_to_include,
            generation_metadata={}
        )
        return self.reflection_agent.validate_d2_generation(d2_gen, design)

    def _evaluate_quality(self, d2_code: str, components: List[Component],
                         relationships: List[Relationship],
                         validation_result: ValidationResult, design: DiagramDesign) -> Any:
        """Phase 5: Quality evaluation"""
        # Create wrappers for the expected parameters
        d2_gen = SimpleD2Generation(
            d2_code=d2_code,
            diagram_type=design.diagram_type,
            layout_strategy=design.layout_strategy,
            components_used=design.components_to_include,
            generation_metadata={}
        )

        # Create CodeAnalysisResult wrapper
        class SimpleAnalysisResult:
            def __init__(self, comps, rels):
                self.components = comps
                self.relationships = rels

        analysis_result = SimpleAnalysisResult(components, relationships)

        return self.evaluation_agent.evaluate_diagram_quality(
            d2_gen, design, analysis_result
        )

    def _save_results(self, d2_code: str, output_path: str, validation_result: ValidationResult) -> None:
        """Phase 6: Save results to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(d2_code)

            if self.verbose:
                print(f"✅ V3.0 diagram saved to: {output_path}")

            # Generate SVG if validation passes
            if validation_result.is_valid:
                self._generate_svg(d2_code, output_path)

        except Exception as e:
            self.logger.error(f"Failed to save results: {str(e)}")

    def _generate_svg(self, d2_code: str, d2_path: str) -> None:
        """Generate SVG from D2 code"""
        try:
            import subprocess
            svg_path = d2_path.replace('.d2', '.svg')

            # Use D2 to generate SVG
            result = subprocess.run(
                ['d2', d2_path, svg_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and self.verbose:
                print(f"✅ SVG generated: {svg_path}")
            elif result.returncode != 0:
                self.logger.warning(f"D2 rendering failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            self.logger.warning("D2 rendering timed out")
        except FileNotFoundError:
            self.logger.warning("D2 command not found - install D2 for SVG generation")
        except Exception as e:
            self.logger.error(f"SVG generation failed: {str(e)}")

    def _update_stats(self, d2_result: Any, evaluation_result: Any, generation_time: float) -> None:
        """Update generation statistics"""
        self.generation_stats['total_generations'] += 1

        overall_score = evaluation_result.get('overall_score', 0.0)
        if overall_score >= 0.7:
            self.generation_stats['successful_generations'] += 1

        # Update average quality
        total_successful = self.generation_stats['successful_generations']
        current_avg = self.generation_stats['average_quality']
        if total_successful > 0:
            new_avg = ((current_avg * (total_successful - 1)) + overall_score) / total_successful
            self.generation_stats['average_quality'] = round(new_avg, 3)
        else:
            self.generation_stats['average_quality'] = round(overall_score, 3)

        # Update layout and theme usage
        layout = d2_result.layout_engine
        theme = d2_result.theme_used

        if layout not in self.generation_stats['most_used_layouts']:
            self.generation_stats['most_used_layouts'][layout] = 0
        self.generation_stats['most_used_layouts'][layout] += 1

        if theme not in self.generation_stats['most_used_themes']:
            self.generation_stats['most_used_themes'][theme] = 0
        self.generation_stats['most_used_themes'][theme] += 1

    def _log_generation_summary(self, result: V3GenerationResult) -> None:
        """Log summary of generation results"""
        if not self.verbose:
            return

        print("\n" + "="*60)
        print("🎨 V3.0 DIAGRAM GENERATION COMPLETE")
        print("="*60)
        print(f"✅ Success: {result.generation_result.success}")
        print(f"📊 Quality Score: {result.generation_result.quality_score:.2f}/1.00")
        print(f"🎯 Layout Engine: {result.layout_engine}")
        print(f"🎨 Theme: {result.theme_used}")
        print(f"🔷 Shapes Used: {', '.join(result.shapes_used)}")
        print(f"⏱️  Generation Time: {result.generation_result.generation_time:.2f}s")

        if result.quality_breakdown:
            print("\n📈 Quality Breakdown:")
            for metric, score in result.quality_breakdown.items():
                emoji = "🏆" if score >= 0.8 else "✅" if score >= 0.6 else "⚠️" if score >= 0.4 else "❌"
                print(f"  {emoji} {metric}: {score:.2f}")

        if result.validation_errors:
            print(f"\n⚠️  Validation Warnings: {len(result.validation_errors)}")
            for error in result.validation_errors[:3]:  # Show first 3 errors
                print(f"    • {error}")

        print("="*60)

    def _generate_fallback_result(self, error_message: str, start_time: float) -> V3GenerationResult:
        """Generate fallback result for failed generations"""
        fallback_d2 = """# Fallback Diagram - V3.0 Generation Failed
# Error: """ + error_message + """

direction: down

Error {
  shape: rectangle
  style.fill: "#ffebee"
  style.stroke: "#f44336"
  label: "Generation Failed\\n""" + error_message + """"
}

Note {
  shape: document
  style.fill: "#fff3e0"
  style.stroke: "#ff9800"
  label: "Please check your input\\nand try again."
}

Error -> Note
"""

        generation_time = time.time() - start_time

        return V3GenerationResult(
            generation_result=GenerationResult(
                d2_code=fallback_d2,
                validation_result=ValidationResult(
                    is_valid=False,
                    can_render=False,
                    syntax_errors=[error_message],
                    warnings=["Using fallback diagram"]
                ),
                generation_time=generation_time,
                quality_score=0.0,
                success=False
            ),
            shapes_used=['rectangle', 'document'],
            layout_engine='hierarchical',
            theme_used='professional_blue',
            quality_breakdown={},
            generation_stats=self.generation_stats.copy(),
            validation_errors=[error_message]
        )

    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get comprehensive generation statistics"""
        return {
            **self.generation_stats,
            'success_rate': (
                self.generation_stats['successful_generations'] /
                max(self.generation_stats['total_generations'], 1)
            ) * 100
        }

    def preview_design_recommendations(self, file_path: str = None,
                                      repository_path: str = None) -> Dict[str, Any]:
        """Preview design recommendations without full generation"""
        try:
            # Quick code analysis
            components, relationships = self._analyze_code(file_path, repository_path)

            # Get design recommendations
            recommendations = self.diagram_design_agent.get_design_recommendations(
                components, relationships
            )

            return {
                'components_found': len(components),
                'relationships_found': len(relationships),
                'recommendations': recommendations,
                'estimated_generation_time': '5-10 seconds'
            }

        except Exception as e:
            return {
                'error': str(e),
                'recommendations': None
            }