"""
CompactOllamaWeb - Subclass that truncates large responses
"""
import json
from typing import Dict, Any
from agno.tools.ollama_web import OllamaWebTools


class CompactOllamaWeb(OllamaWebTools):
    """
    Subclass of OllamaWebTools that aggressively truncates responses
    to prevent "request body too large" errors.
    """

    def __init__(self, max_results: int = 1, max_citation_chars: int = 80, **kwargs):
        super().__init__(**kwargs)
        self.max_results = max_results
        self.max_citation_chars = max_citation_chars

    def _truncate_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Aggressively truncate to prevent token overflow"""
        if not isinstance(response, dict):
            print(f"  ⚠️  Response is not a dict, returning as-is")
            return response

        # Make a DEEP copy to avoid modifying cached data
        import copy
        response = copy.deepcopy(response)

        print(f"  📊 Original: {response.get('total_grounded_facts', 0)} facts in {len(response.get('results', []))} results")

        # Keep only first result
        if 'results' in response and isinstance(response['results'], list):
            orig_result_count = len(response['results'])
            response['results'] = response['results'][:self.max_results]
            print(f"  🔪 Trimmed results: {orig_result_count} → {len(response['results'])}")

            for idx, result in enumerate(response['results']):
                # Keep only first 2 facts
                if 'grounded_facts' in result and isinstance(result['grounded_facts'], list):
                    orig_fact_count = len(result['grounded_facts'])
                    result['grounded_facts'] = result['grounded_facts'][:2]
                    print(f"  🔪 Trimmed facts in result {idx}: {orig_fact_count} → {len(result['grounded_facts'])}")

                    for fact_idx, fact in enumerate(result['grounded_facts']):
                        # Keep only first citation
                        if 'citations' in fact and isinstance(fact['citations'], list):
                            orig_citation_count = len(fact['citations'])
                            fact['citations'] = fact['citations'][:1]
                            print(f"  🔪 Trimmed citations in fact {fact_idx}: {orig_citation_count} → {len(fact['citations'])}")

                            for cite_idx, citation in enumerate(fact['citations']):
                                # AGGRESSIVELY truncate text
                                if 'text' in citation:
                                    orig_len = len(citation['text'])
                                    if orig_len > self.max_citation_chars:
                                        citation['text'] = citation['text'][:self.max_citation_chars] + f"...[truncated {orig_len-self.max_citation_chars} chars]"
                                        print(f"  ✂️  Truncated citation text: {orig_len:,} → {len(citation['text']):,} chars")

        # Also truncate at the top level if there's excessive data
        if 'total_grounded_facts' in response:
            response['total_grounded_facts'] = min(response['total_grounded_facts'], 2)

        return response

    def search(self, query: str, max_results: int = None, strict: bool = True) -> str:
        """Override search to add truncation"""
        if max_results is None:
            max_results = self.max_results

        print(f"🔍 CompactOllamaWeb.search('{query[:50]}...', max={max_results})")

        # Call parent (no **kwargs to avoid conflicts with Agno's parameter passing)
        response_str = super().search(query=query, max_results=max_results, strict=strict)

        # Parse JSON string to dict
        try:
            response = json.loads(response_str) if isinstance(response_str, str) else response_str
        except json.JSONDecodeError:
            print(f"  ⚠️  Failed to parse response as JSON, returning as-is")
            return response_str

        # Truncate
        truncated = self._truncate_response(response)

        # Report size reduction
        orig_size = len(response_str)
        truncated_str = json.dumps(truncated) if isinstance(truncated, dict) else str(truncated)
        trunc_size = len(truncated_str)
        print(f"  ✂️  {orig_size:,} → {trunc_size:,} chars ({100*trunc_size//max(orig_size,1)}%)")

        return truncated_str

    def research(self, query: str, max_results: int = None) -> Dict[str, Any]:
        """Override research to add truncation"""
        if max_results is None:
            max_results = self.max_results

        print(f"📚 CompactOllamaWeb.research('{query[:50]}...', max={max_results})")
        response = super().research(query=query, max_results=max_results)
        return self._truncate_response(response)
