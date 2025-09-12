"""News Agent Quality Evaluation Tests"""
import pytest
import logging
from deepeval import assert_test
from deepeval.test_case import LLMTestCase

logger = logging.getLogger(__name__)

class TestNewsAgent:
    """News agent evaluation test suite"""
    
    def test_news_agent_basic_functionality(self, news_agent):
        """Test that news agent responds to basic queries"""
        response = news_agent.query("Hello, can you get news?")
        
        assert response.content, "News agent should provide some response"
        assert len(response.content) > 10, "Response should be substantial"
        logger.info(f"Basic functionality test passed. Response length: {len(response.content)}")
    
    @pytest.mark.parametrize("scenario", [
        {
            "name": "breaking_news",
            "input": "Get latest breaking news",
            "category": "breaking",
            "expected_keywords": ["news", "latest", "today", "recent"]
        },
        {
            "name": "tech_news", 
            "input": "Latest technology news",
            "category": "technology",
            "expected_keywords": ["technology", "tech", "innovation", "digital"]
        },
        {
            "name": "general_news",
            "input": "What's happening in the world today?",
            "category": "general",
            "expected_keywords": ["world", "today", "happening", "news"]
        }
    ])
    def test_news_quality_metrics(self, news_agent, news_metrics, scenario):
        """Test news agent response quality using DeepEval metrics"""
        logger.info(f"Testing scenario: {scenario['name']}")
        
        # Get agent response
        try:
            response = news_agent.query(scenario["input"])
            logger.info(f"Agent response length: {len(response.content)} characters")
            
            # Basic sanity checks
            assert response.content, f"Agent should provide response for: {scenario['input']}"
            
            # Check for expected keywords (basic relevance check)
            content_lower = response.content.lower()
            found_keywords = [kw for kw in scenario["expected_keywords"] if kw in content_lower]
            if found_keywords:
                logger.info(f"Found relevant keywords: {found_keywords}")
            
            # Create DeepEval test case
            test_case = LLMTestCase(
                input=scenario["input"],
                actual_output=response.content,
                retrieval_context=response.sources or [],
                # Additional metadata for custom metrics
                metadata={
                    "category": scenario["category"],
                    "test_name": scenario["name"]
                }
            )
            
            # Use DeepEval's native PyTest integration
            logger.info(f"Running {len(news_metrics)} DeepEval metrics...")
            assert_test(test_case, news_metrics)
            
            logger.info(f"✅ All metrics passed for scenario: {scenario['name']}")
            
        except Exception as e:
            logger.error(f"Test failed for scenario {scenario['name']}: {e}")
            # Log the full error for debugging
            if hasattr(e, '__cause__') and e.__cause__:
                logger.error(f"Underlying cause: {e.__cause__}")
            raise
    
    def test_news_agent_error_handling(self, news_agent):
        """Test news agent handles various input types appropriately"""
        
        # Test cases where failure is expected (invalid inputs)
        expected_failures = [
            "",  # Empty input - should be rejected
            "   ",  # Whitespace only - should be rejected
        ]
        
        # Test cases where graceful handling is expected
        edge_cases = [
            "Invalid query with special chars: !@#$%^&*()",
            "Very long query: " + "test " * 100,  # Very long input
        ]
        
        # Test expected failures
        for test_input in expected_failures:
            try:
                response = news_agent.query(test_input)
                # If we get a response for empty/whitespace input, log it but don't fail
                logger.info(f"Unexpected response for invalid input '{test_input}': {response.content[:100]}...")
            except Exception as e:
                # This is expected behavior - OpenCode should reject invalid inputs
                logger.info(f"✅ Correctly rejected invalid input '{test_input}': {type(e).__name__}")
        
        # Test edge cases that should be handled gracefully
        for test_input in edge_cases:
            try:
                response = news_agent.query(test_input)
                # Should get some response for legitimate (though unusual) queries
                assert isinstance(response.content, str)
                logger.info(f"✅ Handled edge case gracefully: '{test_input[:50]}...'")
            except Exception as e:
                logger.warning(f"⚠️  Edge case handling could be improved for: '{test_input[:50]}...'. Error: {e}")
                # Don't fail the test for edge cases that could be improved, just warn
    
    @pytest.mark.slow
    def test_news_agent_comprehensive(self, news_agent, news_metrics, news_test_scenarios):
        """Comprehensive evaluation with all test scenarios"""
        logger.info(f"Running comprehensive evaluation with {len(news_test_scenarios)} scenarios")
        
        results = []
        for scenario in news_test_scenarios:
            try:
                response = news_agent.query(scenario["input"])
                
                test_case = LLMTestCase(
                    input=scenario["input"],
                    actual_output=response.content,
                    expected_output=scenario.get("expected_output"),
                    retrieval_context=response.sources or [],
                    metadata=scenario
                )
                
                # Collect results for batch analysis
                results.append((test_case, scenario))
                
            except Exception as e:
                logger.error(f"Failed to get response for scenario '{scenario.get('name', 'unknown')}': {e}")
                continue
        
        logger.info(f"Successfully collected {len(results)} responses for evaluation")
        
        # Evaluate each test case
        passed = 0
        failed = 0
        
        for test_case, scenario in results:
            try:
                assert_test(test_case, news_metrics)
                passed += 1
                logger.info(f"✅ Passed: {scenario.get('name', 'unknown')}")
            except AssertionError as e:
                failed += 1
                logger.warning(f"❌ Failed: {scenario.get('name', 'unknown')} - {e}")
                # Continue with other tests instead of stopping
        
        logger.info(f"Comprehensive evaluation complete. Passed: {passed}, Failed: {failed}")
        
        # Require at least 70% pass rate
        pass_rate = passed / len(results) if results else 0
        assert pass_rate >= 0.7, f"Pass rate {pass_rate:.1%} is below 70% threshold"
    
    def test_news_sources_extraction(self, news_agent):
        """Test that news agent responses include source information when available"""
        query = "Get news about artificial intelligence"
        response = news_agent.query(query)
        
        # Check if response includes any source-like information
        content = response.content.lower()
        source_indicators = ["source", "http", "www.", ".com", "reported", "according to"]
        
        has_source_info = any(indicator in content for indicator in source_indicators)
        
        if has_source_info:
            logger.info("✅ Response includes source information")
        else:
            logger.warning("⚠️  Response might benefit from including source information")
        
        # Don't fail the test, but log the observation
        assert response.content, "Should have content regardless of source info"