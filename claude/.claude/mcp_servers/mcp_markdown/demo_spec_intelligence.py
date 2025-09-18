#!/usr/bin/env python3
"""
Demo script for Spec Intelligence functionality.

This script demonstrates the spec intelligence capabilities by running
validation and analysis on a real specification file.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from spec_engine import SpecEngine

def demo_spec_intelligence():
    """Demonstrate spec intelligence on a real spec file."""
    print("🎯 Spec Intelligence Demo")
    print("=" * 50)
    
    # Use one of the epic task files as test input
    epic_dir = Path("/Users/smian/github-smian0/epic-spec-intelligence/.claude/epics/spec-intelligence")
    test_file = epic_dir / "001.md"
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return
    
    print(f"📄 Analyzing: {test_file.name}")
    print()
    
    # Initialize spec engine
    spec = SpecEngine()
    
    # 1. Document Validation
    print("🔍 1. DOCUMENT VALIDATION")
    print("-" * 30)
    result = spec.validate_spec_document(str(test_file))
    print(f"Valid: {'✅ Yes' if result.get('valid', False) else '❌ No'}")
    print(f"Errors: {len(result.get('errors', []))}")
    print(f"Warnings: {len(result.get('warnings', []))}")
    
    if result.get('warnings'):
        print("  Warnings:")
        for warning in result['warnings'][:3]:  # Show first 3
            print(f"    • {warning}")
    print()
    
    # 2. Semantic Analysis
    print("🧠 2. SEMANTIC ANALYSIS")
    print("-" * 30)
    result = spec.analyze_spec_semantics(str(test_file))
    req_lang = result.get('requirement_language', {})
    print(f"MUST requirements: {req_lang.get('must_count', 0)}")
    print(f"SHOULD requirements: {req_lang.get('should_count', 0)}")
    print(f"MAY requirements: {req_lang.get('may_count', 0)}")
    print(f"Ambiguity score: {result.get('ambiguity_score', 0):.3f}")
    
    clarity = result.get('spec_clarity', {})
    if clarity:
        print(f"Clarity score: {clarity.get('clarity_score', 0):.3f}")
    print()
    
    # 3. Requirements Extraction
    print("📋 3. REQUIREMENTS EXTRACTION")
    print("-" * 30)
    result = spec.extract_spec_requirements(str(test_file))
    print(f"Total requirements: {result.get('total_requirements', 0)}")
    print(f"Critical (MUST): {len(result.get('must_requirements', []))}")
    print(f"Important (SHOULD): {len(result.get('should_requirements', []))}")
    print(f"Optional (MAY): {len(result.get('may_requirements', []))}")
    print(f"Acceptance criteria: {len(result.get('acceptance_criteria', []))}")
    
    # Show some acceptance criteria
    criteria = result.get('acceptance_criteria', [])
    if criteria:
        print("  Sample acceptance criteria:")
        for criterion in criteria[:3]:  # Show first 3
            print(f"    ☐ {criterion['criterion']}")
    print()
    
    # 4. Dependencies Analysis
    print("🔗 4. DEPENDENCIES ANALYSIS")
    print("-" * 30)
    result = spec.extract_spec_dependencies(str(test_file))
    print(f"Spec references: {len(result.get('spec_references', []))}")
    print(f"Issue references: {len(result.get('issue_references', []))}")
    print(f"External dependencies: {len(result.get('external_dependencies', []))}")
    print(f"Internal dependencies: {len(result.get('internal_dependencies', []))}")
    print()
    
    # 5. Completeness Check
    print("✅ 5. COMPLETENESS VALIDATION")
    print("-" * 30)
    result = spec.validate_spec_completeness(str(test_file))
    print(f"Document type: {result.get('spec_type', 'Unknown')}")
    print(f"Completeness score: {result.get('completeness_score', 0):.2f}")
    print(f"Required sections: {len(result.get('required_sections', []))}")
    print(f"Missing sections: {len(result.get('missing_sections', []))}")
    
    missing = result.get('missing_sections', [])
    if missing:
        print("  Missing sections:")
        for section in missing[:3]:  # Show first 3
            print(f"    • {section}")
    
    recommendations = result.get('recommendations', [])
    if recommendations:
        print("  Recommendations:")
        for rec in recommendations[:3]:  # Show first 3
            print(f"    💡 {rec}")
    print()
    
    print("🎉 Demo completed successfully!")
    print()
    print("Available MCP tools:")
    print("  • validate_spec_document")
    print("  • analyze_spec_semantics")
    print("  • extract_spec_requirements")
    print("  • extract_spec_constraints")
    print("  • extract_spec_dependencies")
    print("  • validate_spec_completeness")

if __name__ == "__main__":
    demo_spec_intelligence()