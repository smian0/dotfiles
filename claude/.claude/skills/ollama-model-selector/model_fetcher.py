#!/usr/bin/env python3
"""
Model Fetcher - Fetches latest Ollama models from API.

This module handles fetching and parsing model data from Ollama's API
to keep the model selector current with the latest models.
"""

import json
import requests
from typing import Dict, List, Optional

def fetch_ollama_models() -> Dict[str, Dict]:
    """Fetch latest cloud models from Ollama API."""
    try:
        response = requests.get("https://ollama.com/search?c=cloud")
        if response.status_code == 200:
            data = response.json()
            models = {}
            
            # Parse model data from search results
            for model in data.get("models", []):
                name = model.get("name", "")
                if name and "cloud" in name:
                    # Extract model info
                    model_info = {
                        "name": name,
                        "context": model.get("context", {}).get("context_length", 0),
                        "parameters": model.get("details", {}).get("parameter_size", ""),
                        "family": model.get("details", {}).get("family", "")
                    }
                    models[name] = model_info
            
            return models
        else:
            print(f"Error fetching models: {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error fetching models: {e}")
        return {}

def save_models_to_cache(models: Dict[str, Dict], cache_file: str) -> None:
    """Save fetched models to cache file."""
    try:
        with open(cache_file, 'w') as f:
            json.dump(models, f, indent=2)
        print(f"Saved {len(models)} models to {cache_file}")
    except Exception as e:
        print(f"Error saving models: {e}")

def load_cached_models(cache_file: str) -> Dict[str, Dict]:
    """Load cached models if available."""
    try:
        with open(cache_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading cache: {e}")
        return {}

def merge_with_performance_data(ollama_models: Dict[str, Dict], performance_file: str) -> Dict[str, Dict]:
    """Merge Ollama models with our verified performance data."""
    try:
        with open(performance_file, 'r') as f:
            performance_data = json.load(f)
    except FileNotFoundError:
        performance_data = {}
    
    # Merge performance data
    for model_name, model_info in ollama_models.items():
        if model_name in performance_data:
            model_info["tok_per_s"] = performance_data[model_name].get("tok_per_s", 0)
            model_info["best_for"] = performance_data[model_name].get("best_for", "")
    
    return ollama_models

if __name__ == "__main__":
    # Example usage
    models = fetch_ollama_models()
    cache_file = "models_cache.json"
    
    # Save to cache
    save_models_to_cache(models, cache_file)
    
    # Load performance data and merge
    merged_models = merge_with_performance_data(models, "performance_data.json")
    
    # Print merged data
    print(json.dumps(merged_models, indent=2))
