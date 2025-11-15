# Obsidian Features Reference

Advanced Obsidian vault processing capabilities.

## Wiki Links

### Basic Wiki Links
```python
find_wiki_links("note.md")
```

**Finds**: `[[Internal Link]]` and `[[Link|Alias]]`

**Returns**:
```json
{
  "file": "note.md",
  "wiki_links": [
    {"target": "Internal Link", "alias": null, "line": 5},
    {"target": "Link", "alias": "Alias", "line": 10}
  ],
  "count": 2
}
```

### Filter by Target
```python
find_wiki_links("note.md", target_link="Specific Page")
```

Returns only links to a specific page.

## Embedded Content

Transclusion using `![[]]` syntax:

```python
find_embedded_content("note.md")                  # All embeds
find_embedded_content("note.md", content_type="image")  # Images only
```

**Content types**: `"image"`, `"note"`, or `None` (all)

**Returns**: Embedded file paths and types.

## Block References

### Block IDs
```python
find_block_references("note.md")
```

**Finds**:
- Block definitions: `^block-id`
- Block links: `[[note#^block-id]]`

**Returns**:
```json
{
  "file": "note.md",
  "block_ids": [
    {"id": "block-id", "line": 15, "content": "..."}
  ],
  "block_links": [
    {"source": "note", "block_id": "block-id", "line": 20}
  ]
}
```

### Header Links
Automatic via wiki link parsing - links to headers within notes.

## Callouts (Admonitions)

```python
find_callouts("note.md")                      # All callouts
find_callouts("note.md", callout_type="warning")  # Specific type
```

**Syntax**: `> [!note]`, `> [!warning]`, `> [!tip]`, etc.

**Returns**:
```json
{
  "callouts": [
    {"type": "note", "content": "...", "line": 5}
  ],
  "count": 1
}
```

## Dataview Fields

Inline metadata fields:

```python
extract_dataview_fields("note.md")              # All fields
extract_dataview_fields("note.md", "status")    # Specific field
```

**Syntax**: `field:: value`

**Example**:
```markdown
status:: active
priority:: high
```

**Returns**:
```json
{
  "fields": [
    {"name": "status", "value": "active", "line": 3},
    {"name": "priority", "value": "high", "line": 4}
  ]
}
```

## Comprehensive Link Parsing

Get all Obsidian link types in one call:

```python
parse_obsidian_links("note.md")
```

**Returns**:
- Wiki links (with aliases)
- Embedded content
- Block references
- Header links
- Complete link graph

## Vault Graph Analysis

Build connection graph across entire vault:

```python
build_vault_graph("/path/to/vault")
```

**Returns**:
```json
{
  "nodes": [
    {"id": "note1.md", "title": "Note 1", "outgoing": 3, "incoming": 2}
  ],
  "edges": [
    {"source": "note1.md", "target": "note2.md", "type": "wiki_link"}
  ],
  "stats": {
    "total_notes": 100,
    "total_connections": 250,
    "orphaned_notes": 5
  }
}
```

## Cross-Reference Search

Find all references to a term across vault:

```python
find_cross_references("/path/to/vault", "important-concept")
```

**Searches**:
- Wiki links
- Plain text mentions
- Header references
- Tag references

**Returns**: Files, line numbers, and context for each reference.

## Use Cases

**Vault cleanup**: Find orphaned notes with zero connections
**Knowledge mapping**: Visualize note relationships
**Link validation**: Check for broken wiki links
**Content migration**: Extract all embeds for reorganization
**Dataview queries**: Extract structured metadata fields

