# Python Dependency Analysis Demo

This example demonstrates how to use the Kit SDK's Python Dependency Analyzer to analyze, visualize, and understand import relationships in Python codebases.

## Overview

The demo includes a Python script that analyzes the Kit repository itself, showcasing how the `PythonDependencyAnalyzer` can:

1. Build a comprehensive dependency graph of Python modules
2. Identify circular dependencies
3. Generate visualizations of module relationships
4. Create LLM-friendly context for understanding code structure
5. Analyze specific modules and their interdependencies

## Key Features Demonstrated

This demo shows how Kit's Python Dependency Analyzer can:

1. **Map Import Relationships**: Identify which modules import others, both directly and indirectly.

2. **Detect Circular Dependencies**: Find circular imports that might cause issues at runtime.

3. **Visualize Code Structure**: Generate visual representations of module relationships.

4. **Generate Documentation**: Create LLM-friendly context that describes the code structure in natural language.

5. **Analyze Specific Modules**: Dive deep into the dependencies and dependents of particular modules.

## Running the Demo

To run the demo and analyze the Kit repository:

```bash
# Create output directory
mkdir -p output

# Run basic analysis
python analyze_python_deps.py

# Run with visualization
python analyze_python_deps.py --visualize

# Generate LLM-friendly context
python analyze_python_deps.py --llm-context

# Export in different formats
python analyze_python_deps.py --format json
python analyze_python_deps.py --format graphml

# Analyze a specific module
python analyze_python_deps.py --module kit.dependency_analyzer.python_dependency_analyzer

# Run all options
python analyze_python_deps.py --visualize --llm-context --format dot --module kit.repository
```

## Implementation Details

The analyzer works by:

1. **Parsing Python Files**: It examines each Python file in the codebase to extract import statements.

2. **Mapping Module Names**: It builds a map between module identifiers and file paths.

3. **Building a Dependency Graph**: It creates a graph where nodes are modules and edges represent import relationships.

4. **Analyzing the Graph**: It uses graph algorithms to find cycles, central modules, and other insights.

The Kit repository is an ideal showcase for the analyzer because it has a well-structured codebase with clear module boundaries and dependencies.

## Example Output

The analyzer produces several outputs:

1. **Dependency Graph**: A graph representation of module relationships in various formats (.dot, .json, .graphml).

2. **Visualization**: A visual representation of the dependency graph (.png).

3. **LLM Context**: A markdown document describing the code structure in natural language.

4. **Module Analysis**: Detailed information about specific modules, including their dependencies and dependents.

5. **Console Output**: A summary of key findings, including circular dependencies and central modules.

## Notes

- The visualization requires the Graphviz package. If you encounter errors, install it with `pip install graphviz`.
- You may also need to install the Graphviz system package (`brew install graphviz` on macOS).
- Large repositories may generate complex visualizations that are hard to interpret. Consider filtering to specific modules.
