#!/usr/bin/env python3
"""
Helper script to automatically update .mcp.json configuration files.

Adds or updates MCP server configurations while preserving existing settings.
Supports both Claude Code format and standard MCP client formats.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def load_mcp_config(config_path: Path) -> Dict[str, Any]:
    """Load existing MCP configuration or create new one."""
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        # Return empty config with standard structure
        return {"mcpServers": {}}


def save_mcp_config(config_path: Path, config: Dict[str, Any]) -> None:
    """Save MCP configuration with proper formatting."""
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"✅ Updated: {config_path}")


def add_server_config(
    config: Dict[str, Any],
    server_name: str,
    server_path: str,
    description: Optional[str] = None,
    env_vars: Optional[Dict[str, str]] = None,
    auto_restart: bool = False
) -> Dict[str, Any]:
    """
    Add or update a server configuration.

    Args:
        config: Existing MCP configuration
        server_name: Name of the MCP server
        server_path: Absolute path to the server.py file
        description: Optional server description
        env_vars: Optional environment variables
        auto_restart: Enable auto-restart with reloaderoo
    """
    # Ensure mcpServers key exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Build server configuration
    server_config = {
        "type": "stdio"  # MCP server type
    }

    # Add description if provided
    if description:
        server_config["description"] = description

    # Configure command and args
    if auto_restart:
        # Use reloaderoo for auto-restart
        server_config["command"] = "npx"
        server_config["args"] = [
            "reloaderoo",
            "proxy",
            "--",
            "uv",
            "run",
            "--script",
            server_path
        ]
        # Add auto-restart environment variable
        if env_vars is None:
            env_vars = {}
        env_vars["MCPDEV_PROXY_AUTO_RESTART"] = "true"
    else:
        # Standard uv run command
        server_config["command"] = "uv"
        server_config["args"] = [
            "run",
            "--script",
            server_path
        ]

    # Add environment variables if provided
    if env_vars:
        server_config["env"] = env_vars

    # Add/update server configuration
    config["mcpServers"][server_name] = server_config

    return config


def remove_server_config(config: Dict[str, Any], server_name: str) -> Dict[str, Any]:
    """Remove a server configuration."""
    if "mcpServers" in config and server_name in config["mcpServers"]:
        del config["mcpServers"][server_name]
        print(f"✅ Removed server: {server_name}")
    else:
        print(f"⚠️  Server not found: {server_name}")

    return config


def list_servers(config: Dict[str, Any]) -> None:
    """List all configured servers."""
    if "mcpServers" not in config or not config["mcpServers"]:
        print("No servers configured.")
        return

    print("\nConfigured MCP Servers:")
    print("-" * 60)
    for name, server_config in config["mcpServers"].items():
        desc = server_config.get("description", "No description")
        cmd = server_config.get("command", "")
        args = server_config.get("args", [])
        env = server_config.get("env", {})

        print(f"\n📦 {name}")
        print(f"   Description: {desc}")
        print(f"   Command: {cmd} {' '.join(args)}")
        if env:
            print(f"   Environment: {env}")


def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Update .mcp.json MCP server configurations"
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path.cwd() / ".mcp.json",
        help="Path to .mcp.json file (default: ./.mcp.json in current directory)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Add server command
    add_parser = subparsers.add_parser("add", help="Add or update a server")
    add_parser.add_argument("name", help="Server name")
    add_parser.add_argument("path", type=Path, help="Path to server.py file")
    add_parser.add_argument("--description", help="Server description")
    add_parser.add_argument(
        "--env",
        action="append",
        help="Environment variable (format: KEY=VALUE)"
    )
    add_parser.add_argument(
        "--auto-restart",
        action="store_true",
        help="Enable auto-restart with reloaderoo"
    )

    # Remove server command
    remove_parser = subparsers.add_parser("remove", help="Remove a server")
    remove_parser.add_argument("name", help="Server name to remove")

    # List servers command
    subparsers.add_parser("list", help="List all configured servers")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Load config
    config = load_mcp_config(args.config)

    # Execute command
    if args.command == "add":
        # Parse environment variables
        env_vars = {}
        if args.env:
            for env_str in args.env:
                key, value = env_str.split("=", 1)
                env_vars[key] = value

        # Add server
        config = add_server_config(
            config,
            server_name=args.name,
            server_path=str(args.path.resolve()),
            description=args.description,
            env_vars=env_vars if env_vars else None,
            auto_restart=args.auto_restart
        )

        # Save config
        save_mcp_config(args.config, config)

        print(f"\n✅ Added server '{args.name}' to {args.config}")
        if args.auto_restart:
            print("   🔄 Auto-restart enabled with reloaderoo")

    elif args.command == "remove":
        config = remove_server_config(config, args.name)
        save_mcp_config(args.config, config)

    elif args.command == "list":
        list_servers(config)

    return 0


if __name__ == "__main__":
    sys.exit(main())
