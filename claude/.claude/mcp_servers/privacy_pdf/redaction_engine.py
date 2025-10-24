"""
PII Redaction Engine
Detects and redacts personally identifiable information from text
"""
import re
import json
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime


class RedactionEngine:
    """PII detection and redaction using regex patterns"""

    # Privacy level configurations
    # NOTE: CURRENCY and ZIP_CODE removed from all levels - these are analysis data, not PII
    # ZIP codes alone don't identify individuals and cause false positives (box numbers, amounts)
    # Use preserve_patterns parameter to explicitly redact these if needed
    PRIVACY_CONFIGS = {
        "strict": {
            "patterns": [
                (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN'),
                (r'\b\d{2}-\d{7}\b', 'EIN'),
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL'),
                (r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', 'PHONE'),
                (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 'CREDIT_CARD'),
                (r'\b\d{3,4}[-\s]?\d{6,7}\b', 'ACCOUNT_NUMBER'),
                (r'\b\d{1,5}\s+[A-Za-z0-9\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir|Way)\b', 'ADDRESS'),
                (r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b', 'DATE'),
                (r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b', 'DATE'),
                (r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', 'FULL_NAME'),
                (r'\b(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?\b', 'URL')
            ]
        },
        "balanced": {
            "patterns": [
                (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN'),
                (r'\b\d{2}-\d{7}\b', 'EIN'),
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL'),
                (r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', 'PHONE'),
                (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 'CREDIT_CARD'),
                (r'\b\d{3,4}[-\s]?\d{6,7}\b', 'ACCOUNT_NUMBER'),
                (r'\b\d{1,5}\s+[A-Za-z0-9\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)\b', 'ADDRESS')
            ]
        },
        "minimal": {
            "patterns": [
                (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN'),
                (r'\b\d{2}-\d{7}\b', 'EIN'),
                (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 'CREDIT_CARD'),
                (r'\b\d{3,4}[-\s]?\d{6,7}\b', 'ACCOUNT_NUMBER')
            ]
        },
        "business": {
            "patterns": [
                # Only redact financial PII - preserve business contact info
                (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN'),
                (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 'CREDIT_CARD'),
                (r'\b\d{3,4}[-\s]?\d{6,7}\b', 'ACCOUNT_NUMBER')
            ],
            "skip_similarity_check": True  # Business content expected to stay mostly intact
        }
    }

    def __init__(self, privacy_level: str = "balanced"):
        """
        Initialize redaction engine

        Args:
            privacy_level: One of 'strict', 'balanced', 'minimal', 'business'
        """
        if privacy_level not in self.PRIVACY_CONFIGS:
            raise ValueError(f"Invalid privacy_level: {privacy_level}. Must be one of {list(self.PRIVACY_CONFIGS.keys())}")

        self.privacy_level = privacy_level
        config = self.PRIVACY_CONFIGS[privacy_level]
        self.patterns = config["patterns"]
        self.skip_similarity_check = config.get("skip_similarity_check", False)

    def redact(
        self,
        text: str,
        preserve_patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Redact PII from text

        Args:
            text: Text to redact
            preserve_patterns: Optional regex patterns to preserve (whitelist)

        Returns:
            Dict with redacted_text, audit_log, and statistics
        """
        audit_log = []
        redacted_text = text
        redaction_count = 0

        # Build preserve pattern if provided
        preserve_regex = None
        if preserve_patterns:
            try:
                preserve_regex = re.compile('|'.join(f'({p})' for p in preserve_patterns))
            except re.error as e:
                return {
                    "error": "Invalid preserve_pattern regex",
                    "details": str(e)
                }

        # Apply each PII pattern
        for pattern_str, pii_type in self.patterns:
            pattern = re.compile(pattern_str)

            for match in pattern.finditer(text):
                matched_text = match.group(0)

                # Check if this match should be preserved
                if preserve_regex and preserve_regex.search(matched_text):
                    continue  # Skip redaction for whitelisted patterns

                # Redact the match
                replacement = f"[REDACTED_{pii_type}_{redaction_count}]"
                redacted_text = redacted_text.replace(matched_text, replacement, 1)

                # Log redaction
                audit_log.append({
                    "index": redaction_count,
                    "pii_type": pii_type,
                    "original_length": len(matched_text),
                    "position": match.start(),
                    "redacted_as": replacement
                })

                redaction_count += 1

        # Calculate statistics
        stats = self._calculate_stats(text, redacted_text, audit_log)

        return {
            "redacted_text": redacted_text,
            "audit_log": audit_log,
            "statistics": stats,
            "privacy_level": self.privacy_level,
            "timestamp": datetime.now().isoformat()
        }

    def _calculate_stats(
        self,
        original: str,
        redacted: str,
        audit_log: List[Dict]
    ) -> Dict[str, Any]:
        """Calculate redaction statistics"""
        # Count by PII type
        type_counts = {}
        for entry in audit_log:
            pii_type = entry["pii_type"]
            type_counts[pii_type] = type_counts.get(pii_type, 0) + 1

        return {
            "total_redactions": len(audit_log),
            "original_length": len(original),
            "redacted_length": len(redacted),
            "reduction_bytes": len(original) - len(redacted),
            "redactions_by_type": type_counts
        }

    def validate_safety(
        self,
        text: str,
        original: Optional[str] = None,
        strict_mode: bool = True,
        preserve_patterns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate that redacted text contains no PII leakage

        Args:
            text: Redacted text to validate
            original: Optional original text for comparison
            strict_mode: If True, fail on any potential PII
            preserve_patterns: Patterns that were intentionally preserved

        Returns:
            Safety validation report
        """
        issues = []
        safe_false_positives = []
        risk_level = "LOW"

        # Re-scan for any PII patterns
        for pattern_str, pii_type in self.patterns:
            pattern = re.compile(pattern_str)
            matches = list(pattern.finditer(text))

            if matches:
                # Check if this is an intentional preserve pattern (false positive)
                if self._is_safe_false_positive(pii_type, matches, preserve_patterns):
                    safe_false_positives.append({
                        "pii_type": pii_type,
                        "found_count": len(matches),
                        "reason": "Intentionally preserved via preserve_patterns",
                        "examples": [f"[PRESERVED_{pii_type}_at_pos_{m.start()}]" for m in matches[:3]]
                    })
                else:
                    # Actual PII leakage - NEVER expose actual PII in error messages
                    issues.append({
                        "severity": "HIGH" if strict_mode else "MEDIUM",
                        "pii_type": pii_type,
                        "found_count": len(matches),
                        "examples": [f"[LEAKED_{pii_type}_at_pos_{m.start()}]" for m in matches[:3]]
                    })
                    risk_level = "HIGH"

        # If original provided, check for high similarity (possible incomplete redaction)
        # Skip for business mode - business content expected to stay mostly intact
        if original and len(original) > 0 and not self.skip_similarity_check:
            similarity = self._calculate_similarity(original, text)
            if similarity > 0.9:  # More than 90% similar
                issues.append({
                    "severity": "MEDIUM",
                    "issue": "High similarity to original",
                    "similarity_score": similarity,
                    "recommendation": "Verify redaction coverage"
                })
                if risk_level == "LOW":
                    risk_level = "MEDIUM"

        # Overall assessment
        is_safe = len(issues) == 0 or (not strict_mode and risk_level != "HIGH")

        return {
            "is_safe": is_safe,
            "risk_level": risk_level,
            "issues": issues,
            "safe_false_positives": safe_false_positives,
            "total_issues": len(issues),
            "total_safe_false_positives": len(safe_false_positives),
            "recommendation": "Safe for LLM analysis" if is_safe else "UNSAFE - contains PII leakage"
        }

    def _is_safe_false_positive(
        self,
        pii_type: str,
        matches: List,
        preserve_patterns: Optional[List[str]]
    ) -> bool:
        """
        Check if detected PII is actually a safe false positive from preserve patterns

        Args:
            pii_type: Type of PII detected (CURRENCY, DATE, etc.)
            matches: List of regex match objects
            preserve_patterns: Patterns that were intentionally preserved

        Returns:
            True if this is a safe false positive, False if actual PII leakage
        """
        # Only certain types can be false positives
        safe_types = {'CURRENCY', 'DATE', 'URL'}
        if pii_type not in safe_types:
            return False  # Names, SSNs, etc. are never false positives

        # If no preserve patterns, can't be intentional
        if not preserve_patterns:
            return False

        # Build preserve regex
        try:
            preserve_regex = re.compile('|'.join(f'({p})' for p in preserve_patterns))
        except re.error:
            return False

        # Check if all matches are within preserve patterns
        for match in matches:
            match_text = match.group(0)
            if not preserve_regex.search(match_text):
                # Found a match NOT in preserve patterns - actual PII leakage!
                return False

        # All matches are in preserve patterns - safe false positive
        return True

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Simple character-level similarity ratio"""
        if len(text1) == 0 or len(text2) == 0:
            return 0.0

        # Count matching characters
        matches = sum(c1 == c2 for c1, c2 in zip(text1, text2))
        max_len = max(len(text1), len(text2))

        return matches / max_len if max_len > 0 else 0.0

    def sanitize_response(self, response_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan entire response for PII leakage before returning to LLM

        This is a critical safety layer that prevents PII from leaking through
        error messages, metadata, or any other part of the JSON response.

        Args:
            response_dict: Response dictionary to sanitize

        Returns:
            Sanitized response dictionary

        Raises:
            Exception: If PII detected in response (prevents data leak)
        """
        # Convert to JSON to scan all nested values
        response_json = json.dumps(response_dict)

        # Check for any PII patterns in the JSON response itself
        leaked_pii = []
        for pattern_str, pii_type in self.patterns:
            pattern = re.compile(pattern_str)
            matches = list(pattern.finditer(response_json))

            if matches:
                leaked_pii.append({
                    "pii_type": pii_type,
                    "count": len(matches),
                    "positions": [m.start() for m in matches[:5]]
                })

        if leaked_pii:
            # CRITICAL: Response contains PII - block entire response
            raise Exception(
                f"CRITICAL SECURITY VIOLATION: PII detected in response metadata. "
                f"Blocked {len(leaked_pii)} PII types from leaking. "
                f"This indicates a bug in the redaction/validation logic. "
                f"Types found: {[p['pii_type'] for p in leaked_pii]}"
            )

        return response_dict
