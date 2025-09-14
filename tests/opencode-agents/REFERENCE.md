# OpenCode Agent Evaluation System - Complete Reference

## System Architecture

### Core Components

**Evaluation Engine**
- **PyTest Integration**: Native DeepEval + PyTest with `assert_test()`
- **Ollama Configuration**: Local `gemma3:latest` model for evaluation
- **OpenCode Integration**: Command-line integration with OpenCode agents
- **Custom Metrics**: Agent-specific evaluation criteria

**Performance Tracking**
- **Benchmark System**: Git-integrated performance tracking over time
- **Trend Analysis**: Performance improvements and regressions
- **Code Correlation**: Link performance changes to specific code modifications

**Reporting Infrastructure**
- **HTML Report Generator**: Interactive reports with visualizations
- **Dashboard System**: Overview with cross-linked navigation
- **Multi-format Support**: PyTest JSON, JUnit XML, DeepEval JSON

**Git Integration**
- **Automated Commits**: Intelligent commit messages with performance data
- **Context Capture**: Commit hash, branch, changed files for every benchmark
- **History Visualization**: Timeline showing code changes + performance impact

## Complete Workflows

### 1. Basic Evaluation Workflow

```bash
# Run evaluation
python demo_deepeval.py

# Results in: results/deepeval_results.json
# Contains: scores, issues, recommendations, full agent output
```

**What happens internally:**
1. Invokes `opencode run --agent news` with test query
2. Captures full agent response and metadata
3. Evaluates with custom DeepEval metrics (NewsRelevancy, Faithfulness)
4. Generates actionable insights and improvement recommendations
5. Saves detailed results with input/output visibility

### 2. Benchmark Tracking Workflow

```bash
# Save benchmark with Git context
python benchmark_tracker.py save --version "baseline_v1"

# Save benchmark + automatic Git commit
python benchmark_tracker.py save-commit --version "improvement_v2"

# Compare performance
python benchmark_tracker.py compare --baseline "baseline_v1"

# View trends over time
python benchmark_tracker.py trends

# View Git-integrated history
python benchmark_tracker.py git-history
```

**Benchmark data includes:**
- Performance scores by agent and metric
- Issue counts and types
- Git context (commit, branch, changed files)
- Timestamps and version labels
- Recommendations and insights

### 3. Reporting Workflow

```bash
# Generate full HTML report
python reporting/generate_report.py results --type full

# Generate specific report types
python reporting/generate_report.py results --type summary
python reporting/generate_report.py results --type agents --agents news
python reporting/generate_report.py results --type metrics --metrics NewsRelevancy

# Generate dashboard with cross-linking
python reporting/generate_dashboard.py results --open
```

**Report features:**
- Interactive visualizations with Chart.js
- Performance history automatically included
- Cross-linking between reports and dashboard
- Self-contained HTML files
- Mobile-responsive design

### 4. Complete Analysis Workflow

```bash
# Full workflow: evaluate → report → benchmark → dashboard
python generate_full_analysis.py --version "release_v1" --open

# With Git integration
python generate_full_analysis.py --version "feature_x" --commit --open
```

### 5. Git-Integrated Development Cycle

```bash
# Make code improvements
vim agents/news_agent.py

# Run evaluation + save + commit in one step
python benchmark_tracker.py save-commit --version "content_filter_v1"

# Generate updated reports
python reporting/generate_dashboard.py results --open

# Review performance correlation with code changes
python benchmark_tracker.py git-history
```

## Command Reference

### benchmark_tracker.py

**Basic Operations:**
```bash
python benchmark_tracker.py save --version "version_name"           # Save benchmark
python benchmark_tracker.py trends                                  # Show performance trends
python benchmark_tracker.py compare --baseline "version_name"       # Compare with baseline
```

**Git Integration:**
```bash
python benchmark_tracker.py save-commit --version "version_name"              # Save + Git commit
python benchmark_tracker.py save-commit --commit-message "custom message"     # Custom commit message
python benchmark_tracker.py git-history                                       # Performance + Git timeline
```

