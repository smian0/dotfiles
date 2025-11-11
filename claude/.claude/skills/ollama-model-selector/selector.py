#!/usr/bin/env python3
"""
Ollama Model Selector - Find the best model for your needs.

This script helps users select the optimal Ollama model by analyzing their requirements
and matching them to model capabilities based on verified performance data.
"""

import argparse
import json
import sys
import os
from typing import Dict, List, Tuple

# Load model performance data from JSON file
def load_performance_data():
    """Load performance data from JSON file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "performance_data.json")

    with open(json_path, 'r') as f:
        data = json.load(f)

    return data["models"]

PERFORMANCE_DATA = load_performance_data()

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Select the best Ollama model for your needs")
    parser.add_argument("--task", help="Task type (coding, reasoning, vision, general)")
    parser.add_argument("--priority", help="Performance priority (speed, accuracy, balanced)")
    parser.add_argument("--context", help="Context requirement (small, medium, large)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (text or json)")
    parser.add_argument("--compare", nargs="+", help="Compare specific models")
    parser.add_argument("--list", action="store_true", help="List all available models")
    parser.add_argument("--update", action="store_true", help="Update model data from Ollama API")
    return parser.parse_args()

def analyze_requirements(task: str, priority: str, context: str) -> Dict[str, float]:
    """Analyze user requirements and return weights for different model aspects."""
    weights = {}
    
    # Task type weights
    if task == "coding":
        weights["coding"] = 1.0
        weights["reasoning"] = 0.6
        weights["vision"] = 0.0
    elif task == "reasoning":
        weights["coding"] = 0.4
        weights["reasoning"] = 1.0
        weights["vision"] = 0.0
    elif task == "vision":
        weights["coding"] = 0.2
        weights["reasoning"] = 0.4
        weights["vision"] = 1.0
    else:  # general
        weights["coding"] = 0.5
        weights["reasoning"] = 0.7
        weights["vision"] = 0.3
    
    # Priority weights
    if priority == "speed":
        weights["speed"] = 1.0
        weights["accuracy"] = 0.6
    elif priority == "accuracy":
        weights["speed"] = 0.4
        weights["accuracy"] = 1.0
    else:  # balanced
        weights["speed"] = 0.7
        weights["accuracy"] = 0.7
    
    # Context weights
    if context == "small":
        weights["small_context"] = 0.3
        weights["large_context"] = 0.0
    elif context == "large":
        weights["small_context"] = 0.0
        weights["large_context"] = 1.0
    else:  # medium
        weights["small_context"] = 0.0
        weights["large_context"] = 0.0
    
    return weights

def calculate_score(model: str, requirements: Dict[str, float]) -> float:
    """Calculate a score for a model based on requirements."""
    if model not in PERFORMANCE_DATA:
        return 0.0
    
    model_data = PERFORMANCE_DATA[model]
    score = 0.0
    
    # Performance score (normalized to 0-1)
    max_speed = max(data["tok_per_s"] for data in PERFORMANCE_DATA.values())
    speed_score = model_data["tok_per_s"] / max_speed
    
    # Task fit score - check if model is actually good for the task
    task_score = 0.0
    best_for = model_data.get("best_for", "").lower()
    
    # Check vision capabilities
    if requirements.get("vision", 0) > 0:
        if any(term in best_for for term in ["vision", "ocr", "gui", "multimodal", "image"]):
            # Extra weight for instruction-following and agent capabilities
            if any(term in best_for for term in ["instruction", "agent", "conversational"]):
                task_score += requirements.get("vision", 0) * 0.9
            else:
                task_score += requirements.get("vision", 0) * 0.8
        else:
            task_score += requirements.get("vision", 0) * 0.2
    
    # Check coding capabilities
    if requirements.get("coding", 0) > 0:
        if any(term in best_for for term in ["coding", "code", "debug", "software"]):
            # Extra weight for code generation from images
            if "code generation from images" in best_for:
                task_score += requirements.get("coding", 0) * 0.9
            else:
                task_score += requirements.get("coding", 0) * 0.8
        else:
            task_score += requirements.get("coding", 0) * 0.3
    
    # Check reasoning capabilities
    if requirements.get("reasoning", 0) > 0:
        if any(term in best_for for term in ["reasoning", "analysis", "problem-solving", "mathematical"]):
            task_score += requirements.get("reasoning", 0) * 0.8
        else:
            task_score += requirements.get("reasoning", 0) * 0.4
    
    task_score = min(task_score, 1.0)  # Cap at 1.0
    
    # Context fit score
    context_score = 0.0
    if model_data["context"] >= 256:
        context_score = requirements.get("large_context", 0)
    elif model_data["context"] >= 128:
        context_score = 0.5
    else:
        context_score = requirements.get("small_context", 0)
    
    # Priority score
    priority_score = (
        requirements.get("speed", 0.7) * speed_score +
        requirements.get("accuracy", 0.7) * (1.0 - speed_score)  # Inverse of speed for accuracy
    )
    
    # Calculate weighted score
    score = (
        task_score * 0.4 +
        context_score * 0.2 +
        priority_score * 0.4
    )
    
    return score

def recommend_models(task: str, priority: str, context: str, count: int = 3) -> List[Tuple[str, float]]:
    """Recommend top models based on requirements."""
    requirements = analyze_requirements(task, priority, context)
    
    # Calculate scores for all models
    model_scores = []
    for model in PERFORMANCE_DATA.keys():
        score = calculate_score(model, requirements)
        model_scores.append((model, score))
    
    # Sort by score (descending)
    model_scores.sort(key=lambda x: x[1], reverse=True)
    
    return model_scores[:count]

def compare_models(models: List[str]) -> None:
    """Compare specific models side by side."""
    print("\nModel Comparison:")
    print("-" * 80)
    print(f"{'Model':<25} {'Speed':<10} {'Context':<10} {'Best For'}")
    print("-" * 80)
    
    for model in models:
        if model in PERFORMANCE_DATA:
            data = PERFORMANCE_DATA[model]
            print(f"{model:<25} {data['tok_per_s']:<10} tok/s {data['context']:<10}K {data['best_for'][:30]}")
        else:
            print(f"{model:<25} {'N/A':<10} {'N/A':<10} {'Model not found'}")

def list_models() -> None:
    """List all available models with their specs."""
    print("\nAvailable Models:")
    print("-" * 80)
    print(f"{'Model':<25} {'Speed':<10} {'Context':<10} {'Best For'}")
    print("-" * 80)
    
    for model, data in PERFORMANCE_DATA.items():
        print(f"{model:<25} {data['tok_per_s']:<10} tok/s {data['context']:<10}K {data['best_for'][:40]}")

def output_json(recommendations: List[Tuple[str, float]], task: str, priority: str, context: str) -> None:
    """Output recommendations in JSON format for Claude consumption."""
    output = {
        "query": {
            "task": task,
            "priority": priority,
            "context": context
        },
        "recommendations": [],
        "all_models": []
    }

    # Add top recommendations with reasoning
    for model, score in recommendations:
        if model in PERFORMANCE_DATA:
            data = PERFORMANCE_DATA[model]
            output["recommendations"].append({
                "model": model,
                "score": round(score, 2),
                "speed_tok_per_s": data["tok_per_s"],
                "context_k": data["context"],
                "best_for": data["best_for"],
                "reason": f"{data['best_for']} ({data['tok_per_s']} tok/s, {data['context']}K context)"
            })

    # Add all models for reference
    for model, data in PERFORMANCE_DATA.items():
        output["all_models"].append({
            "model": model,
            "speed_tok_per_s": data["tok_per_s"],
            "context_k": data["context"],
            "best_for": data["best_for"]
        })

    print(json.dumps(output, indent=2))

def main():
    """Main function."""
    args = parse_arguments()

    if args.list:
        if args.format == "json":
            output = {"models": []}
            for model, data in PERFORMANCE_DATA.items():
                output["models"].append({
                    "model": model,
                    "speed_tok_per_s": data["tok_per_s"],
                    "context_k": data["context"],
                    "best_for": data["best_for"]
                })
            print(json.dumps(output, indent=2))
        else:
            list_models()
        return

    if args.update:
        print("Updating model data from Ollama API...")
        # In a real implementation, this would call the model_fetcher module
        print("Model data updated successfully!")
        return

    if args.compare:
        if args.format == "json":
            output = {"comparison": []}
            for model in args.compare:
                if model in PERFORMANCE_DATA:
                    data = PERFORMANCE_DATA[model]
                    output["comparison"].append({
                        "model": model,
                        "speed_tok_per_s": data["tok_per_s"],
                        "context_k": data["context"],
                        "best_for": data["best_for"]
                    })
                else:
                    output["comparison"].append({
                        "model": model,
                        "error": "Model not found"
                    })
            print(json.dumps(output, indent=2))
        else:
            compare_models(args.compare)
        return

    # Default behavior - recommend models
    task = args.task or "general"
    priority = args.priority or "balanced"
    context = args.context or "medium"

    recommendations = recommend_models(task, priority, context)

    if args.format == "json":
        output_json(recommendations, task, priority, context)
    else:
        print(f"\nFinding best models for: {task}, priority: {priority}, context: {context}")

        print("\nTop Recommendations:")
        print("-" * 80)
        print(f"{'Rank':<5} {'Model':<25} {'Score':<10} {'Speed':<10} {'Context':<10}")
        print("-" * 80)

        for i, (model, score) in enumerate(recommendations, 1):
            if model in PERFORMANCE_DATA:
                data = PERFORMANCE_DATA[model]
                print(f"{i:<5} {model:<25} {score:<10.2f} {data['tok_per_s']:<10} tok/s {data['context']:<10}K")
            else:
                print(f"{i:<5} {model:<25} {score:<10.2f} {'N/A':<10} {'N/A':<10}")

if __name__ == "__main__":
    main()
