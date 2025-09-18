#!/usr/bin/env python3
"""
Test script for Spec Intelligence MCP integration.

This script tests the spec validation functionality by running it against
a sample specification document.
"""

import sys
import tempfile
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from spec_engine import SpecEngine

def create_test_spec_file():
    """Create a test specification file."""
    content = """---
name: test-spec
status: draft
created: 2025-09-17
type: PRD
---

# Test Product Requirements Document

## Overview
This is a test specification document for validating the spec intelligence system.

## Requirements

### Functional Requirements
The system MUST provide validation capabilities for specification documents.
The system SHOULD detect ambiguous language in requirements.
Users MAY configure validation rules according to their needs.

### Non-Functional Requirements
The system MUST NOT exceed 100MB memory usage.
Performance SHOULD be optimized for large specification files.

## Acceptance Criteria
- [ ] System validates specification structure
- [ ] System detects RFC 2119 compliance issues
- [ ] System provides actionable feedback
- [ ] System integrates with existing workflows

## Dependencies
This specification depends on [Epic-001] and references issue #1234.

## Implementation Notes
TODO: Add performance benchmarks
The implementation details are TBD.
"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        return f.name

def test_spec_engine():
    """Test the SpecEngine functionality."""
    print("Testing Spec Intelligence Engine...")
    
    # Create test file
    test_file = create_test_spec_file()
    print(f"Created test file: {test_file}")
    
    # Initialize engine
    spec_engine = SpecEngine()
    
    try:
        # Test 1: Document validation
        print("\n1. Testing document validation...")
        result = spec_engine.validate_spec_document(test_file)
        print(f"   Valid: {result.get('valid', 'unknown')}")
        print(f"   Errors: {len(result.get('errors', []))}")
        print(f"   Warnings: {len(result.get('warnings', []))}")
        
        # Test 2: Semantic analysis
        print("\n2. Testing semantic analysis...")
        result = spec_engine.analyze_spec_semantics(test_file)
        req_lang = result.get('requirement_language', {})
        print(f"   MUST count: {req_lang.get('must_count', 0)}")
        print(f"   SHOULD count: {req_lang.get('should_count', 0)}")
        print(f"   Ambiguity score: {result.get('ambiguity_score', 0)}")
        
        # Test 3: Requirements extraction
        print("\n3. Testing requirements extraction...")
        result = spec_engine.extract_spec_requirements(test_file)
        print(f"   Total requirements: {result.get('total_requirements', 0)}")
        print(f"   MUST requirements: {len(result.get('must_requirements', []))}")
        print(f"   Acceptance criteria: {len(result.get('acceptance_criteria', []))}")
        
        # Test 4: Dependencies extraction
        print("\n4. Testing dependencies extraction...")
        result = spec_engine.extract_spec_dependencies(test_file)
        print(f"   Spec references: {len(result.get('spec_references', []))}")
        print(f"   Issue references: {len(result.get('issue_references', []))}")
        
        # Test 5: Completeness validation
        print("\n5. Testing completeness validation...")
        result = spec_engine.validate_spec_completeness(test_file)
        print(f"   Spec type: {result.get('spec_type', 'unknown')}")
        print(f"   Completeness score: {result.get('completeness_score', 0):.2f}")
        print(f"   Missing sections: {len(result.get('missing_sections', []))}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        Path(test_file).unlink(missing_ok=True)
        print(f"Cleaned up test file: {test_file}")

def test_mcp_server_import():
    """Test that the MCP server can be imported with spec integration."""
    print("\nTesting MCP server import...")
    
    try:
        # This should import without errors
        import server
        print("✅ MCP server imported successfully")
        
        # Check that spec engine is initialized
        if hasattr(server, 'spec'):
            print("✅ Spec engine initialized in server")
        else:
            print("❌ Spec engine not found in server")
            
        # Check that spec tools are available
        mcp_tools = [
            'validate_spec_document',
            'analyze_spec_semantics', 
            'extract_spec_requirements',
            'extract_spec_constraints',
            'extract_spec_dependencies',
            'validate_spec_completeness'
        ]
        
        missing_tools = []
        for tool in mcp_tools:
            if not hasattr(server, tool):
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"❌ Missing MCP tools: {missing_tools}")
        else:
            print("✅ All spec MCP tools are available")
            
    except Exception as e:
        print(f"❌ MCP server import failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Spec Intelligence Integration Test")
    print("=" * 40)
    
    # Test the spec engine directly
    test_spec_engine()
    
    # Test MCP server integration
    test_mcp_server_import()
    
    print("\nTest completed.")