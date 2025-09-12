# DeepEval HTML Report Generator

A comprehensive reporting system for DeepEval test results that provides multi-dimensional analysis of agent performance with interactive HTML reports.

## Features

🎯 **Multi-Dimensional Analysis**
- Agent performance comparison
- Metric-by-metric analysis
- Test category breakdowns
- Failure pattern identification

📊 **Interactive Visualizations**
- Pass rate distribution charts
- Performance comparison graphs
- Duration vs. performance scatter plots
- Radar charts for metric analysis

🎨 **Professional Reporting**
- DeepEval-inspired modern UI
- Self-contained HTML reports
- Mobile-responsive design
- Print-friendly layouts

🔧 **Generic & Extensible**
- Works with any DeepEval metrics
- Supports multiple result formats (PyTest JSON, JUnit XML, DeepEval JSON)
- CLI and programmatic interfaces
- Configurable analysis thresholds

## Quick Start

### Generate Report from Test Results

```bash
# Navigate to your test results directory
cd tests/opencode-agents

# Activate virtual environment (if using one)
source venv/bin/activate

# Generate full report
python reporting/generate_report.py . --title "Agent Performance Report"

# Generate specific report types
python reporting/generate_report.py . --type summary
python reporting/generate_report.py . --type agents --agents news websearch
python reporting/generate_report.py . --type metrics --metrics FaithfulnessMetric AnswerRelevancyMetric
```

### Programmatic Usage

```python
from reporting import DeepEvalReportGenerator

# Initialize generator
generator = DeepEvalReportGenerator('path/to/test/results')

# Generate full report
report_path = generator.generate_full_report("My Agent Report")

# Generate specific analyses
summary_path = generator.generate_quick_summary()
agent_comparison = generator.generate_agent_comparison(['news', 'websearch'])
metric_analysis = generator.generate_metric_deep_dive(['FaithfulnessMetric'])

# Export raw data
data_path = generator.export_raw_data()

print(f"Report available at: file://{report_path.absolute()}")
```

## Report Sections

### 📊 Overview
- Total test count and pass rates
- Average duration metrics
- High-level performance indicators
- Distribution charts

### 📈 Metrics
- Individual metric performance analysis
- Pass rate by metric type
- Score distributions and thresholds
- Comparative metric analysis

### 🤖 Agents
- Per-agent performance breakdown
- Duration vs. performance analysis
- Common failure patterns
- Agent comparison charts

### 📂 Categories
- Test category analysis (functionality, quality, edge cases)
- Category-specific performance metrics
- Failure pattern identification
- Category recommendations

### 🚨 Failures
- Comprehensive failure analysis
- Failure type categorization
- Most problematic agents identification
- Actionable remediation recommendations

### 💡 Recommendations
- Data-driven improvement suggestions
- Performance optimization guidance
- Quality enhancement recommendations

## Configuration

### Report Settings (`config/report_config.yaml`)

```yaml
# Customize analysis thresholds
analysis:
  thresholds:
    excellent_pass_rate: 90
    good_pass_rate: 80
    poor_pass_rate: 60
    fast_duration: 5.0
    slow_duration: 30.0

# Configure report sections
sections:
  overview: true
  metrics: true
  agents: true
  failures: true
  recommendations: true

# Customize appearance
charts:
  color_scheme: "deepeval"
  animation: true
  responsive: true
```

## Supported Input Formats

### 1. PyTest JSON Reports
Generated with `pytest --json-report --json-report-file=report.json`

### 2. JUnit XML Reports
Generated with `pytest --junit-xml=junit.xml`

### 3. DeepEval JSON Exports
Custom DeepEval result exports with test run metadata

### 4. Multiple File Detection
The system automatically searches for common result file patterns:
- `report.json`, `*pytest*.json`
- `junit.xml`, `*junit*.xml`  
- `*deepeval*.json`

## CLI Reference

```bash
python reporting/generate_report.py <results_dir> [options]

Required:
  results_dir          Directory containing test results

Options:
  --output, -o         Output filename (auto-generated if not specified)
  --title, -t          Report title (default: "DeepEval Agent Performance Report")
  --type              Report type: full, summary, agents, metrics (default: full)
  --agents            Specific agents to analyze (for agent reports)
  --metrics           Specific metrics to analyze (for metric reports)
  --export-data       Also export raw analysis data as JSON
  --output-dir        Custom output directory
  --verbose, -v       Verbose output

Examples:
  # Full report with custom title
  python reporting/generate_report.py ./results --title "Production Agent Analysis"
  
  # Quick summary report
  python reporting/generate_report.py ./results --type summary --output summary.html
  
  # Agent comparison
  python reporting/generate_report.py ./results --type agents --agents news websearch reasoning
  
  # Metric deep dive
  python reporting/generate_report.py ./results --type metrics --metrics FaithfulnessMetric GEval
  
  # Export data for external analysis
  python reporting/generate_report.py ./results --export-data --verbose
```

## Architecture

```
reporting/
├── core/                    # Core analysis components
│   ├── data_collector.py    # Multi-format result collection
│   ├── metric_analyzer.py   # Cross-dimensional analysis engine
│   └── report_generator.py  # Main orchestrator
├── templates/               # Jinja2 HTML templates
│   ├── base.html           # Base template with styling
│   └── report.html         # Main report template
├── config/                 # Configuration files
│   └── report_config.yaml  # Analysis and display settings
├── assets/                 # Static assets (if needed)
└── generate_report.py      # CLI entry point
```

## Example Output

The generated reports include:

✅ **Interactive Navigation** - Click through different analysis sections  
📊 **Rich Visualizations** - Charts and graphs powered by Chart.js  
🎯 **Actionable Insights** - Specific recommendations for improvement  
📱 **Responsive Design** - Works on desktop, tablet, and mobile  
🖨️ **Print Support** - Clean printing with optimized layouts  
🔗 **Self-Contained** - Single HTML file with embedded assets  

## Troubleshooting

### No Test Results Found
- Ensure test results exist in the specified directory
- Check that result files are in supported formats
- Use `--verbose` flag to see which files are being searched

### Template Rendering Errors
- Verify Jinja2 is installed: `pip install jinja2`
- Check that template files exist in `templates/` directory
- Ensure result data structure matches expected format

### Missing Dependencies
```bash
# Install required packages
pip install deepeval jinja2

# Or create requirements.txt
echo "deepeval>=3.4.0" > requirements.txt
echo "jinja2>=3.1.0" >> requirements.txt
pip install -r requirements.txt
```

### Chart Rendering Issues
- Charts require internet connection for Chart.js CDN
- Ensure JavaScript is enabled in browser
- Check browser console for any JavaScript errors

## Development

### Adding New Metrics
Extend the `MetricAnalyzer` class to add custom metric analysis:

```python
def analyze_custom_metric(self, results):
    # Custom metric analysis logic
    pass
```

### Custom Templates
Create custom report templates by:
1. Adding new template files to `templates/`
2. Extending the base template
3. Using the template in `report_generator.py`

### Configuration Extensions
Add new configuration options in `config/report_config.yaml` and update the corresponding analysis classes.

## License

This DeepEval HTML Report Generator is designed to work with any DeepEval setup and can be freely modified and extended for specific needs.