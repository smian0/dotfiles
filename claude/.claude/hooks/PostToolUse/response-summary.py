#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai",
#     "python-dotenv",
# ]
# ///
"""
Claude Response Summarizer with Log Rotation

Provides concise summaries of Claude's responses without polluting Claude's context.
Uses efficient log rotation to prevent unbounded log growth.

Environment Variables:
    OLLAMA_MODEL: Model to use for summaries (default: gpt-oss:20b)
    SUMMARY_MODE: Output mode - minimal/inline/panel (default: minimal)
    DEBUG_HOOK: Enable debug output (set to 1)
"""

import json
import sys
import os
from pathlib import Path
from typing import Optional

# Import LogRotator from log-rotator.py using importlib
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location('log_rotator', str(Path.home() / '.claude' / 'scripts' / 'log-rotator.py'))
    log_rotator_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(log_rotator_module)
    LogRotator = log_rotator_module.LogRotator
except Exception:
    # Fallback if log rotator not available
    LogRotator = None


def extract_last_response(transcript_path: str) -> Optional[str]:
    """Extract Claude's latest response from transcript"""
    if not Path(transcript_path).exists():
        return None
    
    import time
    # Try multiple times with small delays (transcript may still be writing)
    for attempt in range(3):
        messages = []
        try:
            with open(transcript_path, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            messages.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except Exception:
            if attempt < 2:  # Don't sleep on last attempt
                time.sleep(0.1)
            continue
        
        # If we found messages, break out of retry loop
        if messages:
            break
        
        if attempt < 2:  # Don't sleep on last attempt
            time.sleep(0.1)
    
    # Find last assistant message
    for msg in reversed(messages):
        if msg.get('role') == 'assistant':
            content = msg.get('message', {}).get('content', '')
            if isinstance(content, list):
                text_parts = [
                    item.get('text', '') 
                    for item in content 
                    if item.get('type') == 'text'
                ]
                response = ' '.join(text_parts)
            else:
                response = content
            
            # Clean up response - remove tool calls and system reminders
            if response:
                lines = response.split('\n')
                cleaned_lines = []
                skip_until_end = False
                
                for line in lines:
                    if '<system-reminder>' in line:
                        skip_until_end = True
                        continue
                    elif '</system-reminder>' in line:
                        skip_until_end = False
                        continue
                    elif skip_until_end:
                        continue
                    elif line.strip().startswith('<function_calls>'):
                        skip_until_end = True
                        continue
                    elif line.strip().startswith('</function_results>'):
                        skip_until_end = False
                        continue
                    elif not skip_until_end and line.strip():
                        cleaned_lines.append(line)
                
                return '\n'.join(cleaned_lines).strip()
    return None


def should_summarize(response: str) -> bool:
    """Determine if response warrants summarization"""
    if not response:
        return False
    
    # Only summarize substantial responses
    word_count = len(response.split())
    return word_count > 100  # Skip short responses


def generate_ollama_summary(response: str) -> Optional[str]:
    """Try to generate summary using Ollama"""
    try:
        from openai import OpenAI
        
        client = OpenAI(
            base_url='http://localhost:11434/v1',
            api_key='ollama',
        )
        model = os.getenv("OLLAMA_MODEL", "gemma3:latest")
        
        # Truncate very long responses
        if len(response) > 3000:
            response = response[:3000] + "..."
        
        prompt = f"""Summarize this AI assistant response in ONE concise sentence (max 15 words).
Focus on the main action or key information provided.
Do not include meta-commentary or formatting.

Response to summarize:
{response}

Summary:"""
        
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.3,
            timeout=5
        )
        
        summary = completion.choices[0].message.content.strip()
        # Clean up common prefixes
        for prefix in ["Summary:", "In summary:", "The response"]:
            if summary.startswith(prefix):
                summary = summary[len(prefix):].strip()
        
        return summary
        
    except Exception:
        return None  # Fall back on any error


