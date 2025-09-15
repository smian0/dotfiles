#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "ollama",
#     "python-dotenv",
# ]
# ///
"""
Claude Response Summarizer - Ultra Minimal

Generates concise summaries optimized for gpt-oss models.
"""

import json
import sys
import os
from pathlib import Path
from typing import Optional

try:
    import ollama
except ImportError:
    ollama = None

from dotenv import load_dotenv
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

def extract_response(transcript_path: str) -> Optional[str]:
    """Extract last assistant response"""
    try:
        with open(transcript_path, 'r') as f:
            messages = [json.loads(line) for line in f if line.strip()]
        
        for msg in reversed(messages):
            if msg.get('type') == 'assistant':
                content = msg.get('message', {}).get('content', '')
                if isinstance(content, list):
                    return ' '.join(item.get('text', '') for item in content if item.get('type') == 'text')
                return content
    except:
        pass
    return None

def summarize(response: str) -> str:
    """Generate summary"""
    if not ollama:
        return f"Response ({len(response.split())} words)"
    
    try:
        model = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:3305")
        
        # Generic single-line prompt for any content
        prompt = f"Summarize this in one concise sentence:\n\n{response}"
        
        # 20b needs more tokens than 120b
        tokens = 300 if "20b" in model else 150 if "gpt-oss" in model else 50
        
        result = ollama.Client(host=base_url).chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"num_predict": tokens, "temperature": 0.3}
        )
        
        if result and result.message:
            content = result.message.content or ''
            thinking = getattr(result.message, 'thinking', '') or ''
            
            # Handle gpt-oss thinking field - use content first, then thinking
            if content.strip():
                summary = content.strip()
            elif "gpt-oss" in model and thinking:
                lines = [line.strip() for line in thinking.split('\n') if line.strip()]
                summary = lines[-1] if lines else ""
            else:
                summary = ""
            
            # Clean up common prefixes and ensure single line
            for prefix in ["Summary:", "SUMMARY:", "Answer:", "ANSWER:"]:
                if summary.startswith(prefix):
                    summary = summary[len(prefix):].strip(' ":')
            
            # Ensure single line and reasonable length
            summary = summary.replace('\n', ' ').replace('\r', ' ')
            summary = ' '.join(summary.split())  # Remove extra whitespace
            if len(summary) > 120:
                summary = summary[:117] + "..."
            
            if len(summary) > 5:
                return summary
    except:
        pass
    
    # Generic fallback
    words = response.split()
    return f"Response provided ({len(words)} words)"

def main():
    try:
        data = json.load(sys.stdin)
        transcript_path = data.get('transcript_path')
        
        if not transcript_path:
            return
            
        response = extract_response(transcript_path)
        if not response or len(response.split()) < int(os.getenv("MIN_RESPONSE_WORDS", "3")):
            return
            
        summary = summarize(response)
        print(summary)
        
        # Write to statusline temp file
        try:
            import time
            project_id = os.path.basename(os.getcwd()).replace('/', '-').replace(' ', '_')
            summary_file = Path(f"/tmp/claude-{project_id}-last-summary.txt")
            timestamp = int(time.time())
            summary_file.write_text(f"{timestamp}:{summary}")
        except:
            pass
        
    except:
        pass  # Never disrupt Claude

if __name__ == "__main__":
    main()