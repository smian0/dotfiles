"""
Specification-focused markdown processing engine.

This module provides spec-specific validation, semantic analysis, and structured
data extraction for specification documents including PRDs, technical specs,
and requirements documents.
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

try:
    from .core import PATTERNS, MarkdownParser, MarkdownError, safe_findall, safe_finditer, safe_search
except ImportError:
    from core import PATTERNS, MarkdownParser, MarkdownError, safe_findall, safe_finditer, safe_search


class SpecPatterns:
    """Specification-specific regex patterns."""
    
    # RFC 2119 requirement language patterns
    MUST = re.compile(r'\b(MUST|SHALL|REQUIRED|MANDATORY)\b', re.IGNORECASE)
    SHOULD = re.compile(r'\b(SHOULD|RECOMMENDED)\b', re.IGNORECASE)
    MAY = re.compile(r'\b(MAY|OPTIONAL|CAN)\b', re.IGNORECASE)
    MUST_NOT = re.compile(r'\b(MUST NOT|SHALL NOT|FORBIDDEN)\b', re.IGNORECASE)
    SHOULD_NOT = re.compile(r'\b(SHOULD NOT|NOT RECOMMENDED)\b', re.IGNORECASE)
    
    # Spec structure patterns
    ACCEPTANCE_CRITERIA = re.compile(r'^- \[ \]\s+(.+)$', re.MULTILINE)
    REQUIREMENTS = re.compile(r'^#{2,3}\s+(Requirements?|Functional Requirements|Non-Functional Requirements)', re.MULTILINE | re.IGNORECASE)
    CONSTRAINTS = re.compile(r'^#{2,3}\s+(Constraints?|Limitations?|Assumptions?)', re.MULTILINE | re.IGNORECASE)
    DEPENDENCIES = re.compile(r'^#{2,3}\s+(Dependencies|Prerequisites|Dependencies & Requirements)', re.MULTILINE | re.IGNORECASE)
    
    # Cross-reference patterns
    SPEC_REFERENCES = re.compile(r'\[(PRD|Epic|Task|Spec)[\s-]*(\d+|[A-Za-z-]+)\]', re.IGNORECASE)
    ISSUE_REFERENCES = re.compile(r'#(\d+)')
    
    # Vague language patterns (ambiguity detection)
    VAGUE_TERMS = re.compile(r'\b(fast|quick|slow|large|small|many|few|some|several|appropriate|reasonable|sufficient|adequate|good|bad|better|worse|easy|hard|simple|complex|user-friendly|intuitive|seamless|robust|scalable|flexible|efficient|optimized)\b', re.IGNORECASE)
    
    # Missing implementation details
    IMPLEMENTATION_GAPS = re.compile(r'\b(TBD|TODO|FIXME|XXX|placeholder|to be determined|implementation details|specifics to follow)\b', re.IGNORECASE)


class SpecEngine:
    """Engine for specification document validation and analysis."""
    
    def _parse_frontmatter(self, file_path: str) -> Dict[str, Any]:
        """Parse frontmatter from a markdown file."""
        try:
            content = MarkdownParser.read_file(file_path)
            match = safe_search(PATTERNS.FRONTMATTER, content)
            
            if not match:
                return {}
            
            # Simple key:value parsing
            metadata = {}
            for line in match.group(1).split('\n'):
                if ':' in line and not line.strip().startswith('#'):
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip().strip('"\'[]')
            
            return metadata
            
        except Exception:
            return {}
    
    def validate_spec_document(self, file_path: str) -> Dict[str, Any]:
        """Comprehensive validation of a specification document."""
        try:
            content = MarkdownParser.read_file(file_path)
            frontmatter = self._parse_frontmatter(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
        
        validation_results = {
            "file": file_path,
            "valid": True,
            "errors": [],
            "warnings": [],
            "structure_check": self._validate_structure(content, frontmatter),
            "content_check": self._validate_content(content),
            "completeness_check": self._validate_completeness(content),
            "cross_references": self._validate_cross_references(content)
        }
        
        # Aggregate validation status
        if validation_results["structure_check"]["errors"] or validation_results["content_check"]["errors"]:
            validation_results["valid"] = False
            validation_results["errors"] = (
                validation_results["structure_check"]["errors"] + 
                validation_results["content_check"]["errors"]
            )
        
        validation_results["warnings"] = (
            validation_results["structure_check"]["warnings"] + 
            validation_results["content_check"]["warnings"] +
            validation_results["completeness_check"]["warnings"]
        )
        
        return validation_results
    
    def analyze_spec_semantics(self, file_path: str) -> Dict[str, Any]:
        """Analyze semantic patterns in specification documents."""
        try:
            content = MarkdownParser.read_file(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        
        semantics = {
            "file": file_path,
            "requirement_language": self._analyze_requirement_language(content),
            "ambiguity_score": self._calculate_ambiguity_score(content),
            "implementation_gaps": self._find_implementation_gaps(content),
            "spec_clarity": self._assess_clarity(content)
        }
        
        return semantics
    
    def extract_spec_requirements(self, file_path: str) -> Dict[str, Any]:
        """Extract structured requirements from specification documents."""
        try:
            content = MarkdownParser.read_file(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        
        requirements = {
            "file": file_path,
            "must_requirements": self._extract_requirements_by_type(content, SpecPatterns.MUST),
            "should_requirements": self._extract_requirements_by_type(content, SpecPatterns.SHOULD),
            "may_requirements": self._extract_requirements_by_type(content, SpecPatterns.MAY),
            "acceptance_criteria": self._extract_acceptance_criteria(content),
            "total_requirements": 0
        }
        
        requirements["total_requirements"] = (
            len(requirements["must_requirements"]) +
            len(requirements["should_requirements"]) + 
            len(requirements["may_requirements"])
        )
        
        return requirements
    
    def extract_spec_constraints(self, file_path: str) -> Dict[str, Any]:
        """Extract constraints and limitations from specification documents."""
        try:
            content = MarkdownParser.read_file(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        
        constraints = {
            "file": file_path,
            "technical_constraints": self._extract_constraints_by_section(content, "technical"),
            "business_constraints": self._extract_constraints_by_section(content, "business"),
            "resource_constraints": self._extract_constraints_by_section(content, "resource"),
            "must_not_requirements": self._extract_requirements_by_type(content, SpecPatterns.MUST_NOT),
            "should_not_requirements": self._extract_requirements_by_type(content, SpecPatterns.SHOULD_NOT)
        }
        
        return constraints
    
    def extract_spec_dependencies(self, file_path: str) -> Dict[str, Any]:
        """Extract dependencies and cross-references from specification documents."""
        try:
            content = MarkdownParser.read_file(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        
        dependencies = {
            "file": file_path,
            "spec_references": self._extract_spec_references(content),
            "issue_references": self._extract_issue_references(content),
            "external_dependencies": self._extract_external_dependencies(content),
            "internal_dependencies": self._extract_internal_dependencies(content)
        }
        
        return dependencies
    
    def validate_spec_completeness(self, file_path: str) -> Dict[str, Any]:
        """Validate completeness of specification documents against templates."""
        try:
            content = MarkdownParser.read_file(file_path)
            frontmatter = self._parse_frontmatter(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        
        # Determine spec type from frontmatter or content
        spec_type = self._determine_spec_type(frontmatter, content)
        
        completeness = {
            "file": file_path,
            "spec_type": spec_type,
            "required_sections": self._get_required_sections(spec_type),
            "present_sections": self._extract_sections(content),
            "missing_sections": [],
            "completeness_score": 0.0,
            "recommendations": []
        }
        
        # Calculate missing sections
        for required in completeness["required_sections"]:
            if not any(required.lower() in section.lower() for section in completeness["present_sections"]):
                completeness["missing_sections"].append(required)
        
        # Calculate completeness score
        if completeness["required_sections"]:
            score = 1.0 - (len(completeness["missing_sections"]) / len(completeness["required_sections"]))
            completeness["completeness_score"] = max(0.0, score)
        
        # Generate recommendations
        if completeness["missing_sections"]:
            completeness["recommendations"].extend([
                f"Add missing section: {section}" for section in completeness["missing_sections"]
            ])
        
        return completeness
    
    # Helper methods
    def _validate_structure(self, content: str, frontmatter: Dict) -> Dict[str, Any]:
        """Validate document structure."""
        errors = []
        warnings = []
        
        # Check for required frontmatter fields
        required_fields = ["name", "status", "created"]
        for field in required_fields:
            if field not in frontmatter:
                errors.append(f"Missing required frontmatter field: {field}")
        
        # Check for proper header hierarchy
        headers = safe_findall(PATTERNS.HEADERS, content)
        if not headers:
            warnings.append("No headers found in document")
        
        return {"errors": errors, "warnings": warnings}
    
    def _validate_content(self, content: str) -> Dict[str, Any]:
        """Validate content quality."""
        errors = []
        warnings = []
        
        # Check for broken cross-references
        spec_refs = safe_findall(SpecPatterns.SPEC_REFERENCES, content)
        for ref in spec_refs:
            # This is a simplified check - in practice would validate against actual refs
            if "BROKEN" in ref[0].upper():
                errors.append(f"Broken specification reference: {ref[0]}")
        
        # Check for implementation gaps
        gaps = safe_findall(SpecPatterns.IMPLEMENTATION_GAPS, content)
        if gaps:
            warnings.extend([f"Implementation gap found: {gap}" for gap in gaps[:5]])  # Limit to 5
        
        return {"errors": errors, "warnings": warnings}
    
    def _validate_completeness(self, content: str) -> Dict[str, Any]:
        """Validate document completeness."""
        warnings = []
        
        # Check for acceptance criteria
        criteria = safe_findall(SpecPatterns.ACCEPTANCE_CRITERIA, content)
        if not criteria:
            warnings.append("No acceptance criteria found")
        
        # Check for requirement language
        must_count = len(safe_findall(SpecPatterns.MUST, content))
        should_count = len(safe_findall(SpecPatterns.SHOULD, content))
        
        if must_count == 0 and should_count == 0:
            warnings.append("No formal requirement language found (MUST, SHOULD)")
        
        return {"warnings": warnings}
    
    def _validate_cross_references(self, content: str) -> Dict[str, Any]:
        """Validate cross-references in the document."""
        spec_refs = safe_findall(SpecPatterns.SPEC_REFERENCES, content)
        issue_refs = safe_findall(SpecPatterns.ISSUE_REFERENCES, content)
        
        return {
            "spec_references": [{"type": ref[0], "id": ref[1]} for ref in spec_refs],
            "issue_references": [{"id": ref} for ref in issue_refs],
            "total_references": len(spec_refs) + len(issue_refs)
        }
    
    def _analyze_requirement_language(self, content: str) -> Dict[str, Any]:
        """Analyze RFC 2119 requirement language usage."""
        return {
            "must_count": len(safe_findall(SpecPatterns.MUST, content)),
            "should_count": len(safe_findall(SpecPatterns.SHOULD, content)),
            "may_count": len(safe_findall(SpecPatterns.MAY, content)),
            "must_not_count": len(safe_findall(SpecPatterns.MUST_NOT, content)),
            "should_not_count": len(safe_findall(SpecPatterns.SHOULD_NOT, content))
        }
    
    def _calculate_ambiguity_score(self, content: str) -> float:
        """Calculate ambiguity score based on vague language usage."""
        vague_terms = safe_findall(SpecPatterns.VAGUE_TERMS, content)
        word_count = len(content.split())
        
        if word_count == 0:
            return 0.0
        
        # Ambiguity score: percentage of vague terms relative to total words
        ambiguity_score = min(1.0, len(vague_terms) / word_count * 10)  # Scale by 10 for visibility
        return round(ambiguity_score, 3)
    
    def _find_implementation_gaps(self, content: str) -> List[Dict[str, Any]]:
        """Find implementation gaps and TODOs."""
        gaps = []
        for match in safe_finditer(SpecPatterns.IMPLEMENTATION_GAPS, content):
            gaps.append({
                "term": match.group(0),
                "line": MarkdownParser.get_line_number(content, match.start()),
                "context": self._get_context_around_match(content, match)
            })
        return gaps
    
    def _assess_clarity(self, content: str) -> Dict[str, Any]:
        """Assess overall specification clarity."""
        vague_count = len(safe_findall(SpecPatterns.VAGUE_TERMS, content))
        gap_count = len(safe_findall(SpecPatterns.IMPLEMENTATION_GAPS, content))
        requirement_count = (
            len(safe_findall(SpecPatterns.MUST, content)) +
            len(safe_findall(SpecPatterns.SHOULD, content))
        )
        
        # Simple clarity scoring
        clarity_score = 1.0
        if requirement_count > 0:
            clarity_score -= min(0.5, (vague_count / requirement_count) * 0.1)
            clarity_score -= min(0.3, (gap_count / requirement_count) * 0.1)
        
        return {
            "clarity_score": max(0.0, round(clarity_score, 3)),
            "vague_terms_count": vague_count,
            "implementation_gaps_count": gap_count,
            "formal_requirements_count": requirement_count
        }
    
    def _extract_requirements_by_type(self, content: str, pattern: re.Pattern) -> List[Dict[str, Any]]:
        """Extract requirements by requirement type pattern."""
        requirements = []
        for match in safe_finditer(pattern, content):
            line_num = MarkdownParser.get_line_number(content, match.start())
            context = self._get_context_around_match(content, match)
            
            requirements.append({
                "requirement": match.group(0),
                "line": line_num,
                "context": context,
                "priority": self._get_requirement_priority(pattern)
            })
        
        return requirements
    
    def _extract_acceptance_criteria(self, content: str) -> List[Dict[str, Any]]:
        """Extract acceptance criteria from the document."""
        criteria = []
        for match in safe_finditer(SpecPatterns.ACCEPTANCE_CRITERIA, content):
            criteria.append({
                "criterion": match.group(1),
                "line": MarkdownParser.get_line_number(content, match.start()),
                "completed": False  # All are unchecked boxes
            })
        
        return criteria
    
    def _extract_constraints_by_section(self, content: str, constraint_type: str) -> List[str]:
        """Extract constraints by type from constraint sections."""
        # This is a simplified implementation - would need more sophisticated parsing
        constraint_patterns = {
            "technical": re.compile(r'technical|performance|scalability|security', re.IGNORECASE),
            "business": re.compile(r'business|budget|timeline|legal|compliance', re.IGNORECASE),
            "resource": re.compile(r'resource|memory|cpu|storage|bandwidth', re.IGNORECASE)
        }
        
        pattern = constraint_patterns.get(constraint_type, re.compile(r'.*'))
        matches = safe_findall(pattern, content)
        return matches[:10]  # Limit results
    
    def _extract_spec_references(self, content: str) -> List[Dict[str, Any]]:
        """Extract specification references."""
        refs = []
        for match in safe_finditer(SpecPatterns.SPEC_REFERENCES, content):
            refs.append({
                "type": match.group(1),
                "id": match.group(2),
                "line": MarkdownParser.get_line_number(content, match.start()),
                "full_reference": match.group(0)
            })
        
        return refs
    
    def _extract_issue_references(self, content: str) -> List[Dict[str, Any]]:
        """Extract issue references."""
        refs = []
        for match in safe_finditer(SpecPatterns.ISSUE_REFERENCES, content):
            refs.append({
                "id": match.group(1),
                "line": MarkdownParser.get_line_number(content, match.start())
            })
        
        return refs
    
    def _extract_external_dependencies(self, content: str) -> List[str]:
        """Extract external dependencies mentioned in the document."""
        # Simplified pattern for external services/libraries
        external_pattern = re.compile(r'\b(API|service|library|framework|database)\s+[A-Z][a-zA-Z0-9]+', re.IGNORECASE)
        return safe_findall(external_pattern, content)[:10]  # Limit results
    
    def _extract_internal_dependencies(self, content: str) -> List[str]:
        """Extract internal dependencies within the project."""
        # Look for internal component references
        internal_pattern = re.compile(r'\b(component|module|service|endpoint)\s+[A-Z][a-zA-Z0-9]+', re.IGNORECASE)
        return safe_findall(internal_pattern, content)[:10]  # Limit results
    
    def _determine_spec_type(self, frontmatter: Dict, content: str) -> str:
        """Determine the type of specification document."""
        # Check frontmatter first
        if "type" in frontmatter:
            return frontmatter["type"]
        
        # Infer from content patterns
        if "Product Requirements" in content or "PRD" in content:
            return "PRD"
        elif "Technical Specification" in content or "Tech Spec" in content:
            return "Technical Specification"
        elif "Epic" in content and "Tasks" in content:
            return "Epic"
        elif "Acceptance Criteria" in content:
            return "User Story"
        else:
            return "Generic Specification"
    
    def _get_required_sections(self, spec_type: str) -> List[str]:
        """Get required sections for a specification type."""
        section_requirements = {
            "PRD": [
                "Overview", "Problem Statement", "Solution", "Requirements", 
                "User Stories", "Acceptance Criteria", "Success Metrics"
            ],
            "Technical Specification": [
                "Overview", "Architecture", "Implementation Details", "API Specification",
                "Data Models", "Testing Strategy", "Deployment"
            ],
            "Epic": [
                "Overview", "Scope", "Tasks", "Acceptance Criteria", "Definition of Done"
            ],
            "User Story": [
                "Description", "Acceptance Criteria", "Definition of Done"
            ],
            "Generic Specification": [
                "Overview", "Requirements", "Acceptance Criteria"
            ]
        }
        
        return section_requirements.get(spec_type, section_requirements["Generic Specification"])
    
    def _extract_sections(self, content: str) -> List[str]:
        """Extract section headers from the document."""
        headers = safe_findall(PATTERNS.HEADERS, content)
        return [header[1].strip() for header in headers]
    
    def _get_requirement_priority(self, pattern: re.Pattern) -> str:
        """Get priority level for requirement pattern."""
        if pattern == SpecPatterns.MUST or pattern == SpecPatterns.MUST_NOT:
            return "Critical"
        elif pattern == SpecPatterns.SHOULD or pattern == SpecPatterns.SHOULD_NOT:
            return "Important"
        elif pattern == SpecPatterns.MAY:
            return "Optional"
        else:
            return "Unknown"
    
    def _get_context_around_match(self, content: str, match: re.Match, context_chars: int = 100) -> str:
        """Get context around a regex match."""
        start = max(0, match.start() - context_chars)
        end = min(len(content), match.end() + context_chars)
        return content[start:end].strip()