"""
Reflection Agent - Validates D2 syntax and checks renderability.
"""

import os
import tempfile
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
import re

from data_models import (
    ValidationResult, D2Generation, DiagramDesign
)


class ReflectionAgent:
    """Validates generated D2 code and ensures it can be rendered."""

    def __init__(self):
        self.name = "ReflectionAgent"
        self.d2_executable = self._find_d2_executable()

    def validate_d2_generation(self, d2_generation: D2Generation,
                             diagram_design: DiagramDesign, output_dir: str = ".") -> ValidationResult:
        """Validate D2 generation comprehensively and generate SVG."""
        validation_start = time.time()

        # Step 1: Basic syntax validation
        syntax_errors = self._validate_syntax(d2_generation.d2_code)

        # Step 2: Try to render the diagram to SVG
        render_result = self._test_renderability_to_svg(d2_generation.d2_code, output_dir)

        # Step 3: Validate diagram structure
        structure_errors = self._validate_diagram_structure(
            d2_generation.d2_code, diagram_design
        )

        # Step 4: Check for common issues
        warnings = self._check_common_issues(d2_generation.d2_code)

        render_time = (time.time() - validation_start) * 1000  # Convert to milliseconds

        all_errors = syntax_errors + structure_errors

        return ValidationResult(
            is_valid=len(all_errors) == 0,
            can_render=render_result["success"],
            syntax_errors=syntax_errors,
            warnings=warnings,
            render_time_ms=render_time,
            validation_details={
                "render_success": render_result["success"],
                "render_output": render_result.get("output", ""),
                "render_error": render_result.get("error", ""),
                "svg_file": render_result.get("svg_file", ""),
                "d2_executable_found": self.d2_executable is not None,
                "structure_validation": len(structure_errors) == 0,
                "total_lines": len(d2_generation.d2_code.splitlines()),
                "components_checked": len(d2_generation.components_used)
            }
        )

    def _find_d2_executable(self) -> Optional[str]:
        """Find D2 executable in the system."""
        try:
            # Try common D2 executable names
            for cmd in ["d2", "d2.exe"]:
                result = subprocess.run(
                    [cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return cmd
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return None

    def _validate_syntax(self, d2_code: str) -> List[str]:
        """Validate basic D2 syntax."""
        errors = []
        lines = d2_code.splitlines()

        # Track braces across the entire file
        brace_count = 0

        for line_num, line in enumerate(lines, 1):
            original_line = line
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            # Count braces outside of strings
            in_string = False
            escape_next = False

            for char in original_line:
                if escape_next:
                    escape_next = False
                    continue

                if char == "\\":
                    escape_next = True
                    continue

                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue

                if not in_string:
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count < 0:
                            errors.append(f"Line {line_num}: Unmatched closing brace")
                            brace_count = 0

        if brace_count != 0:
            errors.append(f"Unmatched braces in file: {brace_count} more opening than closing")

        # Additional syntax checks
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Check for invalid characters in object names
            if "->" in line and not any(char in line for char in ['"', "'"]):
                errors.append(f"Line {line_num}: Object names should be in quotes")

            # Check for proper arrow syntax
            if "->" in line:
                parts = line.split("->", 1)  # Split only on first arrow
                if len(parts) == 2:
                    source = parts[0].strip()
                    target_part = parts[1].strip()

                    if not (source.startswith('"') and source.endswith('"')):
                        errors.append(f"Line {line_num}: Source object should be quoted")

                    # For arrow syntax, check if target is properly formatted
                    # Target can be "Target" or "Target" { ... }
                    if not target_part.startswith('"'):
                        errors.append(f"Line {line_num}: Target should start with quoted object")

        return errors

    def _test_renderability_to_svg(self, d2_code: str, output_dir: str) -> Dict[str, Any]:
        """Test if the D2 code can actually be rendered and generate SVG file."""
        if not self.d2_executable:
            return {
                "success": False,
                "error": "D2 executable not found. Please install D2 from https://d2lang.com/"
            }

        try:
            # Create temporary D2 file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.d2', delete=False) as temp_file:
                temp_file.write(d2_code)
                temp_file_path = temp_file.name

            # Create SVG output file path
            import uuid
            svg_filename = f"diagram_{uuid.uuid4().hex[:8]}.svg"
            svg_path = os.path.join(output_dir, svg_filename)

            try:
                # Try to render to SVG
                result = subprocess.run(
                    [self.d2_executable, temp_file_path, svg_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                success = result.returncode == 0 and os.path.exists(svg_path)

                # Check if SVG file has content
                if success and os.path.exists(svg_path):
                    file_size = os.path.getsize(svg_path)
                    if file_size == 0:
                        success = False
                        os.unlink(svg_path)
                        svg_path = ""
                    else:
                        # Read SVG content to verify it's valid
                        try:
                            with open(svg_path, 'r', encoding='utf-8') as f:
                                svg_content = f.read()
                                if not svg_content.strip().startswith('<svg'):
                                    success = False
                                    os.unlink(svg_path)
                                    svg_path = ""
                        except:
                            success = False
                            if os.path.exists(svg_path):
                                os.unlink(svg_path)
                            svg_path = ""

                return {
                    "success": success,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None,
                    "svg_file": svg_path if success else ""
                }

            finally:
                # Clean up temporary D2 file
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "D2 rendering timed out after 30 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error during rendering: {str(e)}"
            }

    def _validate_diagram_structure(self, d2_code: str, diagram_design: DiagramDesign) -> List[str]:
        """Validate the overall structure of the diagram."""
        errors = []
        lines = d2_code.splitlines()

        # Check if expected components are present
        components_found = set()
        for line in lines:
            # Find object definitions
            if '"' in line and '{' in line and '->' not in line:
                match = re.match(r'"([^"]+)"\s*{', line)
                if match:
                    components_found.add(match.group(1))

        expected_components = set(diagram_design.components_to_include)
        missing_components = expected_components - components_found

        for component in missing_components:
            errors.append(f"Missing expected component: {component}")

        # Check for relationships
        relationships_found = 0
        for line in lines:
            if '->' in line and not line.strip().startswith("#"):
                relationships_found += 1

        # Check if there are any obvious structural issues
        if len(components_found) > 1 and relationships_found == 0:
            errors.append("Multiple components found but no relationships defined")

        # Check for proper D2 structure
        has_direction = any("direction:" in line for line in lines)
        if not has_direction:
            errors.append("Missing direction declaration")

        return errors

    def _check_common_issues(self, d2_code: str) -> List[str]:
        """Check for common D2 issues that might not cause errors but affect quality."""
        warnings = []
        lines = d2_code.splitlines()

        # Check for very long lines
        for line_num, line in enumerate(lines, 1):
            if len(line) > 200:
                warnings.append(f"Line {line_num}: Very long line, might affect readability")

        # Check for potential naming conflicts
        object_names = []
        for line in lines:
            match = re.match(r'"([^"]+)"\s*{', line)
            if match:
                name = match.group(1)
                if name in object_names:
                    warnings.append(f"Duplicate object name: {name}")
                object_names.append(name)

        # Check for missing labels
        for line_num, line in enumerate(lines, 1):
            if '{' in line and 'label:' not in line and '->' not in line:
                # Check if this is an object definition without a label
                if '"' in line and '{' in line:
                    next_lines = lines[line_num:line_num + 5]  # Check next 5 lines
                    if not any('label:' in next_line for next_line in next_lines):
                        warnings.append(f"Line {line_num}: Object definition might be missing a label")

        # Check for potential overlapping issues
        if len(object_names) > 50:
            warnings.append("Large number of components, diagram might be crowded")

        # Check for missing styling
        has_styling = any("style:" in line or "fill:" in line for line in lines)
        if not has_styling:
            warnings.append("No styling found, diagram might lack visual clarity")

        return warnings

    def get_improvement_suggestions(self, validation_result: ValidationResult) -> List[str]:
        """Get suggestions for improving the diagram based on validation results."""
        suggestions = []

        if validation_result.syntax_errors:
            suggestions.append("Fix syntax errors before attempting to render")

        if not validation_result.can_render:
            if not validation_result.validation_details.get("d2_executable_found"):
                suggestions.append("Install D2 from https://d2lang.com/ to enable rendering validation")
            else:
                suggestions.append("Review D2 code structure and fix renderability issues")

        if validation_result.warnings:
            suggestions.append("Consider addressing warnings for better diagram quality")

        validation_details = validation_result.validation_details
        if validation_details.get("total_lines", 0) > 500:
            suggestions.append("Consider breaking down large diagrams into smaller, focused ones")

        if validation_details.get("components_checked", 0) > 20:
            suggestions.append("Consider reducing component count for better readability")

        return suggestions