"""Source verification utilities for news content evaluation"""
import re
import requests
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SourceInfo:
    """Information about a detected source"""
    text: str
    url: Optional[str] = None
    organization: Optional[str] = None
    citation_format: str = "unknown"
    is_accessible: bool = False
    response_status: Optional[int] = None

@dataclass 
class SourceVerificationResult:
    """Results of source verification analysis"""
    total_sources: int
    attributed_sources: int
    accessible_sources: int
    credible_sources: int
    attribution_score: float  # 0-1
    accessibility_score: float  # 0-1
    credibility_score: float  # 0-1
    sources: List[SourceInfo]
    issues: List[str]

class SourceAttributionVerifier:
    """Verifies source attribution patterns and quality"""
    
    CREDIBLE_DOMAINS = {
        'reuters.com', 'bbc.com', 'cnn.com', 'nytimes.com', 
        'washingtonpost.com', 'apnews.com', 'bloomberg.com',
        'wsj.com', 'npr.org', 'theguardian.com', 'abc.go.com',
        'cbsnews.com', 'nbcnews.com', 'axios.com', 'politico.com'
    }
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def verify_sources(self, content: str) -> SourceVerificationResult:
        """Main source verification method"""
        sources = self._extract_sources(content)
        
        # Verify accessibility
        for source in sources:
            if source.url:
                source.is_accessible, source.response_status = self._check_url_accessibility(source.url)
        
        # Calculate scores
        attribution_score = self._calculate_attribution_score(content, sources)
        accessibility_score = self._calculate_accessibility_score(sources)
        credibility_score = self._calculate_credibility_score(sources)
        
        # Identify issues
        issues = self._identify_issues(content, sources)
        
        return SourceVerificationResult(
            total_sources=len(sources),
            attributed_sources=len([s for s in sources if s.citation_format != "unknown"]),
            accessible_sources=len([s for s in sources if s.is_accessible]),
            credible_sources=len([s for s in sources if self._is_credible_source(s)]),
            attribution_score=attribution_score,
            accessibility_score=accessibility_score,
            credibility_score=credibility_score,
            sources=sources,
            issues=issues
        )
    
    def _extract_sources(self, content: str) -> List[SourceInfo]:
        """Extract source references from content"""
        sources = []
        
        # Pattern 1: [1] Source Name - Description
        numbered_pattern = r'\[(\d+)\]\s*([^–\-\n]+)(?:[–\-]\s*([^\n]+))?'
        for match in re.finditer(numbered_pattern, content):
            source_text = match.group(2).strip()
            organization = self._extract_organization(source_text)
            sources.append(SourceInfo(
                text=source_text,
                organization=organization,
                citation_format="numbered",
                url=self._extract_url_from_text(source_text)
            ))
        
        # Pattern 2: URLs in text
        url_pattern = r'https?://[^\s\)\]\}]+'
        for match in re.finditer(url_pattern, content):
            url = match.group(0)
            sources.append(SourceInfo(
                text=url,
                url=url,
                organization=self._extract_domain(url),
                citation_format="url"
            ))
        
        # Pattern 3: "According to [Source]" patterns
        attribution_pattern = r'(?i)(?:according to|reports|sources from|per)\s+([A-Z][^,.!?]*(?:Reuters|BBC|CNN|AP|Bloomberg|Guardian|Times|Post|News)[^,.!?]*)'
        for match in re.finditer(attribution_pattern, content):
            source_text = match.group(1).strip()
            organization = self._extract_organization(source_text)
            sources.append(SourceInfo(
                text=source_text,
                organization=organization,
                citation_format="attribution"
            ))
        
        return sources
    
    def _extract_organization(self, text: str) -> Optional[str]:
        """Extract news organization from source text"""
        orgs = ['Reuters', 'BBC', 'CNN', 'AP', 'Bloomberg', 'Guardian', 'Times', 
                'Post', 'NPR', 'CBS', 'NBC', 'ABC', 'Fox', 'Politico', 'Axios']
        
        for org in orgs:
            if org.lower() in text.lower():
                return org
        return None
    
    def _extract_url_from_text(self, text: str) -> Optional[str]:
        """Try to extract URL from source text"""
        url_match = re.search(r'https?://[^\s\)\]\}]+', text)
        return url_match.group(0) if url_match else None
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            return urlparse(url).netloc.lower().replace('www.', '')
        except:
            return url
    
    def _check_url_accessibility(self, url: str) -> Tuple[bool, Optional[int]]:
        """Check if URL is accessible"""
        try:
            response = requests.head(url, timeout=self.timeout, allow_redirects=True)
            return response.status_code < 400, response.status_code
        except:
            return False, None
    
    def _is_credible_source(self, source: SourceInfo) -> bool:
        """Check if source is from credible domain"""
        if source.url:
            domain = self._extract_domain(source.url)
            return domain in self.CREDIBLE_DOMAINS
        
        if source.organization:
            return source.organization.lower() in [org.lower() for org in 
                ['Reuters', 'BBC', 'CNN', 'AP', 'Bloomberg', 'NPR', 'Guardian']]
        
        return False
    
    def _calculate_attribution_score(self, content: str, sources: List[SourceInfo]) -> float:
        """Calculate how well sources are attributed"""
        if not sources:
            return 0.0
        
        # Count claims that appear to have attribution
        claim_indicators = ['reports', 'according to', 'sources', 'officials', 'analysts']
        total_indicators = sum(len(re.findall(rf'\b{indicator}\b', content.lower())) 
                             for indicator in claim_indicators)
        
        attributed_count = len([s for s in sources if s.citation_format != "unknown"])
        
        # Score based on attribution density and quality
        if total_indicators == 0:
            return 0.8 if attributed_count > 0 else 0.0
        
        return min(1.0, attributed_count / max(total_indicators, 1))
    
    def _calculate_accessibility_score(self, sources: List[SourceInfo]) -> float:
        """Calculate what percentage of sources are accessible"""
        url_sources = [s for s in sources if s.url]
        if not url_sources:
            return 1.0  # No URLs to check - neutral score
        
        accessible = len([s for s in url_sources if s.is_accessible])
        return accessible / len(url_sources)
    
    def _calculate_credibility_score(self, sources: List[SourceInfo]) -> float:
        """Calculate credibility based on source reputation"""
        if not sources:
            return 0.0
        
        credible = len([s for s in sources if self._is_credible_source(s)])
        return credible / len(sources)
    
    def _identify_issues(self, content: str, sources: List[SourceInfo]) -> List[str]:
        """Identify potential issues with source attribution"""
        issues = []
        
        if len(sources) == 0:
            issues.append("No sources detected in content")
        elif len(sources) < 3:
            issues.append("Fewer than 3 sources detected - may indicate insufficient sourcing")
        
        url_sources = [s for s in sources if s.url]
        if url_sources:
            inaccessible = [s for s in url_sources if not s.is_accessible]
            if len(inaccessible) > len(url_sources) * 0.3:
                issues.append(f"{len(inaccessible)} of {len(url_sources)} URLs are inaccessible")
        
        credible_count = len([s for s in sources if self._is_credible_source(s)])
        if credible_count < len(sources) * 0.5:
            issues.append("Less than 50% of sources are from recognized credible outlets")
        
        # Check for attribution patterns
        if not re.search(r'(?i)(according to|reports|sources)', content):
            issues.append("Content lacks standard attribution language")
        
        return issues


