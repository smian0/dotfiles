"""Custom DeepEval metrics for source-based news evaluation"""
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
from deepeval.metrics.utils import construct_verbose_logs
try:
    from .source_verification import SourceAttributionVerifier, ContentStructureVerifier
except ImportError:
    from source_verification import SourceAttributionVerifier, ContentStructureVerifier
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

class SourceAttributionMetric(BaseMetric):
    """Verifies source attribution quality in news content"""
    
    def __init__(
        self,
        threshold: float = 0.7,
        include_reason: bool = True,
        timeout: int = 10,
        async_mode: bool = False
    ):
        self.threshold = threshold
        self.include_reason = include_reason
        self.timeout = timeout
        self.async_mode = async_mode
        self.verifier = SourceAttributionVerifier(timeout=timeout)
    
    def measure(self, test_case: LLMTestCase) -> float:
        """Measure source attribution quality"""
        try:
            # Get the actual output from the test case
            content = test_case.actual_output
            if not content:
                self.reason = "No content provided for evaluation"
                return 0.0
            
            # Perform source verification
            result = self.verifier.verify_sources(content)
            
            # Calculate combined score (weighted average)
            combined_score = (
                result.attribution_score * 0.4 +      # 40% - How well claims are attributed
                result.accessibility_score * 0.3 +    # 30% - How many sources are accessible  
                result.credibility_score * 0.3        # 30% - How credible the sources are
            )
            
            # Generate detailed reason
            if self.include_reason:
                self.reason = self._generate_reason(result, combined_score)
            
            # Store detailed results for debugging
            self.source_details = {
                "total_sources": result.total_sources,
                "attributed_sources": result.attributed_sources,
                "accessible_sources": result.accessible_sources,
                "credible_sources": result.credible_sources,
                "attribution_score": result.attribution_score,
                "accessibility_score": result.accessibility_score,
                "credibility_score": result.credibility_score,
                "issues": result.issues,
                "sources": [{"text": s.text, "org": s.organization, "accessible": s.is_accessible} 
                           for s in result.sources]
            }
            
            logger.info(f"Source attribution analysis: {combined_score:.3f} "
                       f"({result.total_sources} sources, {len(result.issues)} issues)")
            
            # Store score for is_successful() method
            self.score = combined_score
            return combined_score
            
        except Exception as e:
            logger.error(f"Source attribution metric failed: {e}")
            self.reason = f"Evaluation failed: {str(e)}"
            return 0.0
    
    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Async wrapper for measure method"""
        return self.measure(test_case)
    
    def is_successful(self) -> bool:
        """Check if metric passes threshold"""
        return hasattr(self, 'score') and self.score is not None and self.score >= self.threshold
    
    def _generate_reason(self, result, score: float) -> str:
        """Generate human-readable reason for the score"""
        parts = []
        
        # Overall assessment
        if score >= 0.8:
            parts.append("✅ Excellent source attribution")
        elif score >= 0.6:
            parts.append("⚠️ Good source attribution with room for improvement")
        else:
            parts.append("❌ Poor source attribution")
        
        # Specific details
        parts.append(f"Found {result.total_sources} sources total")
        
        if result.attributed_sources < result.total_sources:
            parts.append(f"Only {result.attributed_sources}/{result.total_sources} properly attributed")
        
        if result.accessible_sources < len([s for s in result.sources if s.url]):
            url_count = len([s for s in result.sources if s.url])
            parts.append(f"Only {result.accessible_sources}/{url_count} URLs accessible")
        
        if result.credible_sources < result.total_sources:
            parts.append(f"Only {result.credible_sources}/{result.total_sources} from credible outlets")
        
        # Issues
        if result.issues:
            parts.append(f"Issues: {'; '.join(result.issues)}")
        
        return " | ".join(parts)
    
    @property
    def __name__(self):
        return "Source Attribution"


class ContentStructureMetric(BaseMetric):
    """Verifies news content structure and professional formatting"""
    
    def __init__(
        self,
        threshold: float = 0.7,
        include_reason: bool = True,
        async_mode: bool = False
    ):
        self.threshold = threshold
        self.include_reason = include_reason
        self.async_mode = async_mode
        self.verifier = ContentStructureVerifier()
    
    def measure(self, test_case: LLMTestCase) -> float:
        """Measure content structure quality"""
        try:
            content = test_case.actual_output
            if not content:
                self.reason = "No content provided for evaluation"
                return 0.0
            
            # Analyze structure
            structure_result = self.verifier.verify_structure(content)
            score = structure_result["structure_score"]
            
            # Generate reason
            if self.include_reason:
                self.reason = self._generate_reason(structure_result, score)
            
            # Store details
            self.structure_details = structure_result
            
            logger.info(f"Content structure analysis: {score:.3f} "
                       f"({structure_result['word_count']} words, "
                       f"{structure_result['paragraph_count']} paragraphs)")
            
            # Store score for is_successful() method
            self.score = score
            return score
            
        except Exception as e:
            logger.error(f"Content structure metric failed: {e}")
            self.reason = f"Evaluation failed: {str(e)}"
            return 0.0
    
    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Async wrapper for measure method"""
        return self.measure(test_case)
    
    def is_successful(self) -> bool:
        return hasattr(self, 'score') and self.score is not None and self.score >= self.threshold
    
    def _generate_reason(self, result, score: float) -> str:
        """Generate reason for structure score"""
        parts = []
        
        if score >= 0.8:
            parts.append("✅ Excellent content structure")
        elif score >= 0.6:
            parts.append("⚠️ Good structure with minor issues")
        else:
            parts.append("❌ Poor content structure")
        
        parts.append(f"{result['word_count']} words, {result['paragraph_count']} paragraphs")
        
        if result["has_headline_structure"]:
            parts.append("proper headlines")
        else:
            parts.append("missing headline structure")
        
        if result["has_date_reference"]:
            parts.append("includes date references")
        
        if result["professional_formatting"]:
            parts.append("professional formatting")
        else:
            parts.append("needs formatting improvement")
        
        if result["average_paragraph_length"] < 30:
            parts.append("paragraphs too short")
        elif result["average_paragraph_length"] > 200:
            parts.append("paragraphs too long")
        
        return " | ".join(parts)
    
    @property
    def __name__(self):
        return "Content Structure"


