#!/usr/bin/env python3
"""
Demo script showing DeepEval + OpenCode integration
Run a single news agent evaluation with DeepEval metrics using Ollama
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'utils'))

from opencode_client import OpenCodeClient  
from deepeval_helpers import get_ollama_model, load_agent_metrics
from deepeval.test_case import LLMTestCase
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

def main():
    print("🚀 OpenCode + DeepEval Integration Demo")
    print("=" * 50)
    
    # Initialize OpenCode client
    print("📡 Initializing OpenCode client...")
    client = OpenCodeClient()
    news_agent = client.get_agent("news")
    
    # Set up Ollama model for evaluation
    print("🤖 Setting up Ollama model for evaluation...")
    ollama_model = get_ollama_model()
    
    # Create a simple evaluation metric
    relevancy_metric = GEval(
        name="NewsRelevancy",
        criteria="Evaluate if the response contains relevant, current news information that addresses the user's request",
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=0.7,
        model=ollama_model
    )
    
    # Test query
    test_query = "Latest tech news"
    print(f"\n📰 Testing news agent with query: '{test_query}'")
    print("⏳ Getting news from OpenCode agent (this may take a minute)...")
    
    try:
        # Get response from news agent
        response = news_agent.query(test_query)
        print(f"✅ Got response! Length: {len(response.content)} characters")
        
        # Show a snippet of the response
        snippet = response.content[:200] + "..." if len(response.content) > 200 else response.content
        print(f"\n📖 Response preview:\n{snippet}")
        
        # Create DeepEval test case
        print(f"\n🔍 Evaluating response quality with DeepEval...")
        test_case = LLMTestCase(
            input=test_query,
            actual_output=response.content,
            retrieval_context=response.sources or []
        )
        
        # Run evaluation
        print("⚙️  Running NewsRelevancy evaluation...")
        relevancy_metric.measure(test_case)
        
        # Display results
        print(f"\n📊 Evaluation Results:")
        print(f"   Score: {relevancy_metric.score:.2f}/1.0")
        print(f"   Threshold: {relevancy_metric.threshold}")
        print(f"   Passed: {'✅ Yes' if relevancy_metric.score >= relevancy_metric.threshold else '❌ No'}")
        print(f"   Reason: {relevancy_metric.reason}")
        
        print(f"\n🎉 Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())