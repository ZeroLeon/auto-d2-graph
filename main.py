#!/usr/bin/env python3
"""
Main CLI interface for the Agentic D2 Diagram Generator.
"""

import click
import os
import sys
from pathlib import Path

from agents.orchestrator_agent import OrchestratorAgent


@click.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='Python file to analyze')
@click.option('--repository', '-r', type=click.Path(exists=True, file_okay=False), help='Python repository to analyze')
@click.option('--output', '-o', default='output.d2', help='Output D2 file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--max-retries', default=3, help='Maximum number of retry attempts')
@click.option('--report', is_flag=True, help='Generate workflow report')
def main(file, repository, output, verbose, max_retries, report):
    """
    Agentic D2 Diagram Generator

    Automatically generates D2 diagrams from Python code with reflection and validation.

    Examples:

        # Analyze a single file
        python main.py --file test_sample_code.py --output my_diagram.d2

        # Analyze a repository
        python main.py --repository ./my_project --output project_diagram.d2

        # Generate with verbose output
        python main.py --file test_sample_code.py --verbose

        # Generate workflow report
        python main.py --file test_sample_code.py --report
    """
    # Validate input
    if not file and not repository:
        click.echo("Error: Please provide either --file or --repository", err=True)
        sys.exit(1)

    if file and repository:
        click.echo("Error: Please provide either --file or --repository, not both", err=True)
        sys.exit(1)

    # Initialize orchestrator
    orchestrator = OrchestratorAgent()

    try:
        # Determine output directory
        output_path = Path(output)
        output_dir = output_path.parent

        # Generate diagram
        if file:
            click.echo(f"🔍 Analyzing Python file: {file}")
            result = orchestrator.generate_diagram_from_file(file, max_retries, str(output_dir))
        else:
            click.echo(f"🔍 Analyzing Python repository: {repository}")
            result = orchestrator.generate_diagram_from_repository(repository, max_retries, str(output_dir))

        # Display results
        if result["success"]:
            _display_success_result(result, verbose)

            # Save D2 file
            if orchestrator.save_d2_to_file(result["d2_generation"], output):
                click.echo(f"\n📁 D2 diagram saved to: {output}")
            else:
                click.echo(f"\n❌ Failed to save D2 file to: {output}", err=True)

            # Generate report if requested
            if report:
                report_content = orchestrator.generate_workflow_report()
                report_path = output.replace('.d2', '_report.md')
                try:
                    with open(report_path, 'w') as f:
                        f.write(report_content)
                    click.echo(f"📊 Workflow report saved to: {report_path}")
                except Exception as e:
                    click.echo(f"⚠️  Failed to save report: {e}", err=True)

        else:
            _display_error_result(result, verbose)

            # Still save the D2 file for debugging even if validation failed
            if "d2_generation" in result:
                if orchestrator.save_d2_to_file(result["d2_generation"], output):
                    click.echo(f"\n📁 D2 diagram (with validation errors) saved to: {output}")

            sys.exit(1)

    except KeyboardInterrupt:
        click.echo("\n⚠️  Process interrupted by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def _display_success_result(result, verbose):
    """Display successful generation results."""
    summary = result["summary"]
    validation = result["validation_result"]

    # Check if this is Version 2.0 with quality evaluation
    is_v2 = result.get("version") == "2.0"

    click.echo(f"\n✅ Diagram generated successfully! (Version {result.get('version', '1.0')})")
    click.echo(f"📊 Summary:")
    click.echo(f"   • Components analyzed: {summary['components_analyzed']}")
    click.echo(f"   • Components in diagram: {summary['components_in_diagram']}")
    click.echo(f"   • Diagram type: {summary['diagram_type']}")
    click.echo(f"   • Layout strategy: {summary['layout_strategy']}")
    click.echo(f"   • D2 lines generated: {summary['d2_lines_generated']}")
    click.echo(f"   • Execution time: {result['execution_time_seconds']:.2f}s")

    if validation.is_valid:
        click.echo(f"   • ✅ Validation passed")
    else:
        click.echo(f"   • ⚠️  Validation warnings present")

    if validation.can_render:
        click.echo(f"   • ✅ Renderable to SVG")
        svg_file = validation.validation_details.get("svg_file", "")
        if svg_file:
            click.echo(f"   • 📄 SVG generated: {svg_file}")
    else:
        click.echo(f"   • ❌ Not renderable")

    # Version 2.0 specific information
    if is_v2:
        quality_score = summary.get("quality_score", 0)
        meets_standards = summary.get("meets_quality_standards", False)

        if quality_score >= 0.8:
            click.echo(f"   • 🏆 Excellent quality: {quality_score:.2f}/1.00")
        elif quality_score >= 0.7:
            click.echo(f"   • ✅ Good quality: {quality_score:.2f}/1.00")
        elif quality_score >= 0.6:
            click.echo(f"   • ⚠️  Fair quality: {quality_score:.2f}/1.00")
        else:
            click.echo(f"   • ❌ Poor quality: {quality_score:.2f}/1.00")

        if meets_standards:
            click.echo(f"   • ✅ Meets quality standards")
        else:
            click.echo(f"   • ⚠️  Below quality standards")

        suggestions = summary.get("improvement_suggestions", [])
        if suggestions:
            click.echo(f"   • 💡 {len(suggestions)} improvement suggestions available")
            if verbose:
                click.echo("\n💡 Improvement Suggestions:")
                for suggestion in suggestions[:5]:  # Show first 5
                    click.echo(f"   - {suggestion}")

    if validation.warnings:
        click.echo(f"   • Warnings: {len(validation.warnings)}")
        if verbose:
            click.echo("\n⚠️  Warnings:")
            for warning in validation.warnings:
                click.echo(f"   - {warning}")

    if verbose:
        _display_verbose_details(result)


def _display_error_result(result, verbose):
    """Display error results."""
    click.echo(f"\n❌ Diagram generation failed!")
    click.echo(f"🔍 Error type: {result['error_type']}")

    is_quality_failure = result.get("error_type") == "quality_failed"

    if 'error_message' in result:
        click.echo(f"💬 Error message: {result['error_message']}")

    # Quality failure specific information
    if is_quality_failure:
        quality_score = result.get("quality_score", 0)
        click.echo(f"📊 Quality Score: {quality_score:.2f}/1.00")

        quality_breakdown = result.get("quality_breakdown", {})
        if quality_breakdown:
            click.echo(f"\n📈 Quality Breakdown:")
            for aspect, score in quality_breakdown.items():
                score_emoji = "✅" if score >= 0.7 else "⚠️" if score >= 0.5 else "❌"
                click.echo(f"   {score_emoji} {aspect.title()}: {score:.2f}")

    if result.get("syntax_errors"):
        click.echo(f"\n📝 Syntax errors:")
        for error in result["syntax_errors"]:
            click.echo(f"   • {error}")

    if result.get("warnings"):
        click.echo(f"\n⚠️  Warnings:")
        for warning in result["warnings"]:
            click.echo(f"   • {warning}")

    if result.get("suggestions"):
        click.echo(f"\n💡 Suggestions:")
        for suggestion in result["suggestions"]:
            click.echo(f"   • {suggestion}")

    if verbose and "workflow_state" in result:
        click.echo(f"\n🔄 Workflow state: {result['workflow_state']['current_step']}")
        click.echo(f"⏱️  Execution time: {result['execution_time_seconds']:.2f}s")


def _display_verbose_details(result):
    """Display detailed information in verbose mode."""
    analysis = result["analysis_result"]
    design = result["diagram_design"]
    generation = result["d2_generation"]
    validation = result["validation_result"]

    click.echo(f"\n📋 Detailed Information:")

    # Analysis details
    click.echo(f"\n🔍 Code Analysis:")
    click.echo(f"   • Language: {analysis.language}")
    click.echo(f"   • Files processed: {analysis.file_count}")
    click.echo(f"   • Complexity score: {analysis.complexity_score:.2f}")

    click.echo(f"   • Components found (first 10):")
    for comp in analysis.components[:10]:  # Show first 10
        click.echo(f"     - {comp.type.value}: {comp.name}")
    if len(analysis.components) > 10:
        click.echo(f"     ... and {len(analysis.components) - 10} more")

    # Design details
    click.echo(f"\n🎨 Diagram Design:")
    click.echo(f"   • Components to include: {len(design.components_to_include)}")
    click.echo(f"   • Groups created: {len(design.grouping_strategy)}")

    # Generation details
    click.echo(f"\n⚙️  D2 Generation:")
    metadata = generation.generation_metadata
    click.echo(f"   • Components rendered: {metadata.get('components_rendered', 0)}")
    click.echo(f"   • Groups created: {metadata.get('groups_created', 0)}")

    # Validation details
    click.echo(f"\n✅ Validation Details:")
    details = validation.validation_details
    click.echo(f"   • Render success: {details.get('render_success', False)}")
    click.echo(f"   • D2 executable found: {details.get('d2_executable_found', False)}")
    click.echo(f"   • Structure validation: {details.get('structure_validation', False)}")
    click.echo(f"   • Total D2 lines: {details.get('total_lines', 0)}")


if __name__ == "__main__":
    main()