#!/bin/bash
# Setup context-based directories for separate Claude sessions

PROJECT_ROOT="${1:-$PWD}"
CONTEXTS_DIR="$PROJECT_ROOT/.contexts"

echo "🔧 Setting up Claude Code context directories"
echo "================================================"
echo ""
echo "Project: $PROJECT_ROOT"
echo "Contexts: $CONTEXTS_DIR"
echo ""

# Create contexts directory
mkdir -p "$CONTEXTS_DIR"

# Create individual context directories
contexts=("api" "web" "docs" "testing" "debugging" "research")

for ctx in "${contexts[@]}"; do
    ctx_dir="$CONTEXTS_DIR/$ctx"
    mkdir -p "$ctx_dir"

    # Create symlinks to parent project files (optional)
    # This makes files accessible but each context has separate Claude session
    # Comment out if you don't want symlinks
    # ln -sf "$PROJECT_ROOT"/* "$ctx_dir/" 2>/dev/null || true

    # Create a marker file
    echo "# Context: $ctx" > "$ctx_dir/CONTEXT.md"
    echo "Working directory for $ctx-related Claude Code sessions" >> "$ctx_dir/CONTEXT.md"

    echo "✅ Created: $ctx_dir"
done

# Create tmuxinator config
TMUXINATOR_CONFIG="$HOME/.config/tmuxinator/$(basename "$PROJECT_ROOT")-contexts.yml"
mkdir -p "$(dirname "$TMUXINATOR_CONFIG")"

cat > "$TMUXINATOR_CONFIG" << EOF
# tmuxinator config for $(basename "$PROJECT_ROOT")
name: $(basename "$PROJECT_ROOT")-contexts
root: $PROJECT_ROOT

windows:
  - api:
      root: $CONTEXTS_DIR/api
      panes:
        - claude
  - web:
      root: $CONTEXTS_DIR/web
      panes:
        - claude
  - docs:
      root: $CONTEXTS_DIR/docs
      panes:
        - claude
  - testing:
      root: $CONTEXTS_DIR/testing
      panes:
        - claude
EOF

echo ""
echo "✅ tmuxinator config created: $TMUXINATOR_CONFIG"
echo ""
echo "📖 Usage:"
echo "  tmuxinator start $(basename "$PROJECT_ROOT")-contexts"
echo ""
echo "Each window will have a separate Claude Code session!"
