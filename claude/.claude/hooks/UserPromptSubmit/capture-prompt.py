#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def ensure_directories():
    """Ensure required directories exist."""
    sessions_dir = Path.home() / ".claude" / "data" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    
    logs_dir = Path.home() / ".claude" / "hooks" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    return sessions_dir, logs_dir


def log_prompt_capture(session_id, prompt, success=True, error=None):
    """Log prompt capture events."""
    try:
        _, logs_dir = ensure_directories()
        log_file = logs_dir / "prompt_capture.jsonl"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "prompt_length": len(prompt),
            "success": success,
        }
        
        if error:
            log_entry["error"] = str(error)
        
        # Append to log file
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
            
    except Exception:
        # Never fail if logging fails
        pass


def manage_session_data(session_id, prompt):
    """Store prompt in session data for statusline access."""
    try:
        sessions_dir, _ = ensure_directories()
        session_file = sessions_dir / f"{session_id}.json"
        
        # Load existing session data or create new
        if session_file.exists():
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                session_data = {
                    "session_id": session_id,
                    "prompts": [],
                    "created_at": datetime.now().isoformat()
                }
        else:
            session_data = {
                "session_id": session_id,
                "prompts": [],
                "created_at": datetime.now().isoformat()
            }
        
        # Add the new prompt with timestamp
        prompt_entry = {
            "text": prompt,
            "timestamp": datetime.now().isoformat()
        }
        
        # Keep only last 10 prompts to prevent file bloat
        session_data["prompts"].append(prompt_entry)
        if len(session_data["prompts"]) > 10:
            session_data["prompts"] = session_data["prompts"][-10:]
        
        session_data["updated_at"] = datetime.now().isoformat()
        
        # Write session data
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Also write current prompt to project-specific quick access file for statusline
        import os
        project_id = os.path.basename(os.getcwd()).replace('/', '-').replace(' ', '_')
        current_prompt_file = Path(f"/tmp/claude-{project_id}-current-prompt.txt")
        with open(current_prompt_file, 'w') as f:
            f.write(f"{prompt}")
            
        log_prompt_capture(session_id, prompt, success=True)
        
    except Exception as e:
        log_prompt_capture(session_id, prompt, success=False, error=e)


def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Extract session_id and prompt
        session_id = input_data.get('session_id', 'unknown')
        prompt = input_data.get('prompt', '')
        
        # Skip empty prompts
        if not prompt.strip():
            sys.exit(0)
        
        # Store prompt for statusline access
        manage_session_data(session_id, prompt)
        
        # Success - allow prompt to continue
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully - never block prompts
        sys.exit(0)


if __name__ == '__main__':
    main()