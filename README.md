# Everything App MCP (Monitoring Control Panel)

This repository contains the monitoring tools for The Everything App project's Python codebase. It helps identify and track static typing issues, style problems, and other code quality concerns.

## Features

- 🔍 Static type checking using Pyright/Pylance
- 📊 Structured JSON output for parsing and visualization
- 📈 Problem tracking over time
- 🚨 Severity-based filtering and reporting
- 🗂️ File-specific analysis

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/tremaynet/everything-app-mcp.git
   cd everything-app-mcp
   ```

2. Install dependencies:
   ```bash
   npm install -g pyright
   ```

## Usage

### Analyzing the entire project

```bash
python mcp_monitor.py
```

### Analyzing specific files

```bash
python mcp_monitor.py aws_lambdas/data_processor.py
```

### Output

The tool provides both terminal output with color-coded problems and saves detailed JSON results to the `mcp_results` directory.

## Integration with The Everything App

This monitoring tool is designed to help maintain code quality across all Python components of The Everything App, including:

- AWS Lambda functions
- SageMaker ML model code
- Data transformation scripts
- API integrations

## Best Practices

1. Run the monitor before each commit
2. Fix errors in order of severity
3. Track progress over time by comparing result files
4. Integrate with CI/CD pipelines for automated quality checks

## AWS Architecture Integration

This MCP integrates with The Everything App's AWS architecture by:

1. Validating Lambda functions for type correctness
2. Ensuring proper AWS SDK usage
3. Checking for common data handling issues
4. Validating SageMaker model integration points

## Contributing

1. Fix one file at a time
2. Run the monitor to verify your changes
3. Submit pull requests with before/after monitoring results

## License

MIT