"""
Evaluation Agent - Assesses diagram quality and provides improvement suggestions.
"""

import re
from typing import List, Dict, Any, Tuple
from data_models import (
    D2Generation, DiagramDesign, CodeAnalysisResult, CodeComponent,
    ComponentType, RelationshipType
)


class EvaluationAgent:
    """Evaluates the quality of generated D2 diagrams and provides improvement suggestions."""

    def __init__(self):
        self.name = "EvaluationAgent"

    def evaluate_diagram_quality(self, d2_generation: D2Generation,
                               diagram_design: DiagramDesign,
                               analysis_result: CodeAnalysisResult) -> Dict[str, Any]:
        """Comprehensive evaluation of diagram quality."""

        # Calculate quality scores
        clarity_score = self._evaluate_clarity(d2_generation, diagram_design)
        completeness_score = self._evaluate_completeness(d2_generation, diagram_design, analysis_result)
        structure_score = self._evaluate_structure(d2_generation, diagram_design)
        readability_score = self._evaluate_readability(d2_generation)
        semantic_quality_score = self._evaluate_semantic_quality(d2_generation, diagram_design, analysis_result)

        # Calculate overall quality score
        overall_score = (
            clarity_score * 0.25 +
            completeness_score * 0.20 +
            structure_score * 0.20 +
            readability_score * 0.15 +
            semantic_quality_score * 0.20
        )

        # Generate improvement suggestions
        suggestions = self._generate_improvement_suggestions(
            d2_generation, diagram_design, analysis_result,
            clarity_score, completeness_score, structure_score, readability_score, semantic_quality_score
        )

        # Determine if diagram meets quality standards (adjusted thresholds for Version 2.0)
        meets_standards = overall_score >= 0.65 and readability_score >= 0.35

        return {
            "overall_score": round(overall_score, 2),
            "meets_quality_standards": meets_standards,
            "quality_breakdown": {
                "clarity": round(clarity_score, 2),
                "completeness": round(completeness_score, 2),
                "structure": round(structure_score, 2),
                "readability": round(readability_score, 2),
                "semantic_quality": round(semantic_quality_score, 2)
            },
            "suggestions": suggestions,
            "detailed_analysis": self._get_detailed_analysis(d2_generation, diagram_design, analysis_result)
        }

    def _evaluate_clarity(self, d2_generation: D2Generation, diagram_design: DiagramDesign) -> float:
        """Evaluate how clear and understandable the diagram is."""
        score = 0.0

        # Check for meaningful component names
        d2_code = d2_generation.d2_code
        component_names = re.findall(r'"([^"]+)"\s*{', d2_code)

        if component_names:
            # Penalize single-letter or very short names
            meaningful_names = sum(1 for name in component_names if len(name) > 2)
            score += (meaningful_names / len(component_names)) * 0.3

            # Bonus for descriptive names (camelCase, snake_case)
            descriptive_names = sum(1 for name in component_names
                                  if re.match(r'^[a-zA-Z][a-zA-Z0-9_]{2,}$', name))
            score += (descriptive_names / len(component_names)) * 0.4

        # Check for proper grouping
        groups = re.findall(r'"([^"]+)"\s*{[^}]*"([^"]+)"', d2_code)
        if groups:
            score += min(len(groups) / 5, 1.0) * 0.3

        return min(score, 1.0)

    def _evaluate_completeness(self, d2_generation: D2Generation, diagram_design: DiagramDesign,
                              analysis_result: CodeAnalysisResult) -> float:
        """Evaluate how complete the diagram representation is."""
        score = 0.0

        total_components = len(analysis_result.components)
        included_components = len(d2_generation.components_used)

        if total_components > 0:
            # Check component coverage
            coverage_ratio = min(included_components / min(total_components, 25), 1.0)
            score += coverage_ratio * 0.4

            # Check if important components are included
            classes = [c for c in analysis_result.components if c.type == ComponentType.CLASS]
            included_classes = sum(1 for c in classes if c.name in d2_generation.components_used)

            if classes:
                class_coverage = min(included_classes / len(classes), 1.0)
                score += class_coverage * 0.6

        return min(score, 1.0)

    def _evaluate_structure(self, d2_generation: D2Generation, diagram_design: DiagramDesign) -> float:
        """Evaluate the structural organization of the diagram."""
        score = 0.0

        d2_code = d2_generation.d2_code

        # Check for hierarchical structure
        if diagram_design.layout_strategy.value == "hierarchical":
            relationships = re.findall(r'"[^"]+"\s*->\s*"[^"]+"', d2_code)
            if relationships:
                score += min(len(relationships) / 10, 1.0) * 0.3

        # Check for logical grouping
        groups = re.findall(r'"group_\w+"\s*{', d2_code)
        if groups:
            score += min(len(groups) / 5, 1.0) * 0.3

        # Check for proper use of D2 structure
        if "direction:" in d2_code:
            score += 0.2

        # Check for consistent styling
        if "style.fill:" in d2_code:
            score += 0.2

        return min(score, 1.0)

    def _evaluate_readability(self, d2_generation: D2Generation) -> float:
        """Evaluate the readability and visual clarity of the diagram."""
        score = 0.0

        d2_code = d2_generation.d2_code
        lines = d2_code.splitlines()

        # Check for reasonable complexity
        component_count = len(re.findall(r'"[^"]+"\s*{', d2_code))

        if component_count <= 10:
            score += 0.4
        elif component_count <= 20:
            score += 0.3
        elif component_count <= 30:
            score += 0.1

        # Check for proper spacing and organization
        empty_lines = sum(1 for line in lines if line.strip() == "")
        if empty_lines >= len(lines) * 0.2:
            score += 0.2

        # Check for comments and documentation
        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        if comment_lines >= 3:
            score += 0.2

        # Check for consistent formatting
        properly_indented = sum(1 for line in lines if line.strip() and (line.startswith('  ') or line.startswith('"')))
        non_empty_lines = [l for l in lines if l.strip()]
        if properly_indented > 0 and len(non_empty_lines) > 0:
            indentation_ratio = properly_indented / len(non_empty_lines)
            score += indentation_ratio * 0.2

        return min(score, 1.0)

    def _evaluate_semantic_quality(self, d2_generation: D2Generation, diagram_design: DiagramDesign,
                                 analysis_result: CodeAnalysisResult) -> float:
        """Evaluate the semantic correctness and meaningfulness of the diagram."""
        score = 0.0

        # Check for appropriate diagram type
        has_classes = any(c.type == ComponentType.CLASS for c in analysis_result.components)
        has_functions = any(c.type == ComponentType.FUNCTION for c in analysis_result.components)

        if has_classes and diagram_design.diagram_type.value == "class":
            score += 0.4
        elif has_functions and diagram_design.diagram_type.value == "flow":
            score += 0.4
        else:
            score += 0.2

        # Check relationship accuracy
        relationships = []
        for comp in analysis_result.components:
            for rel in comp.relationships:
                if (rel.source in d2_generation.components_used and
                    rel.target in d2_generation.components_used):
                    relationships.append(rel)

        # Check for inheritance relationships
        inheritance_rels = [r for r in relationships if r.type == RelationshipType.INHERITANCE]
        if inheritance_rels:
            score += 0.3

        # Check for logical connections
        if len(relationships) > 0:
            score += 0.3

        return min(score, 1.0)

    def _generate_improvement_suggestions(self, d2_generation: D2Generation, diagram_design: DiagramDesign,
                                         analysis_result: CodeAnalysisResult,
                                         clarity_score: float, completeness_score: float,
                                         structure_score: float, readability_score: float,
                                         semantic_quality_score: float) -> List[str]:
        """Generate specific improvement suggestions based on evaluation."""
        suggestions = []

        # Clarity suggestions
        if clarity_score < 0.7:
            if clarity_score < 0.4:
                suggestions.append("CRITICAL: Component names are unclear. Use descriptive, meaningful names.")
            suggestions.append("Improve clarity: Use longer, more descriptive component names.")

        # Completeness suggestions
        if completeness_score < 0.7:
            if completeness_score < 0.4:
                suggestions.append("CRITICAL: Many important components are missing from the diagram.")
            suggestions.append("Include more important classes and functions to improve completeness.")

        # Structure suggestions
        if structure_score < 0.7:
            if structure_score < 0.4:
                suggestions.append("CRITICAL: Diagram lacks proper structure and organization.")
            suggestions.append("Improve structure: Add logical grouping and better hierarchy.")

        # Readability suggestions
        if readability_score < 0.6:
            if readability_score < 0.3:
                suggestions.append("CRITICAL: Diagram is too complex and unreadable.")
            suggestions.append("Reduce complexity: Limit to 15-20 components for better readability.")

        # Semantic quality suggestions
        if semantic_quality_score < 0.7:
            suggestions.append("Improve semantic accuracy: Ensure relationships correctly represent the code.")

        # General suggestions
        component_count = len(re.findall(r'"[^"]+"\s*{', d2_generation.d2_code))
        if component_count > 25:
            suggestions.append("Consider splitting into multiple diagrams for better readability.")
        if component_count < 5:
            suggestions.append("Consider including more components for a more comprehensive view.")

        return suggestions

    def _get_detailed_analysis(self, d2_generation: D2Generation, diagram_design: DiagramDesign,
                             analysis_result: CodeAnalysisResult) -> Dict[str, Any]:
        """Get detailed analysis for debugging and improvement."""
        d2_code = d2_generation.d2_code

        return {
            "component_count": len(re.findall(r'"[^"]+"\s*{', d2_code)),
            "relationship_count": len(re.findall(r'"[^"]+"\s*->\s*"[^"]+"', d2_code)),
            "group_count": len(re.findall(r'"group_\w+"', d2_code)),
            "line_count": len(d2_code.splitlines()),
            "diagram_type": diagram_design.diagram_type.value,
            "layout_strategy": diagram_design.layout_strategy.value,
            "components_by_type": {
                "classes": len([c for c in analysis_result.components if c.type == ComponentType.CLASS]),
                "functions": len([c for c in analysis_result.components if c.type == ComponentType.FUNCTION]),
                "variables": len([c for c in analysis_result.components if c.type == ComponentType.VARIABLE])
            },
            "complexity_metrics": {
                "avg_component_name_length": self._get_avg_name_length(d2_code),
                "has_comments": "#" in d2_code,
                "has_styling": "style." in d2_code
            }
        }

    def _get_avg_name_length(self, d2_code: str) -> float:
        """Calculate average component name length."""
        names = re.findall(r'"([^"]+)"\s*{', d2_code)
        if not names:
            return 0.0
        return sum(len(name) for name in names) / len(names)