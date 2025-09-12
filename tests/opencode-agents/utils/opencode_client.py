"""OpenCode client for agent invocation"""
import subprocess
import logging
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
import re

logger = logging.getLogger(__name__)

@dataclass
class AgentResponse:
    """Response from an OpenCode agent"""
    content: str
    sources: Optional[List[str]] = None
    metadata: Optional[dict] = None
    raw_output: Optional[str] = None

class OpenCodeClient:
    """Client for invoking OpenCode agents"""
    
    def __init__(self, oc_binary: Path = None, timeout: int = 120):
        # Use the existing oc binary from the project
        # From utils/ we need to go: utils -> opencode-agents -> tests -> project-root
        self.oc_binary = oc_binary or Path(__file__).parent.parent.parent.parent / "bin" / "oc"
        self.timeout = timeout
        
        # Verify the binary exists
        if not self.oc_binary.exists():
            raise FileNotFoundError(f"OpenCode binary not found at {self.oc_binary}")
        
        logger.info(f"Using OpenCode binary: {self.oc_binary}")
    
    def get_agent(self, agent_name: str):
        """Get agent interface for testing"""
        return AgentInterface(self, agent_name)
    
    def invoke_agent(self, agent_name: str, query: str) -> AgentResponse:
        """Invoke OpenCode agent and parse response"""
        cmd = [str(self.oc_binary), "run", "--agent", agent_name, query]
        project_root = self.oc_binary.parent.parent
        
        logger.info(f"Invoking: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=project_root  # Run from project root
            )
            
            if result.returncode != 0:
                logger.error(f"OpenCode agent failed: {result.stderr}")
                raise RuntimeError(f"OpenCode agent '{agent_name}' failed: {result.stderr}")
            
            raw_output = result.stdout.strip()
            content = raw_output
            
            # Special handling for news agent - it writes to files
            if agent_name == "news":
                content = self._read_news_file(project_root, raw_output)
                logger.info(f"News agent file content length: {len(content)} characters")
            else:
                logger.info(f"Agent response length: {len(raw_output)} characters")
            
            # Parse agent response
            return AgentResponse(
                content=content,
                sources=self._extract_sources(content),
                metadata={
                    "agent": agent_name, 
                    "query": query,
                    "response_length": len(content),
                    "output_method": "file" if agent_name == "news" else "stdout"
                },
                raw_output=raw_output
            )
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"OpenCode agent '{agent_name}' timed out after {self.timeout}s")
        except Exception as e:
            logger.error(f"Error invoking agent: {e}")
            raise
    
    def _extract_sources(self, output: str) -> Optional[List[str]]:
        """Extract source URLs/references from agent output"""
        # Look for URLs in the output
        url_pattern = r'https?://[^\s\)]+|www\.[^\s\)]+'
        urls = re.findall(url_pattern, output)
        
        # Look for source references (customize based on actual format)
        source_pattern = r'(?i)source[s]?:\s*(.+?)(?:\n|$)'
        source_matches = re.findall(source_pattern, output)
        
        # Look for numbered source references like [1], [2], etc.
        numbered_sources = re.findall(r'\[(\d+)\]\s*([^\n]+)', output)
        source_refs = [f"[{num}] {text}" for num, text in numbered_sources]
        
        all_sources = urls + source_matches + source_refs
        return all_sources if all_sources else None
    
    def _read_news_file(self, project_root: Path, raw_output: str) -> str:
        """Read news file output from the news agent"""
        from datetime import datetime
        
        # Look for file path in the output
        file_pattern = r'📄 News report saved to: ([^\n]+)'
        match = re.search(file_pattern, raw_output)
        
        if match:
            file_path = Path(match.group(1))
            if not file_path.is_absolute():
                file_path = project_root / file_path
        else:
            # Fallback: try today's date format
            today = datetime.now().strftime("%Y-%m-%d")
            file_path = project_root / f"news-{today}.md"
        
        try:
            if file_path.exists():
                content = file_path.read_text()
                logger.info(f"Read news file: {file_path} ({len(content)} chars)")
                return content
            else:
                logger.warning(f"News file not found: {file_path}")
                return raw_output
        except Exception as e:
            logger.error(f"Error reading news file {file_path}: {e}")
            return raw_output

class AgentInterface:
    """Interface for interacting with a specific OpenCode agent"""
    
    def __init__(self, client: OpenCodeClient, agent_name: str):
        self.client = client
        self.agent_name = agent_name
    
    def query(self, input_text: str) -> AgentResponse:
        """Query this specific agent"""
        return self.client.invoke_agent(self.agent_name, input_text)
    
    def __repr__(self):
        return f"AgentInterface(agent='{self.agent_name}')"