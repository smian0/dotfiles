"""
Obsidian-specific markdown processing features.

This module provides all Obsidian-aware operations including wiki-links,
embedded content, block references, callouts, dataview fields, and vault analysis.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

try:
    from .core import PATTERNS, MarkdownParser, MarkdownError
except ImportError:
    from core import PATTERNS, MarkdownParser, MarkdownError


class ObsidianEngine:
    """Engine for Obsidian-specific markdown operations."""
    
    def find_wiki_links(self, file_path: str, target_link: str = None) -> Dict[str, Any]:
        """Find wiki-style [[internal links]] with Obsidian alias support."""
        try:
            content = MarkdownParser.read_file(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        
        links = []
        
        for m in PATTERNS.WIKI_LINKS.finditer(content):
            target = m.group(1)
            alias = m.group(2) if m.group(2) else target
            
            # Check if matches target filter (search both target and alias)
            if not target_link or (target_link.lower() in target.lower() or target_link.lower() in alias.lower()):
                links.append({
                    "target": target,
                    "alias": alias,
                    "display_text": alias,
                    "has_alias": bool(m.group(2)),
                    "line": MarkdownParser.get_line_number(content, m.start()),
                    "match": m.group(0)
                })
        
        return {
            "file": file_path,
            "wiki_links": links,
            "count": len(links),
            "aliases_count": sum(1 for link in links if link["has_alias"])
        }
    
    def find_embedded_content(self, file_path: str, content_type: str = None) -> Dict[str, Any]:
        """Find embedded content using ![[]] syntax (Obsidian transclusion)."""
        try:
            content = MarkdownParser.read_file(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        
        embeds = []
        
        for m in PATTERNS.EMBEDDED.finditer(content):
            embed_path = m.group(1)
            embed_type = "image" if MarkdownParser.is_image_path(embed_path) else "note"
            
            if not content_type or content_type == embed_type:
                embeds.append({
                    "path": embed_path,
                    "type": embed_type,
                    "line": MarkdownParser.get_line_number(content, m.start()),
                    "match": m.group(0)
                })
        
        return {
            "file": file_path,
            "embedded_content": embeds,
            "count": len(embeds),
            "types": list(set(e["type"] for e in embeds))
        }
    
    def find_block_references(self, file_path: str) -> Dict[str, Any]:
        """Find block IDs (^block-id) and block links ([[note#^block]])."""
        try:
            content = MarkdownParser.read_file(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        
        block_ids = []
        block_links = []
        
        # Find block IDs in the current file
        for m in PATTERNS.BLOCK_REF.finditer(content):
            block_ids.append({
                "block_id": m.group(1),
                "line": MarkdownParser.get_line_number(content, m.start()),
                "match": m.group(0)
            })
        
        # Find block links referencing other files
        for m in PATTERNS.BLOCK_LINK.finditer(content):
            block_links.append({
                "target_file": m.group(1),
                "block_id": m.group(2),
                "line": MarkdownParser.get_line_number(content, m.start()),
                "match": m.group(0)
            })
        
        return {
            "file": file_path,
            "block_ids": block_ids,
            "block_links": block_links,
            "block_id_count": len(block_ids),
            "block_link_count": len(block_links)
        }
    
    def find_callouts(self, file_path: str, callout_type: str = None) -> Dict[str, Any]:
        """Find callout/admonition blocks using > [!type] syntax."""
        try:
            content = MarkdownParser.read_file(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        
        callouts = []
        
        for m in PATTERNS.CALLOUTS.finditer(content):
            c_type = m.group(1)
            c_content = m.group(2).strip()
            
            if not callout_type or callout_type.lower() == c_type.lower():
                callouts.append({
                    "type": c_type,
                    "content": c_content,
                    "line": MarkdownParser.get_line_number(content, m.start()),
                    "match": m.group(0)
                })
        
        return {
            "file": file_path,
            "callouts": callouts,
            "count": len(callouts),
            "types": list(set(c["type"] for c in callouts))
        }
    
    def parse_obsidian_links(self, file_path: str) -> Dict[str, Any]:
        """Comprehensive Obsidian link parser for all link types."""
        try:
            content = MarkdownParser.read_file(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        
        results = {
            "wiki_links": [],
            "header_links": [],
            "block_links": [],
            "embedded_content": [],
            "external_links": []
        }
        
        # Parse wiki links with optional aliases
        for m in PATTERNS.WIKI_LINKS.finditer(content):
            link = {
                "target": m.group(1),
                "alias": m.group(2) if m.group(2) else m.group(1),
                "line": MarkdownParser.get_line_number(content, m.start()),
                "match": m.group(0)
            }
            results["wiki_links"].append(link)
        
        # Parse header links
        for m in PATTERNS.HEADER_LINK.finditer(content):
            # Exclude block links (those with ^)
            if '#^' not in m.group(0):
                link = {
                    "target_file": m.group(1),
                    "header": m.group(2),
                    "line": MarkdownParser.get_line_number(content, m.start()),
                    "match": m.group(0)
                }
                results["header_links"].append(link)
        
        # Parse block links
        for m in PATTERNS.BLOCK_LINK.finditer(content):
            link = {
                "target_file": m.group(1),
                "block_id": m.group(2),
                "line": MarkdownParser.get_line_number(content, m.start()),
                "match": m.group(0)
            }
            results["block_links"].append(link)
        
        # Parse embedded content
        for m in PATTERNS.EMBEDDED.finditer(content):
            embed = {
                "path": m.group(1),
                "type": "image" if MarkdownParser.is_image_path(m.group(1)) else "note",
                "line": MarkdownParser.get_line_number(content, m.start()),
                "match": m.group(0)
            }
            results["embedded_content"].append(embed)
        
        # Parse external links
        for m in PATTERNS.EXTERNAL_LINKS.finditer(content):
            link = {
                "text": m.group(1),
                "url": m.group(2),
                "line": MarkdownParser.get_line_number(content, m.start()),
                "match": m.group(0)
            }
            results["external_links"].append(link)
        
        # Add counts (create new dict to avoid iteration issues)
        counts = {}
        for key in results:
            counts[f"{key}_count"] = len(results[key])
        
        results.update(counts)
        results["file"] = file_path
        results["total_links"] = sum(len(v) for k, v in results.items() if isinstance(v, list) and not k.endswith('_count'))
        
        return results
    
    def extract_dataview_fields(self, file_path: str, field_name: str = None) -> Dict[str, Any]:
        """Extract Dataview inline fields (field:: value)."""
        try:
            content = MarkdownParser.read_file(file_path)
        except FileNotFoundError:
            return {"error": f"File not found: {file_path}"}
        
        fields = []
        
        for m in PATTERNS.DATAVIEW_FIELDS.finditer(content):
            f_name = m.group(1)
            f_value = m.group(2)
            
            if not field_name or field_name.lower() == f_name.lower():
                fields.append({
                    "field": f_name,
                    "value": f_value,
                    "line": MarkdownParser.get_line_number(content, m.start()),
                    "match": m.group(0)
                })
        
        return {
            "file": file_path,
            "dataview_fields": fields,
            "count": len(fields),
            "field_names": list(set(f["field"] for f in fields))
        }
    
    def build_vault_graph(self, search_path: str) -> Dict[str, Any]:
        """Build a graph structure of vault connections."""
        path = Path(search_path)
        files = [path] if path.is_file() else list(path.rglob("*.md"))
        
        nodes = []
        edges = []
        
        for file in files:
            try:
                content = file.read_text(encoding='utf-8')
                file_name = file.stem
                
                # Create node
                node = {
                    "id": file_name,
                    "path": str(file),
                    "title": file_name,
                    "links_out": 0,
                    "links_in": 0
                }
                
                # Count outgoing links
                outgoing_targets = set()
                for m in PATTERNS.WIKI_LINKS.finditer(content):
                    target = m.group(1).split('|')[0]  # Remove alias part
                    if target != file_name:  # Avoid self-links
                        outgoing_targets.add(target)
                        edges.append({
                            "source": file_name,
                            "target": target,
                            "type": "wiki_link"
                        })
                
                node["links_out"] = len(outgoing_targets)
                nodes.append(node)
                
            except Exception:
                continue
        
        # Calculate incoming links
        node_map = {node["id"]: node for node in nodes}
        for edge in edges:
            if edge["target"] in node_map:
                node_map[edge["target"]]["links_in"] += 1
        
        return {
            "vault_path": str(path),
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "avg_connections": len(edges) / len(nodes) if nodes else 0
            }
        }
    
    def find_cross_references(self, search_path: str, term: str) -> Dict[str, Any]:
        """Find cross-references to a term across markdown files."""
        path = Path(search_path)
        files = [path] if path.is_file() else list(path.rglob("*.md"))
        references = []
        
        for file in files:
            try:
                content = file.read_text(encoding='utf-8')
                contexts = []
                
                # Headers, wiki links, text
                for pattern, ref_type in [
                    (rf'#{1,6}\s+.*{re.escape(term)}.*', "header"),
                    (rf'\[\[.*{re.escape(term)}.*\]\]', "wiki_link"),
                    (rf'\b{re.escape(term)}\b', "text")
                ]:
                    for m in re.finditer(pattern, content, re.IGNORECASE):
                        line_num = MarkdownParser.get_line_number(content, m.start())
                        line_text = content.split('\n')[line_num - 1] if ref_type == "text" else m.group(0)
                        contexts.append({"type": ref_type, "line": line_num, "text": line_text.strip()})
                
                if contexts:
                    references.append({"file": str(file), "references": contexts})
            except:
                continue
        
        return {
            "term": term,
            "files_searched": len(files),
            "files_with_matches": len(references),
            "cross_references": references
        }