#!/usr/bin/env python3
"""
Ollama Cloud Model Benchmark Tool

Measures actual token/second performance for each Ollama cloud model
to verify and update performance_data.json.

Usage:
    python3 scripts/benchmark_models.py                    # Run benchmark
    python3 scripts/benchmark_models.py --update           # Update performance_data.json
    python3 scripts/benchmark_models.py --models model1 model2  # Test specific models
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Tuple

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_API_URL = f"{OLLAMA_BASE_URL}/api/generate"

# Test prompt - balanced between speed and meaningful output
TEST_PROMPT = """Write a Python function that calculates the factorial of a number using recursion. Include error handling for negative numbers."""

def check_ollama_connection() -> bool:
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Cannot connect to Ollama at {OLLAMA_BASE_URL}")
        print(f"   Error: {e}")
        print(f"\n   Make sure Ollama is running: ollama serve")
        return False

def benchmark_model(model_name: str) -> Tuple[float, int, float, bool]:
    """
    Benchmark a single model.

    Returns:
        (tokens_per_second, total_tokens, duration_seconds, success)
    """
    print(f"Testing {model_name}...", end=" ", flush=True)

    payload = {
        "model": model_name,
        "prompt": TEST_PROMPT,
        "stream": False
    }

    try:
        start_time = time.time()
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        end_time = time.time()

        if response.status_code != 200:
            print(f"❌ Failed (HTTP {response.status_code})")
            return 0.0, 0, 0.0, False

        result = response.json()

        # Extract metrics
        total_tokens = result.get("eval_count", 0)
        duration_seconds = (end_time - start_time)

        if total_tokens > 0 and duration_seconds > 0:
            tokens_per_second = total_tokens / duration_seconds
            print(f"✅ {tokens_per_second:.1f} tok/s ({total_tokens} tokens in {duration_seconds:.1f}s)")
            return tokens_per_second, total_tokens, duration_seconds, True
        else:
            print(f"❌ Failed (no tokens generated)")
            return 0.0, 0, 0.0, False

    except requests.exceptions.Timeout:
        print(f"❌ Timeout (>120s)")
        return 0.0, 0, 0.0, False
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0.0, 0, 0.0, False

def load_current_data() -> Dict:
    """Load current performance_data.json."""
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(script_dir, "performance_data.json")

    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ performance_data.json not found at {json_path}")
        sys.exit(1)

def save_updated_data(data: Dict) -> None:
    """Save updated performance_data.json."""
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(script_dir, "performance_data.json")

    # Update metadata
    data["_metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    data["_metadata"]["source"] = "Benchmark testing + Ollama API"

    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Updated {json_path}")

def main():
    parser = argparse.ArgumentParser(description="Benchmark Ollama cloud models")
    parser.add_argument("--models", nargs="+", help="Specific models to test")
    parser.add_argument("--update", action="store_true", help="Update performance_data.json with results")
    parser.add_argument("--runs", type=int, default=1, help="Number of test runs per model (default: 1)")
    args = parser.parse_args()

    # Check Ollama connection
    if not check_ollama_connection():
        sys.exit(1)

    # Load current data
    data = load_current_data()

    # Determine which models to test
    if args.models:
        models_to_test = args.models
    else:
        models_to_test = list(data["models"].keys())

    print(f"\n{'='*80}")
    print(f"Ollama Cloud Model Benchmark")
    print(f"{'='*80}")
    print(f"Test prompt: {TEST_PROMPT[:60]}...")
    print(f"Models to test: {len(models_to_test)}")
    print(f"Runs per model: {args.runs}")
    print(f"{'='*80}\n")

    # Run benchmarks
    results = {}

    for model in models_to_test:
        if model not in data["models"]:
            print(f"⚠️  {model} not in performance_data.json, skipping")
            continue

        if args.runs > 1:
            print(f"\n{model} ({args.runs} runs):")
            speeds = []
            for run in range(args.runs):
                print(f"  Run {run + 1}/{args.runs}: ", end="", flush=True)
                tok_per_s, tokens, duration, success = benchmark_model(model)
                if success:
                    speeds.append(tok_per_s)

            if speeds:
                avg_speed = sum(speeds) / len(speeds)
                results[model] = {
                    "tok_per_s": round(avg_speed),
                    "runs": len(speeds),
                    "min": round(min(speeds), 1),
                    "max": round(max(speeds), 1)
                }
        else:
            tok_per_s, tokens, duration, success = benchmark_model(model)
            if success:
                results[model] = {
                    "tok_per_s": round(tok_per_s),
                    "tokens": tokens,
                    "duration": round(duration, 1)
                }

    # Display results
    print(f"\n{'='*80}")
    print(f"Benchmark Results")
    print(f"{'='*80}")
    print(f"{'Model':<30} {'Current':<12} {'Measured':<12} {'Difference'}")
    print(f"{'-'*80}")

    for model, result in results.items():
        current_speed = data["models"][model]["tok_per_s"]
        measured_speed = result["tok_per_s"]
        diff = measured_speed - current_speed
        diff_pct = (diff / current_speed * 100) if current_speed > 0 else 0

        diff_str = f"{diff:+.0f} ({diff_pct:+.0f}%)"
        print(f"{model:<30} {current_speed:<12} tok/s {measured_speed:<12} tok/s {diff_str}")

    print(f"{'-'*80}")

    # Update data if requested
    if args.update:
        print(f"\nUpdating performance_data.json...")
        for model, result in results.items():
            data["models"][model]["tok_per_s"] = result["tok_per_s"]

        save_updated_data(data)
    else:
        print(f"\n💡 To update performance_data.json, run with --update flag")

    print(f"\n✅ Benchmark complete!")

if __name__ == "__main__":
    main()
