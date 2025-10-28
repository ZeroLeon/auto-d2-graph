#!/usr/bin/env python3
"""
Agentic D2 Diagram Generator - Version 3.0

Professional-grade diagram generation with intelligent shape selection,
advanced layouts, and enterprise-quality output.
"""

import argparse
import sys
import os
from pathlib import Path

from agents.orchestrator_agent_v3 import OrchestratorAgentV3

def main():
    """Main entry point for V3.0"""
    parser = argparse.ArgumentParser(
        description="Generate professional D2 diagrams from Python code - V3.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from single file with professional styling
  python main_v3.py --file my_service.py --output service_architecture.d2

  # Generate from repository with microservices layout
  python main_v3.py --repository ./my_project --output system_diagram.d2 --theme enterprise_green

  # Preview design recommendations
  python main_v3.py --file my_code.py --preview

  # Generate with custom preferences
  python main_v3.py --file my_api.py --output api_design.d2 --layout microservices --verbose
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--file', '-f',
        type=str,
        help='Path to Python file to analyze'
    )
    input_group.add_argument(
        '--repository', '-r',
        type=str,
        help='Path to repository directory to analyze'
    )

    # Output options
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='diagram_v3.d2',
        help='Output path for generated diagram (default: diagram_v3.d2)'
    )

    # V3.0 Professional Options
    parser.add_argument(
        '--theme',
        type=str,
        choices=['professional_blue', 'enterprise_green', 'modern_purple', 'tech_orange'],
        default='professional_blue',
        help='Color theme for the diagram (default: professional_blue)'
    )

    parser.add_argument(
        '--layout',
        type=str,
        choices=['microservices', 'layered_architecture', 'data_flow', 'system_landscape', 'component_overview'],
        help='Force specific layout type (auto-detected by default)'
    )

    parser.add_argument(
        '--max-components',
        type=int,
        help='Maximum number of components to include (auto-optimized by default)'
    )

    # Analysis options
    parser.add_argument(
        '--preview', '-p',
        action='store_true',
        help='Preview design recommendations without generating diagram'
    )

    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate detailed quality report'
    )

    parser.add_argument(
        '--svg',
        action='store_true',
        help='Also generate SVG output (requires D2 installation)'
    )

    # Utility options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with detailed generation information'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show generation statistics'
    )

    args = parser.parse_args()

    # Validate input
    if args.file and not os.path.exists(args.file):
        print(f"❌ Error: File '{args.file}' not found")
        sys.exit(1)

    if args.repository and not os.path.exists(args.repository):
        print(f"❌ Error: Repository '{args.repository}' not found")
        sys.exit(1)

    # Create output directory if needed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Prepare user preferences
    user_preferences = {
        'theme': args.theme,
        'verbose': args.verbose
    }

    if args.layout:
        user_preferences['layout_engine'] = args.layout
    if args.max_components:
        user_preferences['max_components'] = args.max_components

    # Initialize V3.0 orchestrator
    orchestrator = OrchestratorAgentV3(verbose=args.verbose)

    try:
        if args.preview:
            # Preview mode
            print("🔍 Analyzing code and generating design recommendations...")
            recommendations = orchestrator.preview_design_recommendations(
                file_path=args.file,
                repository_path=args.repository
            )

            if 'error' in recommendations:
                print(f"❌ Analysis failed: {recommendations['error']}")
                sys.exit(1)

            print("\n" + "="*50)
            print("📊 DESIGN RECOMMENDATIONS")
            print("="*50)
            print(f"📦 Components Found: {recommendations['components_found']}")
            print(f"🔗 Relationships Found: {recommendations['relationships_found']}")
            print(f"⏱️  Estimated Time: {recommendations['estimated_generation_time']}")

            recs = recommendations['recommendations']
            print(f"\n🎯 Recommended Layout: {recs['layout_engine']}")
            print(f"📋 Diagram Type: {recs['diagram_type']}")
            print(f"🎨 Recommended Theme: {recs['theme']}")
            print(f"📊 Confidence: {recs['confidence']:.2f}")
            print(f"📈 Complexity: {recs['complexity']}")

            if 'layout_suggestion' in recs:
                print(f"\n💡 Suggestion: {recs['layout_suggestion']}")

            print("="*50)
            return

        # Full generation mode
        print("🚀 Starting V3.0 Professional Diagram Generation...")
        print(f"📁 Input: {args.file or args.repository}")
        print(f"📄 Output: {args.output}")
        print(f"🎨 Theme: {args.theme}")

        result = orchestrator.generate_diagram(
            file_path=args.file,
            repository_path=args.repository,
            output_path=args.output,
            user_preferences=user_preferences
        )

        # Check generation result
        if result.generation_result.success:
            print(f"\n✅ V3.0 diagram successfully generated!")
            print(f"📄 D2 file: {args.output}")

            if args.svg:
                svg_path = args.output.replace('.d2', '.svg')
                # Try to generate SVG even if validation has minor issues
                try:
                    import subprocess
                    result_svg = subprocess.run(['d2', args.output, svg_path],
                                              capture_output=True, text=True, timeout=30)
                    if result_svg.returncode == 0:
                        print(f"🎨 SVG file: {svg_path}")
                    else:
                        print(f"⚠️  SVG generation failed: {result_svg.stderr}")
                except Exception as e:
                    print(f"⚠️  SVG generation error: {e}")
            elif args.svg and not result.generation_result.validation_result.is_valid:
                print("⚠️  SVG generation skipped due to validation errors")

            if args.report:
                report_path = args.output.replace('.d2', '_report.txt')
                generate_quality_report(result, report_path)
                print(f"📊 Quality report: {report_path}")

        else:
            print(f"\n❌ Generation completed with issues:")
            print(f"   Quality Score: {result.generation_result.quality_score:.2f}/1.00")
            print(f"   Valid D2: {'✅' if result.generation_result.validation_result.is_valid else '❌'}")

            if result.validation_errors:
                print(f"   Validation Issues: {len(result.validation_errors)}")

        # Try SVG generation regardless of success status (if D2 file exists)
        if args.svg and os.path.exists(args.output):
            svg_path = args.output.replace('.d2', '.svg')
            # Try to generate SVG even if validation has minor issues
            try:
                import subprocess
                result_svg = subprocess.run(['d2', args.output, svg_path],
                                          capture_output=True, text=True, timeout=30)
                if result_svg.returncode == 0:
                    print(f"🎨 SVG file: {svg_path}")
                else:
                    print(f"⚠️  SVG generation failed: {result_svg.stderr}")
            except Exception as e:
                print(f"⚠️  SVG generation error: {e}")

        # Show statistics if requested
        if args.stats:
            stats = orchestrator.get_generation_statistics()
            print(f"\n📊 Generation Statistics:")
            print(f"   Total Generations: {stats['total_generations']}")
            print(f"   Success Rate: {stats['success_rate']:.1f}%")
            print(f"   Average Quality: {stats['average_quality']:.3f}")

            if stats['most_used_layouts']:
                print(f"   Most Used Layout: {max(stats['most_used_layouts'], key=stats['most_used_layouts'].get)}")

            if stats['most_used_themes']:
                print(f"   Most Used Theme: {max(stats['most_used_themes'], key=stats['most_used_themes'].get)}")

    except KeyboardInterrupt:
        print("\n⏹️  Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def generate_quality_report(result: 'V3GenerationResult', report_path: str) -> None:
    """Generate detailed quality report"""
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("D2 Diagram Quality Report - Version 3.0\n")
            f.write("=" * 50 + "\n\n")

            # Basic info
            f.write("GENERATION INFO\n")
            f.write("-" * 20 + "\n")
            f.write(f"Success: {result.generation_result.success}\n")
            f.write(f"Quality Score: {result.generation_result.quality_score:.3f}/1.000\n")
            f.write(f"Layout Engine: {result.layout_engine}\n")
            f.write(f"Theme: {result.theme_used}\n")
            f.write(f"Generation Time: {result.generation_result.generation_time:.2f}s\n\n")

            # Shapes used
            f.write("SHAPES USED\n")
            f.write("-" * 20 + "\n")
            for shape in result.shapes_used:
                f.write(f"- {shape}\n")
            f.write("\n")

            # Quality breakdown
            if result.quality_breakdown:
                f.write("QUALITY BREAKDOWN\n")
                f.write("-" * 20 + "\n")
                for metric, score in result.quality_breakdown.items():
                    f.write(f"{metric}: {score:.3f}\n")
                f.write("\n")

            # Validation issues
            if result.validation_errors:
                f.write("VALIDATION ISSUES\n")
                f.write("-" * 20 + "\n")
                for error in result.validation_errors:
                    f.write(f"- {error}\n")
                f.write("\n")

            # Statistics
            if result.generation_stats:
                f.write("GENERATION STATISTICS\n")
                f.write("-" * 20 + "\n")
                for key, value in result.generation_stats.items():
                    f.write(f"{key}: {value}\n")

    except Exception as e:
        print(f"⚠️  Could not generate quality report: {str(e)}")

if __name__ == "__main__":
    main()