class NewsCompletenessMetric(BaseMetric):
    """Verifies completeness of news coverage (5W1H: Who, What, When, Where, Why, How)"""
    
    def __init__(
        self,
        threshold: float = 0.6,
        include_reason: bool = True,
        async_mode: bool = False
    ):
        self.threshold = threshold
        self.include_reason = include_reason
        self.async_mode = async_mode
    
    def measure(self, test_case: LLMTestCase) -> float:
        """Measure news completeness using 5W1H framework"""
        try:
            content = test_case.actual_output.lower()
            if not content:
                self.reason = "No content provided for evaluation"
                return 0.0
            
            # Check for 5W1H elements
            checks = {
                "who": self._check_who(content),
                "what": self._check_what(content), 
                "when": self._check_when(content),
                "where": self._check_where(content),
                "why": self._check_why(content),
                "how": self._check_how(content)
            }
            
            # Calculate score (each element worth ~16.7%)
            score = sum(checks.values()) / len(checks)
            
            # Generate reason
            if self.include_reason:
                self.reason = self._generate_reason(checks, score)
            
            self.completeness_details = checks
            
            # Store score for is_successful() method
            self.score = score
            return score
            
        except Exception as e:
            logger.error(f"News completeness metric failed: {e}")
            self.reason = f"Evaluation failed: {str(e)}"
            return 0.0
    
    async def a_measure(self, test_case: LLMTestCase) -> float:
        """Async wrapper for measure method"""
        return self.measure(test_case)
    
    def _check_who(self, content: str) -> bool:
        """Check for people/organizations mentioned"""
        patterns = [r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', r'\bpresident\b', r'\bminister\b', 
                   r'\bofficial\b', r'\bcompany\b', r'\borganization\b']
        return any(len(__import__('re').findall(pattern, content)) > 0 for pattern in patterns)
    
    def _check_what(self, content: str) -> bool:
        """Check for events/actions described"""
        patterns = [r'\bannounce\b', r'\breport\b', r'\bsay\b', r'\bstate\b', r'\bdeclar\b',
                   r'\blaunch\b', r'\brelease\b', r'\bconfirm\b']
        return any(word in content for word in patterns)
    
    def _check_when(self, content: str) -> bool:
        """Check for time references"""
        patterns = [r'\btoday\b', r'\byesterday\b', r'\bthis week\b', r'\brecent\b',
                   r'\b\d{1,2}/\d{1,2}/\d{4}\b', r'\b\d{4}\b', r'\bmonday\b', r'\btuesday\b']
        return any(__import__('re').search(pattern, content) for pattern in patterns)
    
    def _check_where(self, content: str) -> bool:
        """Check for location references"""
        patterns = [r'\b[A-Z][a-z]+ [A-Z][a-z]+\b.*(?:city|state|country|region)\b',
                   r'\bwashington\b', r'\blondon\b', r'\bparis\b', r'\btokyo\b', r'\bbeijing\b']
        return any(__import__('re').search(pattern, content, __import__('re').IGNORECASE) for pattern in patterns)
    
    def _check_why(self, content: str) -> bool:
        """Check for reasons/motivations"""
        patterns = [r'\bbecause\b', r'\bdue to\b', r'\bin order to\b', r'\baimed at\b',
                   r'\bto address\b', r'\bresponse to\b', r'\bresult of\b']
        return any(phrase in content for phrase in patterns)
    
    def _check_how(self, content: str) -> bool:
        """Check for methods/processes"""
        patterns = [r'\bthrough\b', r'\bby\b', r'\busing\b', r'\bvia\b', r'\bmethod\b',
                   r'\bprocess\b', r'\bapproach\b', r'\bstrategy\b']
        return any(word in content for word in patterns)
    
    def _generate_reason(self, checks: dict, score: float) -> str:
        """Generate reason for completeness score"""
        present = [k.upper() for k, v in checks.items() if v]
        missing = [k.upper() for k, v in checks.items() if not v]
        
        parts = []
        if score >= 0.8:
            parts.append("✅ Comprehensive news coverage")
        elif score >= 0.6:
            parts.append("⚠️ Good coverage with some gaps")
        else:
            parts.append("❌ Incomplete news coverage")
        
        if present:
            parts.append(f"Covers: {', '.join(present)}")
        if missing:
            parts.append(f"Missing: {', '.join(missing)}")
        
        return " | ".join(parts)
    
    def is_successful(self) -> bool:
        return hasattr(self, 'score') and self.score is not None and self.score >= self.threshold
    
    @property
    def __name__(self):
        return "News Completeness"