class ContentStructureVerifier:
    """Verifies news content structure and formatting"""
    
    def verify_structure(self, content: str) -> Dict[str, any]:
        """Verify news content structure"""
        result = {
            "has_headline_structure": bool(re.search(r'^#+\s+.+$', content, re.MULTILINE)),
            "has_date_reference": bool(re.search(r'\b\d{4}\b|\b\d{1,2}/\d{1,2}/\d{4}\b|today|yesterday', content, re.IGNORECASE)),
            "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
            "average_paragraph_length": self._calculate_avg_paragraph_length(content),
            "has_bullet_points": bool(re.search(r'^[\-\*]\s+', content, re.MULTILINE)),
            "word_count": len(content.split()),
            "professional_formatting": self._check_professional_formatting(content)
        }
        
        # Calculate overall structure score
        structure_score = 0.0
        if result["has_headline_structure"]: structure_score += 0.2
        if result["has_date_reference"]: structure_score += 0.2
        if result["paragraph_count"] >= 3: structure_score += 0.2
        if 50 <= result["average_paragraph_length"] <= 150: structure_score += 0.2
        if result["word_count"] >= 100: structure_score += 0.2
        
        result["structure_score"] = structure_score
        return result
    
    def _calculate_avg_paragraph_length(self, content: str) -> float:
        """Calculate average paragraph length in words"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if not paragraphs:
            return 0.0
        return sum(len(p.split()) for p in paragraphs) / len(paragraphs)
    
    def _check_professional_formatting(self, content: str) -> bool:
        """Check for professional news formatting patterns"""
        indicators = [
            bool(re.search(r'\*\*[^*]+\*\*', content)),  # Bold text
            bool(re.search(r'^#+\s', content, re.MULTILINE)),  # Headlines
            bool(re.search(r'^[\-\*]\s', content, re.MULTILINE)),  # Lists
            bool(re.search(r'\[[\d]+\]', content)),  # Citations
        ]
        return sum(indicators) >= 2