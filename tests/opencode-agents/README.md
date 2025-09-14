# OpenCode Agent Evaluation System

A production-ready evaluation system for OpenCode agents using DeepEval framework with local Ollama models, Git-integrated performance tracking, and comprehensive HTML reporting.

## 🎯 What This Does

- **Evaluates OpenCode agents** with custom metrics (relevancy, bias, faithfulness)
- **Tracks performance over time** with Git integration
- **Generates actionable reports** with specific improvement recommendations
- **Automates workflows** from evaluation → benchmarking → reporting

## 🚀 Quick Start

### 1. Setup Environment
```bash
cd tests/opencode-agents
source venv/bin/activate  # Or create: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

### 2. Run Your First Evaluation
```bash
# Evaluate news agent
python demo_deepeval.py

# Save as baseline benchmark
python benchmark_tracker.py save --version "baseline_v1"

# Generate HTML report
python reporting/generate_report.py results --type full
```

### 3. Track Improvements
```bash
# After making code improvements
python demo_deepeval.py
python benchmark_tracker.py save-commit --version "improvement_v1"
python reporting/generate_dashboard.py results --open
```

## 📁 Project Structure

```
tests/opencode-agents/
├── demo_deepeval.py            # Main evaluation script
├── benchmark_tracker.py        # Performance tracking with Git integration
├── generate_full_analysis.py   # Complete workflow automation
├── config/                     # Agent metrics and test configurations
├── utils/                      # Helper utilities for DeepEval and OpenCode
├── reporting/                  # HTML report generation system
├── results/                    # Generated results, benchmarks, and reports
└── venv/                       # Virtual environment (158MB)
```

## 🔥 Core Workflows

### Evaluate → Benchmark → Report
```bash
python demo_deepeval.py                                    # Run evaluation
python benchmark_tracker.py save --version "feature_x"     # Save benchmark
python reporting/generate_report.py results --type full    # Generate report
```

### Git-Integrated Development
```bash
python benchmark_tracker.py save-commit --version "v2"     # Save + Git commit
python benchmark_tracker.py git-history                    # View performance timeline
```

### Complete Analysis
```bash
python generate_full_analysis.py --version "release_v1" --open  # Full workflow
```

## 📊 What You Get

- **DeepEval metrics**: NewsRelevancy, Faithfulness, custom evaluations
- **Performance tracking**: Historical trends with Git correlation
- **HTML reports**: Interactive dashboards with actionable insights
- **Improvement roadmap**: Priority-ranked recommendations

## 📚 Documentation

- **REFERENCE.md** - Complete system documentation, workflows, and troubleshooting
- **reporting/README.md** - HTML reporting system details

## 🧹 Clean & Organized

This project has been cleaned and optimized:
- ✅ Python cache removed, .gitignore added
- ✅ Old reports archived, documentation consolidated  
- ✅ Clear separation of core vs archived content

---

**Get started with the Quick Start above, then see REFERENCE.md for advanced usage and complete system details.**