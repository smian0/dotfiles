#!/usr/bin/env python3
"""
⚠️  DEPRECATED: This script is being superseded by Claude CLI-based MCP extraction.

For new installations, use the Claude CLI approach via:
- zsh/mcp-config.zsh functions (mcpg, mcpls, etc.)
- Direct Claude CLI commands (claude mcp list, claude mcp get)

This script is maintained for backward compatibility only.

Extract MCP server configurations from Claude Code's global configuration
and generate a well-formed mcp.json file.

This script reads ~/.claude.json and extracts:
1. Global MCP servers (from root level)
2. Project-specific MCP servers (optionally)
3. Merges them into a standard mcp.json format

Usage:
    python extract-mcp-config.py [options]
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Set


def load_claude_config(claude_json_path: Path) -> Dict[str, Any]:
    """Load and parse the Claude configuration file."""
    try:
        with open(claude_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Claude config file not found at {claude_json_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in Claude config file: {e}")
        sys.exit(1)


def extract_global_mcp_servers(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract global MCP servers from the root level of config."""
    return config.get('mcpServers', {})


def extract_project_mcp_servers(config: Dict[str, Any], project_filter: str = None) -> Dict[str, Any]:
    """Extract MCP servers from all projects or a specific project."""
    projects = config.get('projects', {})
    all_servers = {}
    
    for project_path, project_config in projects.items():
        # Filter by project if specified
        if project_filter and project_filter not in project_path:
            continue
            
        project_servers = project_config.get('mcpServers', {})
        if project_servers:
            # Add project context to server names to avoid conflicts
            project_name = Path(project_path).name
            for server_name, server_config in project_servers.items():
                # Create unique name with project prefix
                unique_name = f"{project_name}_{server_name}"
                all_servers[unique_name] = server_config
                
    return all_servers


def merge_mcp_configs(global_servers: Dict[str, Any], 
                     project_servers: Dict[str, Any],
                     prefer_global: bool = True) -> Dict[str, Any]:
    """Merge global and project MCP server configurations."""
    merged = {}
    
    if prefer_global:
        # Add project servers first, then global (global overwrites)
        merged.update(project_servers)
        merged.update(global_servers)
    else:
        # Add global servers first, then project (project overwrites)
        merged.update(global_servers)
        merged.update(project_servers)
        
    return merged


def generate_mcp_json(mcp_servers: Dict[str, Any], 
                     include_env_section: bool = True) -> Dict[str, Any]:
    """Generate a well-formed mcp.json structure."""
    mcp_config = {
        "mcpServers": mcp_servers
    }
    
    # Add environment section if requested
    if include_env_section:
        # Extract unique environment variables from all servers
        env_vars = set()
        for server_config in mcp_servers.values():
            if 'env' in server_config:
                env_vars.update(server_config['env'].keys())
        
        if env_vars:
            mcp_config["env"] = {var: f"${var}" for var in sorted(env_vars)}
    
    return mcp_config


def list_available_servers(config: Dict[str, Any]) -> None:
    """List all available MCP servers in the configuration."""
    print("Available MCP servers in Claude configuration:")
    print("=" * 50)
    
    # Global servers
    global_servers = extract_global_mcp_servers(config)
    if global_servers:
        print("\nGlobal servers:")
        for name, server_config in global_servers.items():
            command = server_config.get('command', 'N/A')
            server_type = server_config.get('type', 'stdio')
            print(f"  • {name} ({server_type}) - {command}")
    
    # Project servers
    projects = config.get('projects', {})
    project_servers_found = False
    
    for project_path, project_config in projects.items():
        project_servers = project_config.get('mcpServers', {})
        if project_servers:
            if not project_servers_found:
                print("\nProject-specific servers:")
                project_servers_found = True
                
            project_name = Path(project_path).name
            print(f"\n  Project: {project_name}")
            for name, server_config in project_servers.items():
                command = server_config.get('command', 'N/A')
                server_type = server_config.get('type', 'stdio')
                print(f"    • {name} ({server_type}) - {command}")
    
    if not global_servers and not project_servers_found:
        print("  No MCP servers found in configuration.")


def main():
    parser = argparse.ArgumentParser(
        description="Extract MCP server configurations from Claude Code config",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract global servers only
  python extract-mcp-config.py --global-only
  
  # Extract all servers and save to custom file
  python extract-mcp-config.py -o custom-mcp.json
  
  # List available servers without extraction
  python extract-mcp-config.py --list-only
  
  # Extract servers from specific project
  python extract-mcp-config.py --project vectorbt
        """
    )
    
    parser.add_argument(
        '--claude-config', '-c',
        type=Path,
        default=Path.home() / '.claude.json',
        help='Path to Claude configuration file (default: ~/.claude.json)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('.cursor/mcp.json'),
        help='Output path for mcp.json file (default: .cursor/mcp.json)'
    )
    
    parser.add_argument(
        '--global-only',
        action='store_true',
        help='Extract only global MCP servers'
    )
    
    parser.add_argument(
        '--project', '-p',
        type=str,
        help='Extract servers from specific project (filter by project path)'
    )
    
    parser.add_argument(
        '--prefer-project',
        action='store_true',
        help='When merging, let project servers override global ones'
    )
    
    parser.add_argument(
        '--no-env',
        action='store_true',
        help='Do not include env section in output'
    )
    
    parser.add_argument(
        '--list-only',
        action='store_true',
        help='Just list available servers without extracting'
    )
    
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be extracted without writing file'
    )
    
    args = parser.parse_args()
    
    # Load Claude configuration
    config = load_claude_config(args.claude_config)
    
    # List servers if requested
    if args.list_only:
        list_available_servers(config)
        return
    
    # Extract servers based on options
    if args.global_only:
        mcp_servers = extract_global_mcp_servers(config)
        print("Extracting global MCP servers only...")
    elif args.project:
        mcp_servers = extract_project_mcp_servers(config, args.project)
        print(f"Extracting MCP servers from projects matching '{args.project}'...")
    else:
        # Extract both global and project servers
        global_servers = extract_global_mcp_servers(config)
        project_servers = extract_project_mcp_servers(config)
        mcp_servers = merge_mcp_configs(
            global_servers, 
            project_servers, 
            prefer_global=not args.prefer_project
        )
        print("Extracting global and project MCP servers...")
    
    if not mcp_servers:
        print("No MCP servers found to extract.")
        return
    
    # Generate mcp.json structure
    mcp_config = generate_mcp_json(
        mcp_servers, 
        include_env_section=not args.no_env
    )
    
    # Show what would be extracted
    print(f"\nFound {len(mcp_servers)} MCP servers:")
    for name in mcp_servers.keys():
        print(f"  • {name}")
    
    # Format JSON output
    json_output = json.dumps(
        mcp_config, 
        indent=2 if args.pretty else None,
        sort_keys=True
    )
    
    if args.dry_run:
        print(f"\nWould write to {args.output}:")
        print("-" * 50)
        print(json_output)
        return
    
    # Create output directory if needed
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    # Write mcp.json file
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"\n✓ MCP configuration extracted to: {args.output}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
