#!/usr/bin/env python3
"""
Script to verify token generation speed for Ollama models.
Tests actual performance by timing model responses and calculating tokens/second.
"""

import requests
import json
import time
import sys
from typing import Dict, Tuple, Optional

def get_model_info(model_name: str) -> Optional[Dict]:
    """Get model information from Ollama API."""
    try:
        response = requests.post(f"http://localhost:11434/api/show", 
                               json={"name": model_name})
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error getting model info: {e}")
        return None

def count_tokens(text: str) -> int:
    """Simple token approximation (rough estimate)."""
    # This is a very rough approximation - in reality, tokenization is more complex
    # For more accurate results, you would use the model's specific tokenizer
    return len(text.split())

def test_model_speed(model_name: str, prompt: str = "Explain quantum computing in simple terms.") -> Tuple[float, int, float]:
    """
    Test the speed of a model by timing its response.
    
    Returns:
        Tuple of (response_time_seconds, estimated_tokens, tokens_per_second)
    """
    try:
        # Start timing
        start_time = time.time()
        
        # Make request to Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            }
        )
        
        # End timing
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")
            token_count = count_tokens(response_text)
            tokens_per_second = token_count / response_time if response_time > 0 else 0
            
            return response_time, token_count, tokens_per_second
        else:
            print(f"Error: API returned status {response.status_code}")
            return 0, 0, 0
            
    except Exception as e:
        print(f"Error testing model {model_name}: {e}")
        return 0, 0, 0

def main():
    """Main function to test models."""
    # Models to test (from CLAUDE.md)
    models_to_test = [
        "gpt-oss:120b-cloud",
        "deepseek-v3.1:671b-cloud", 
        "qwen3-coder:480b-cloud",
        "glm-4.6:cloud",
        "minimax-m2:cloud",
        "kimi-k2:1t-cloud",
        "qwen3-vl:235b-cloud"
    ]
    
    # Test specific model if provided as argument
    if len(sys.argv) > 1:
        models_to_test = [sys.argv[1]]
    
    print("Testing Ollama model speeds...\n")
    print(f"{'Model':<25} {'Time (s)':<10} {'Tokens':<8} {'Tok/s':<8} {'Context':<10}")
    print("-" * 70)
    
    results = {}
    
    for model in models_to_test:
        # Get model info first
        model_info = get_model_info(model)
        if not model_info:
            print(f"Model {model} not found or error retrieving info")
            continue
            
        # Extract context length if available
        details = model_info.get("details", {})
        model_info_section = model_info.get("model_info", {})
        
        # Try different possible keys for context length
        context_length = (
            details.get("context_length") or 
            model_info_section.get("minimaxm2.context_length") or
            model_info_section.get("llama.context_length") or
            model_info_section.get("qwen2.context_length") or
            "N/A"
        )
        
        # Test speed
        response_time, token_count, tokens_per_second = test_model_speed(model)
        
        if tokens_per_second > 0:
            print(f"{model:<25} {response_time:<10.2f} {token_count:<8} {tokens_per_second:<8.1f} {context_length:<10}")
            results[model] = {
                "response_time": response_time,
                "token_count": token_count,
                "tokens_per_second": tokens_per_second,
                "context_length": context_length
            }
        else:
            print(f"{model:<25} {'ERROR':<10} {'-':<8} {'-':<8} {context_length:<10}")
    
    # Save results to file
    if results:
        with open("ollama_speed_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to ollama_speed_results.json")
        
        # Generate markdown table for CLAUDE.md
        print("\nMarkdown table for CLAUDE.md:")
        print("| Model ID | Context | Tok/s | Best For | Tools | Notes |")
        print("|----------|---------|-------|----------|-------|-------|")
        
        # Sort by tokens per second (descending)
        sorted_results = sorted(results.items(), key=lambda x: x[1]["tokens_per_second"], reverse=True)
        
        for model, data in sorted_results:
            context = data["context_length"]
            tok_s = f"**{data['tokens_per_second']:.0f}**"
            
            # Use existing descriptions for known models
            descriptions = {
                "gpt-oss:120b-cloud": "General purpose, research, high-throughput",
                "deepseek-v3.1:671b-cloud": "Reasoning, analysis, balanced tasks",
                "qwen3-coder:480b-cloud": "Code generation, software engineering",
                "glm-4.6:cloud": "Autonomous agents, search, structured output",
                "minimax-m2:cloud": "Balanced performance, general tasks",
                "kimi-k2:1t-cloud": "Frontend dev, UI tasks, concise responses",
                "qwen3-vl:235b-cloud": "Vision, OCR, GUI, multimodal"
            }
            
            best_for = descriptions.get(model, "General tasks")
            tools = "✅"  # Assuming all support tools
            notes = "Verified speed" if model == "minimax-m2:cloud" else ""
            
            print(f"| `{model}` | {context}K | {tok_s} | {best_for} | {tools} | {notes} |")

if __name__ == "__main__":
    main()