**Data Management:**
```bash
python benchmark_tracker.py list                                    # List all benchmarks
python benchmark_tracker.py delete --version "version_name"         # Delete benchmark
python benchmark_tracker.py export --format json                    # Export data
```

### reporting/generate_report.py

```bash
python reporting/generate_report.py <results_dir> [options]

Options:
  --output, -o         Output filename
  --title, -t          Report title
  --type              Report type: full, summary, agents, metrics
  --agents            Specific agents to analyze
  --metrics           Specific metrics to analyze
  --export-data       Also export raw analysis data as JSON
  --output-dir        Custom output directory
  --verbose, -v       Verbose output
```

**Examples:**
```bash
# Full report with custom title
python reporting/generate_report.py ./results --title "Production Analysis"

# Quick summary
python reporting/generate_report.py ./results --type summary

# Agent comparison
python reporting/generate_report.py ./results --type agents --agents news websearch

# Metric analysis
python reporting/generate_report.py ./results --type metrics --metrics NewsRelevancy
```

### reporting/generate_dashboard.py

```bash
python reporting/generate_dashboard.py <results_dir> [options]

Options:
  --open              Automatically open in browser
  --title             Dashboard title
  --output-dir        Custom output directory
```

## Git Integration Details

### Automatic Git Context Collection
Every benchmark captures:
- **Commit Hash**: Exact code version
- **Branch Name**: Development branch
- **Changed Files**: Files modified since last commit
- **Last Commit Message**: Context about changes

### Intelligent Commit Messages
System generates meaningful commits based on performance changes:

```bash
# Performance improvement
"benchmark: improved_v2 - newsagent NewsRelevancy +0.150 (1 issues)"

# Performance regression
"benchmark: regression_v3 - newsagent NewsRelevancy -0.080 (6 issues)"

# Stable performance
"benchmark: stable_v4 - 2 issues remaining"
```

### Performance-Code Correlation

The system maintains correlation between code changes and performance:

| Benchmark | Performance | Git Context | Code Changes |
|-----------|-------------|-------------|--------------|
| baseline_v1 | NewsRelevancy: 0.70 | 93c3e6ff | Initial implementation |
| improved_v2 | **+0.15 improvement** | a1b2c3d4 | Enhanced content filtering |
| optimized_v3 | **+0.05 improvement** | b2c3d4e5 | Better source weighting |

## Performance Tracking & Benchmarking

### Benchmark Data Structure

```json
{
  "version": "improvement_v2",
  "timestamp": "2025-09-13T14:30:00Z",
  "git_context": {
    "commit_hash": "a1b2c3d4",
    "branch": "feature/improvements",
    "changed_files": ["agents/news_agent.py", "utils/filter.py"],
    "last_commit_message": "Enhanced content filtering"
  },
  "results": {
    "newsagent": {
      "NewsRelevancy": 0.850,
      "Faithfulness": 0.920
    }
  },
  "issues": 1,
  "recommendations": 2
}
```

### Performance Analysis

**Trend Analysis:**
- Score changes over time by agent and metric
- Issue count progression
- Improvement vs regression detection
- Statistical significance testing

**Comparative Analysis:**
- Baseline vs current performance
- Version-to-version deltas
- Best/worst performing versions
- Performance stability metrics

## Improvement Patterns

### Using DeepEval Results for Systematic Enhancement

**1. Issue Identification:**
Reports provide specific problems with priority rankings:
- HIGH: Content filtering (too much non-tech content)
- MEDIUM: Source selection (mixed source quality)
- LOW: Timestamp inclusion (missing publication dates)

**2. Implementation Guidance:**
Each issue includes concrete implementation suggestions:
```python
# Example: Content filtering improvement
tech_keywords = ['AI', 'software', 'tech company', 'startup', 'innovation']
filtered_articles = [article for article in articles 
                    if any(keyword in article.lower() for keyword in tech_keywords)]
```

