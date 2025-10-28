"""
Orchestrator Agent - Coordinates the workflow between agents.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import time

from data_models import (
    AgentMessage, CodeAnalysisResult, DiagramDesign, D2Generation, ValidationResult
)
from agents.code_analysis_agent import CodeAnalysisAgent
from agents.diagram_design_agent import DiagramDesignAgent
from agents.d2_generation_agent import D2GenerationAgent
from agents.reflection_agent import ReflectionAgent
from agents.evaluation_agent import EvaluationAgent


class OrchestratorAgent:
    """Coordinates the workflow between all agents."""

    def __init__(self):
        self.name = "OrchestratorAgent"
        self.code_analysis_agent = CodeAnalysisAgent()
        self.diagram_design_agent = DiagramDesignAgent()
        self.d2_generation_agent = D2GenerationAgent()
        self.reflection_agent = ReflectionAgent()
        self.evaluation_agent = EvaluationAgent()

        # Workflow state
        self.workflow_state = {
            "current_step": "initialized",
            "messages": [],
            "results": {},
            "errors": [],
            "start_time": None,
            "end_time": None
        }

    def generate_diagram_from_file(self, file_path: str, max_retries: int = 3, output_dir: str = ".") -> Dict[str, Any]:
        """Generate a D2 diagram from a single Python file."""
        self.workflow_state["start_time"] = time.time()
        self.workflow_state["current_step"] = "processing_file"

        try:
            # Step 1: Code Analysis
            self.workflow_state["current_step"] = "code_analysis"
            analysis_result = self.code_analysis_agent.analyze_file(file_path)
            self.workflow_state["results"]["analysis"] = analysis_result

            if analysis_result.metadata.get("error"):
                return self._create_error_result("Code analysis failed", analysis_result.metadata["error"])

            # Continue with workflow
            return self._continue_workflow(analysis_result, max_retries, output_dir)

        except Exception as e:
            return self._create_error_result("Unexpected error during file processing", str(e))

    def generate_diagram_from_repository(self, repo_path: str, max_retries: int = 3, output_dir: str = ".") -> Dict[str, Any]:
        """Generate a D2 diagram from a Python repository."""
        self.workflow_state["start_time"] = time.time()
        self.workflow_state["current_step"] = "processing_repository"

        try:
            # Step 1: Code Analysis
            self.workflow_state["current_step"] = "code_analysis"
            analysis_result = self.code_analysis_agent.analyze_repository(repo_path)
            self.workflow_state["results"]["analysis"] = analysis_result

            if analysis_result.metadata.get("error"):
                return self._create_error_result("Repository analysis failed", analysis_result.metadata["error"])

            # Continue with workflow
            return self._continue_workflow(analysis_result, max_retries, output_dir)

        except Exception as e:
            return self._create_error_result("Unexpected error during repository processing", str(e))

    def _continue_workflow(self, analysis_result: CodeAnalysisResult, max_retries: int, output_dir: str) -> Dict[str, Any]:
        """Continue the workflow after code analysis."""
        retries = 0

        while retries <= max_retries:
            try:
                # Step 2: Diagram Design
                self.workflow_state["current_step"] = "diagram_design"
                diagram_design = self.diagram_design_agent.design_diagram(analysis_result)
                self.workflow_state["results"]["design"] = diagram_design

                # Step 3: D2 Generation
                self.workflow_state["current_step"] = "d2_generation"
                d2_generation = self.d2_generation_agent.generate_d2(analysis_result, diagram_design)
                self.workflow_state["results"]["generation"] = d2_generation

                # Step 4: Reflection/Validation with SVG generation
                self.workflow_state["current_step"] = "reflection"
                validation_result = self.reflection_agent.validate_d2_generation(d2_generation, diagram_design, output_dir)
                self.workflow_state["results"]["validation"] = validation_result

                # Step 5: Quality Evaluation
                if validation_result.is_valid:
                    self.workflow_state["current_step"] = "evaluation"
                    evaluation_result = self.evaluation_agent.evaluate_diagram_quality(
                        d2_generation, diagram_design, analysis_result
                    )
                    self.workflow_state["results"]["evaluation"] = evaluation_result

                    # Check if quality meets standards
                    if evaluation_result["meets_quality_standards"]:
                        self.workflow_state["current_step"] = "completed"
                        self.workflow_state["end_time"] = time.time()
                        return self._create_success_result_v2(analysis_result, diagram_design, d2_generation, validation_result, evaluation_result)
                    else:
                        # Quality is too low, provide feedback
                        if retries < max_retries:
                            self.workflow_state["errors"].append(f"Quality below standards (attempt {retries + 1}): {evaluation_result['suggestions'][:2]}")
                            retries += 1
                            # Could implement quality improvement logic here
                            continue
                        else:
                            return self._create_quality_failed_result(analysis_result, diagram_design, d2_generation, validation_result, evaluation_result)

                # If validation failed, try to fix issues
                if retries < max_retries:
                    self.workflow_state["errors"].append(f"Validation failed (attempt {retries + 1}): {validation_result.syntax_errors}")
                    retries += 1
                    # Could implement retry logic here with adjustments
                    continue
                else:
                    return self._create_validation_failed_result(analysis_result, diagram_design, d2_generation, validation_result)

            except Exception as e:
                if retries < max_retries:
                    self.workflow_state["errors"].append(f"Workflow error (attempt {retries + 1}): {str(e)}")
                    retries += 1
                    continue
                else:
                    return self._create_error_result("Workflow failed after retries", str(e))

        return self._create_error_result("Unexpected workflow termination", "Max retries exceeded")

    def _create_quality_failed_result(self, analysis_result: CodeAnalysisResult,
                                     diagram_design: DiagramDesign,
                                     d2_generation: D2Generation,
                                     validation_result: ValidationResult,
                                     evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create a result for failed quality evaluation."""
        return {
            "success": False,
            "version": "2.0",
            "error_type": "quality_failed",
            "workflow_state": self.workflow_state,
            "analysis_result": analysis_result,
            "diagram_design": diagram_design,
            "d2_generation": d2_generation,
            "validation_result": validation_result,
            "evaluation_result": evaluation_result,
            "execution_time_seconds": time.time() - self.workflow_state["start_time"],
            "quality_score": evaluation_result["overall_score"],
            "quality_breakdown": evaluation_result["quality_breakdown"],
            "suggestions": evaluation_result["suggestions"]
        }

    def _create_success_result(self, analysis_result: CodeAnalysisResult,
                             diagram_design: DiagramDesign,
                             d2_generation: D2Generation,
                             validation_result: ValidationResult) -> Dict[str, Any]:
        """Create a successful workflow result (Version 1 fallback)."""
        return {
            "success": True,
            "version": "1.0",
            "workflow_state": self.workflow_state,
            "analysis_result": analysis_result,
            "diagram_design": diagram_design,
            "d2_generation": d2_generation,
            "validation_result": validation_result,
            "execution_time_seconds": time.time() - self.workflow_state["start_time"],
            "summary": {
                "components_analyzed": len(analysis_result.components),
                "components_in_diagram": len(d2_generation.components_used),
                "diagram_type": diagram_design.diagram_type.value,
                "layout_strategy": diagram_design.layout_strategy.value,
                "d2_lines_generated": d2_generation.generation_metadata.get("lines_generated", 0),
                "validation_passed": validation_result.is_valid,
                "can_render": validation_result.can_render,
                "warnings": len(validation_result.warnings)
            }
        }

    def _create_success_result_v2(self, analysis_result: CodeAnalysisResult,
                                 diagram_design: DiagramDesign,
                                 d2_generation: D2Generation,
                                 validation_result: ValidationResult,
                                 evaluation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create a successful Version 2 workflow result with quality evaluation."""
        return {
            "success": True,
            "version": "2.0",
            "workflow_state": self.workflow_state,
            "analysis_result": analysis_result,
            "diagram_design": diagram_design,
            "d2_generation": d2_generation,
            "validation_result": validation_result,
            "evaluation_result": evaluation_result,
            "execution_time_seconds": time.time() - self.workflow_state["start_time"],
            "summary": {
                "components_analyzed": len(analysis_result.components),
                "components_in_diagram": len(d2_generation.components_used),
                "diagram_type": diagram_design.diagram_type.value,
                "layout_strategy": diagram_design.layout_strategy.value,
                "d2_lines_generated": d2_generation.generation_metadata.get("lines_generated", 0),
                "validation_passed": validation_result.is_valid,
                "can_render": validation_result.can_render,
                "quality_score": evaluation_result["overall_score"],
                "meets_quality_standards": evaluation_result["meets_quality_standards"],
                "warnings": len(validation_result.warnings),
                "improvement_suggestions": evaluation_result["suggestions"]
            }
        }

    def _create_validation_failed_result(self, analysis_result: CodeAnalysisResult,
                                       diagram_design: DiagramDesign,
                                       d2_generation: D2Generation,
                                       validation_result: ValidationResult) -> Dict[str, Any]:
        """Create a result for failed validation."""
        return {
            "success": False,
            "error_type": "validation_failed",
            "workflow_state": self.workflow_state,
            "analysis_result": analysis_result,
            "diagram_design": diagram_design,
            "d2_generation": d2_generation,
            "validation_result": validation_result,
            "execution_time_seconds": time.time() - self.workflow_state["start_time"],
            "syntax_errors": validation_result.syntax_errors,
            "warnings": validation_result.warnings,
            "suggestions": self.reflection_agent.get_improvement_suggestions(validation_result)
        }

    def _create_error_result(self, error_type: str, error_message: str) -> Dict[str, Any]:
        """Create an error result."""
        self.workflow_state["end_time"] = time.time()
        self.workflow_state["current_step"] = "error"

        return {
            "success": False,
            "error_type": error_type,
            "error_message": error_message,
            "workflow_state": self.workflow_state,
            "execution_time_seconds": (time.time() - self.workflow_state["start_time"]) if self.workflow_state["start_time"] else 0
        }

    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status."""
        return {
            "current_step": self.workflow_state["current_step"],
            "total_errors": len(self.workflow_state["errors"]),
            "completed_steps": list(self.workflow_state["results"].keys()),
            "execution_time": (time.time() - self.workflow_state["start_time"]) if self.workflow_state["start_time"] else None
        }

    def save_d2_to_file(self, d2_generation: D2Generation, output_path: str) -> bool:
        """Save generated D2 code to a file."""
        try:
            # Ensure output directory exists
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(d2_generation.d2_code)

            return True

        except Exception as e:
            self.workflow_state["errors"].append(f"Failed to save D2 file: {str(e)}")
            return False

    def generate_workflow_report(self) -> str:
        """Generate a text report of the workflow execution."""
        if not self.workflow_state["start_time"]:
            return "No workflow has been executed yet."

        report_lines = [
            "# D2 Diagram Generation Workflow Report",
            "",
            f"**Execution Time:** {self.workflow_state.get('execution_time_seconds', 0):.2f} seconds",
            f"**Current Step:** {self.workflow_state['current_step']}",
            f"**Total Errors:** {len(self.workflow_state['errors'])}",
            "",
            "## Completed Steps:"
        ]

        for step_name, result in self.workflow_state["results"].items():
            report_lines.append(f"- ✅ {step_name.title()}: {self._get_step_summary(step_name, result)}")

        if self.workflow_state["errors"]:
            report_lines.extend([
                "",
                "## Errors:",
            ])
            for i, error in enumerate(self.workflow_state["errors"], 1):
                report_lines.append(f"{i}. {error}")

        return "\n".join(report_lines)

    def _get_step_summary(self, step_name: str, result: Any) -> str:
        """Get a summary of a workflow step result."""
        if step_name == "analysis" and hasattr(result, 'components'):
            return f"Analyzed {len(result.components)} components"
        elif step_name == "design" and hasattr(result, 'diagram_type'):
            return f"{result.diagram_type.value} diagram with {result.layout_strategy.value} layout"
        elif step_name == "generation" and hasattr(result, 'd2_code'):
            return f"Generated {len(result.d2_code.splitlines())} lines of D2 code"
        elif step_name == "validation" and hasattr(result, 'is_valid'):
            status = "✅ Valid" if result.is_valid else "❌ Invalid"
            render_status = "✅ Renderable" if result.can_render else "❌ Not renderable"
            return f"{status}, {render_status}"
        else:
            return "Completed"