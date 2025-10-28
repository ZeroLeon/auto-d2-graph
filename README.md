# Agentic D2 Diagram Generator - Version 2.0

An intelligent application that automatically generates high-quality D2 diagrams from Python code with built-in reflection, validation, and quality assessment capabilities.

## 🆕 Version 2.0 Features

- **Multi-Agent Architecture**: Uses specialized agents for code analysis, diagram design, D2 generation, validation, and quality evaluation
- **Python Support**: Analyzes Python files and repositories to extract structural information
- **Intelligent Design**: Automatically selects optimal diagram types and layouts based on code complexity
- **Reflection & Validation**: Validates generated D2 syntax and checks renderability with SVG generation
- **Quality Evaluation**: Comprehensive quality assessment with detailed metrics and improvement suggestions
- **High-Quality Output**: Enhanced D2 generation with better styling, readability, and structure
- **Smart Component Selection**: Intelligently limits components for optimal readability
- **CLI Interface**: Easy-to-use command-line interface with comprehensive options

## Architecture

The system consists of 5 main agents (Version 2.0):

1. **Code Analysis Agent**: Parses Python code using AST to extract classes, functions, and relationships
2. **Diagram Design Agent**: Determines optimal diagram types (class, architecture, flow) and layouts
3. **D2 Generation Agent**: Converts analyzed data into clean D2 syntax with proper styling
4. **Reflection Agent**: Validates D2 syntax and tests actual renderability
5. **🆕 Evaluation Agent**: Assesses diagram quality and provides improvement suggestions

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd auto_d2_graph
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install D2 (required for validation):
```bash
# Follow instructions at https://d2lang.com/
# For example, on macOS:
brew install d2

# On other platforms, see: https://d2lang.com/tour/install/
```

## Usage

### Basic Usage

Analyze a single Python file:
```bash
python main.py --file test_sample_code.py --output diagram.d2
```

Analyze a Python repository:
```bash
python main.py --repository ./my_project --output project_diagram.d2
```

### Advanced Options

Verbose output with detailed information:
```bash
python main.py --file test_sample_code.py --verbose
```

Generate workflow report:
```bash
python main.py --file test_sample_code.py --report
```

Custom retry attempts for failed validations:
```bash
python main.py --file test_sample_code.py --max-retries 5
```

### Command Line Options

- `--file, -f`: Python file to analyze
- `--repository, -r`: Python repository to analyze
- `--output, -o`: Output D2 file path (default: output.d2)
- `--verbose, -v`: Enable verbose output
- `--max-retries`: Maximum retry attempts (default: 3)
- `--report`: Generate workflow report

## Output

The tool generates:

1. **D2 Diagram File**: Renderable D2 code with proper styling and layout
2. **CLI Output**: Summary of analysis and generation results
3. **Workflow Report** (optional): Detailed report of the generation process

## Example

Given the provided `test_sample_code.py` file, the tool will:

1. **Analyze** the Python code to extract classes like `User`, `Customer`, `Product`, `Order`, etc.
2. **Design** an appropriate class diagram with hierarchical layout
3. **Generate** D2 code showing:
   - Classes with methods and properties
   - Inheritance relationships (e.g., Customer inherits from User)
   - Dependencies and associations
4. **Validate** the D2 syntax and test renderability

## Testing

Run the tool with the provided test file:

```bash
python main.py --file test_sample_code.py --verbose --report
```

This will generate:
- `output.d2`: The generated D2 diagram (valid and renderable)
- `output_report.md`: Detailed workflow report

To render the diagram to SVG:
```bash
d2 output.d2 output.svg
```

The generated diagrams are fully compatible with D2 and can be rendered to SVG, PNG, or other formats.

## Quality Evaluation (Version 2.0)

The system includes comprehensive quality evaluation with the following metrics:

- **Clarity**: Measures how clear and understandable the diagram is
- **Completeness**: Evaluates how complete the diagram representation is
- **Structure**: Assesses the structural organization of the diagram
- **Readability**: Evaluates visual clarity and complexity
- **Semantic Quality**: Checks the semantic correctness and meaningfulness

**Quality Scores:**
- 🏆 **Excellent**: 0.80-1.00
- ✅ **Good**: 0.70-0.79
- ⚠️ **Fair**: 0.60-0.69
- ❌ **Poor**: Below 0.60

The system provides specific improvement suggestions to enhance diagram quality.

## Development

### Project Structure

```
auto_d2_graph/
├── agents/
│   ├── __init__.py
│   ├── code_analysis_agent.py      # Python code analysis
│   ├── diagram_design_agent.py     # Diagram type and layout selection
│   ├── d2_generation_agent.py      # D2 syntax generation
│   ├── reflection_agent.py         # Validation and testing
│   └── orchestrator_agent.py       # Workflow coordination
├── data_models.py                  # Pydantic data models
├── main.py                         # CLI interface
├── test_sample_code.py            # Example Python code
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

### Extending the System

The architecture is designed for easy extension:

1. **Add new languages**: Implement new analysis agents
2. **New diagram types**: Extend the design agent
3. **Custom styling**: Modify the D2 generation agent
4. **Advanced validation**: Enhance the reflection agent

## Limitations (Version 1.0)

- Python language support only
- Basic validation without quality scoring
- Single diagram output per run
- Limited customization options

## Future Enhancements (Version 2.0)

- Multi-language support (JavaScript, Java, etc.)
- Quality evaluation agent with scoring
- Interactive diagram generation
- Integration with IDEs and CI/CD
- Advanced customization options

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Troubleshooting

### D2 Not Found
If you get "D2 executable not found" error:
1. Install D2 from https://d2lang.com/
2. Ensure D2 is in your PATH
3. Run `d2 --version` to verify installation

### Python AST Errors
If analysis fails on certain Python files:
1. Check for syntax errors in the input file
2. Ensure all dependencies are available
3. Use `--verbose` flag for detailed error information

### Large Repositories
For very large codebases:
1. Consider analyzing specific files instead of entire repository
2. The tool automatically limits components to maintain readability
3. Generate multiple diagrams for different modules

## Support

For issues and questions:
1. Check the troubleshooting section
2. Use `--verbose` flag for detailed debugging
3. Review the workflow report for analysis details