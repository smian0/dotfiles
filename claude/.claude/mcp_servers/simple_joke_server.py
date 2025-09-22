#!/usr/bin/env python3
"""
Simple MCP joke server without external dependencies
"""

import json
import sys
import random

# Predefined jokes to avoid external AI dependencies
JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
    "Why do Python programmers prefer snakes? Because they're already used to dealing with bugs!",
    "What's a programmer's favorite hangout place? The Foo Bar.",
    "Why did the programmer quit his job? He didn't get arrays! (get a raise)",
    "What do you call a programmer from Finland? Nerdic!",
    "Why don't programmers like nature? It has too many bugs.",
    "What's the object-oriented way to become wealthy? Inheritance.",
]

class SimpleMCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "tell_joke",
                "description": "Tell a programming joke",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Request for joke type"
                        }
                    },
                    "required": ["prompt"]
                }
            },
            {
                "name": "restart_server",
                "description": "Restart the MCP server (added by reloaderoo)",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    def handle_request(self, request):
        method = request.get("method")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "simple-joke-server",
                        "version": "1.0.0"
                    }
                }
            }

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "tools": self.tools
                }
            }

        elif method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if tool_name == "tell_joke":
                joke = random.choice(JOKES)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": f"🔥 Round 2 test: {joke}"
                            }
                        ]
                    }
                }

        # Default response for unhandled methods
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }

    def run(self):
        """Run the MCP server using stdio transport"""
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = self.handle_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    server = SimpleMCPServer()
    server.run()