def generate_fallback_summary(response: str) -> str:
    """Generate rule-based summary when Ollama is unavailable"""
    words = response.split()
    
    # Look for action words
    action_words = ['implement', 'create', 'build', 'explain', 'analyze', 'design', 
                   'develop', 'configure', 'install', 'setup', 'fix', 'update',
                   'add', 'remove', 'modify', 'test', 'deploy', 'run', 'write']
    
    found_action = None
    action_context = ""
    
    for i, word in enumerate(words[:50]):
        clean_word = word.lower().rstrip('.,!?:;')
        if clean_word in action_words:
            found_action = clean_word
            # Get some context after the action
            if i + 1 < len(words):
                next_words = words[i+1:i+6]  # Get next 5 words
                action_context = ' '.join(next_words)
            break
    
    if found_action:
        if action_context:
            # Clean up context
            action_context = action_context.strip('.,!?:;')[:50]
            if action_context:
                return f"Helped {found_action} {action_context}"
        return f"Provided guidance on {found_action}ing"
    
    # Look for question words that might indicate explanation
    if any(word in response.lower()[:200] for word in ['how to', 'what is', 'why', 'explain']):
        return f"Explained concepts ({len(words)} words)"
    
    # Fallback to word count and type
    word_count = len(words)
    if word_count > 300:
        return f"Comprehensive response ({word_count} words)"
    elif word_count > 150:
        return f"Detailed response ({word_count} words)"
    else:
        return f"Response provided ({word_count} words)"


def format_output(summary: str, mode: str = "minimal") -> None:
    """Output summary in simple format"""
    print(f"Short Summary: {summary}", file=sys.stdout)


def main():
    stdin_data = None
    try:
        # Read hook data from stdin
        stdin_data = json.load(sys.stdin)
        transcript_path = stdin_data.get('transcript_path')
        
        if not transcript_path:
            return
        
        # Initialize log rotator
        if LogRotator:
            hooks_log_dir = Path.home() / ".claude" / "hooks" / "PostToolUse" / "logs"
            hooks_log_dir.mkdir(exist_ok=True)
            log_rotator = LogRotator(
                log_path=str(hooks_log_dir / "response-summary.jsonl"),
                format="jsonl",
                max_size_mb=5.0,
                max_entries=1000,
                max_archives=3,
                compress=True
            )
            # Log hook invocation
            log_rotator.append({
                "status": "started",
                "transcript_path": transcript_path,
                "session_id": stdin_data.get('session_id'),
                "tool_name": stdin_data.get('tool_name'),
                "cwd": os.getcwd()
            })
        
        # Extract response
        response = extract_last_response(transcript_path)
        
        if not response:
            if LogRotator:
                log_rotator.append({"status": "no_response_found"})
            return
        
        if not should_summarize(response):
            if LogRotator:
                log_rotator.append({
                    "status": "response_too_short", 
                    "word_count": len(response.split())
                })
            return
        
        # Generate summary
        summary = generate_ollama_summary(response)
        summary_method = "ollama" if summary else "fallback"
        
        if not summary:
            summary = generate_fallback_summary(response)
        
        # Log successful summary
        if LogRotator:
            log_rotator.append({
                "status": "summary_generated",
                "summary": summary,
                "summary_method": summary_method,
                "response_length": len(response),
                "word_count": len(response.split())
            })
        
        # Output to stderr (user sees, Claude doesn't)
        output_mode = os.getenv("SUMMARY_MODE", "minimal")
        format_output(summary, output_mode)
        
        # Write summary to project-specific temp file for statusline integration
        try:
            import time
            project_id = os.path.basename(os.getcwd()).replace('/', '-').replace(' ', '_')
            summary_file = Path(f"/tmp/claude-{project_id}-last-summary.txt")
            timestamp = int(time.time())
            with summary_file.open("w") as f:
                f.write(f"{timestamp}:{summary}")
        except Exception:
            pass  # Don't fail if we can't write summary file
        
    except Exception as e:
        # Log any errors
        if LogRotator and stdin_data:
            try:
                log_rotator.append({
                    "status": "error", 
                    "error": str(e)
                })
            except:
                pass
        
        if os.getenv("DEBUG_HOOK"):
            print(f"DEBUG: Hook error: {e}", file=sys.stderr)
        pass  # Never disrupt Claude


if __name__ == "__main__":
    main()