**3. Measurement & Validation:**
- Re-run evaluation after changes
- Compare performance with benchmark system
- Track issue reduction over time
- Validate improvements with additional test scenarios

### Continuous Improvement Cycle

1. **Baseline Establishment**: Create initial performance baseline
2. **Issue Prioritization**: Focus on HIGH priority improvements first
3. **Implementation**: Make targeted code improvements
4. **Measurement**: Re-evaluate and benchmark performance
5. **Validation**: Ensure improvements are sustained
6. **Iteration**: Move to next priority improvements

## Configuration

### Agent Metrics Configuration

**File**: `config/agent_metrics.yaml`

```yaml
news:
  - type: "faithfulness"
    threshold: 0.7
    model: "ollama"
  - type: "custom"
    name: "NewsRelevancy"
    criteria: "Evaluate whether news items are current and relevant to technology"
    threshold: 0.7
    model: "ollama"

websearch:
  - type: "answer_relevancy"
    threshold: 0.8
    model: "ollama"
  - type: "custom"
    name: "SearchAccuracy"
    criteria: "Evaluate search result accuracy and completeness"
    threshold: 0.75
    model: "ollama"
```

### Ollama Configuration

**File**: `utils/deepeval_helpers.py`

```python
OllamaModel(
    model_id="gemma3:latest",
    model_url="http://localhost:11434"
)
```

### Report Configuration

**File**: `reporting/config/report_config.yaml`

```yaml
analysis:
  thresholds:
    excellent_pass_rate: 90
    good_pass_rate: 80
    poor_pass_rate: 60
    fast_duration: 5.0
    slow_duration: 30.0

sections:
  overview: true
  metrics: true
  agents: true
  failures: true
  recommendations: true

charts:
  color_scheme: "deepeval"
  animation: true
  responsive: true
```

## Troubleshooting

### Common Issues

**1. Ollama Connection Errors**
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve

# Verify model is available
ollama list | grep gemma3
```

**2. OpenCode Agent Not Found**
```bash
# Verify OpenCode installation
opencode --version

# Check available agents
opencode list-agents

# Test agent manually
opencode run --agent news --query "test query"
```

**3. Virtual Environment Issues**
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install deepeval pytest-html jinja2
```

**4. Git Integration Problems**
```bash
# Ensure Git repository is initialized
git status

# Check for uncommitted changes
git diff --stat

# Verify Git user configuration
git config user.name
git config user.email
```

### Performance Issues

**Slow Evaluations:**
- Normal duration: 60-90 seconds per evaluation
- Ollama model loading adds ~10-15 seconds on first run
- Consider using smaller models for faster iteration

**Large Report Files:**
- Reports include embedded assets for self-containment
- Use `--type summary` for lighter reports
- Archive old reports regularly

### Data Issues

**Missing Benchmarks:**
- Check `results/benchmarks.json` exists
- Verify benchmark was saved successfully
- Use `benchmark_tracker.py list` to see available benchmarks

**Report Generation Failures:**
- Ensure Jinja2 is installed: `pip install jinja2`
- Check template files exist in `reporting/templates/`
- Verify result data structure is valid

## Technical Implementation

### DeepEval Integration

The system uses DeepEval's evaluation framework with:
- Custom metrics for domain-specific evaluation
- Ollama integration for local model execution
- PyTest integration for test framework compatibility
- JSON result export for processing and reporting

### Benchmark Storage

Benchmarks are stored in `results/benchmarks.json` with:
- Versioned performance data
- Git context for each benchmark
- Trend analysis metadata
- Issue and recommendation tracking

### Report Generation

HTML reports use:
- Jinja2 templating for dynamic content
- Chart.js for interactive visualizations
- Bootstrap for responsive design
- Self-contained assets for portability

### Cross-linking System

The system maintains relationships between:
- Benchmarks and Git commits
- Reports and performance data
- Dashboard and individual reports
- Historical trends and specific evaluations

---

This reference provides complete technical documentation for the OpenCode agent evaluation system. For quick start guidance, see README.md.