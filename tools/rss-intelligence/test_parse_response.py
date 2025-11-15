#!/usr/bin/env python3
"""Test the parse_graphiti_response function with real agent output."""

import json
import re

def parse_graphiti_response(content: str):
    """Parse agent response to extract JSON results."""
    try:
        # Try direct JSON parse first
        return json.loads(content)
    except json.JSONDecodeError:
        # Extract JSON from text
        json_match = re.search(r'\{.*\}|\[.*\]', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        raise ValueError(f"Could not find JSON in response: {content[:200]}")


# Test with sample agent response that might have trailing commas or other issues
test_cases = [
    # Case 1: Clean JSON
    '{"nodes": [{"name": "Iran", "uuid": "123"}]}',

    # Case 2: JSON embedded in text
    'The search found: {"nodes": [{"name": "Iran"}]} - done',

    # Case 3: Multiline JSON
    '''{
  "message": "Success",
  "nodes": [
    {"name": "Test"}
  ]
}''',

    # Case 4: JSON with trailing comma (invalid)
    '{"nodes": [{"name": "Test",}]}',  # This will fail
]

print("Testing parse_graphiti_response function:")
print("=" * 80)

for i, test in enumerate(test_cases, 1):
    print(f"\nTest {i}:")
    print(f"Input: {test[:100]}...")
    try:
        result = parse_graphiti_response(test)
        print(f"✅ SUCCESS: {result}")
    except Exception as e:
        print(f"❌ FAILED: {e}")

# Test the actual error you reported
print("\n" + "=" * 80)
print("Testing error case: 'Expecting ',' delimiter: line 20 column 7 (char 616)'")
print("=" * 80)

# This suggests malformed JSON with missing comma
malformed_json = '''{
  "nodes": [
    {
      "name": "Entity1"
      "uuid": "123"
    }
  ]
}'''

print(f"Input:\n{malformed_json}")
try:
    result = parse_graphiti_response(malformed_json)
    print(f"✅ SUCCESS: {result}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    print("\nThis is expected - the JSON is malformed (missing comma after 'name')")
