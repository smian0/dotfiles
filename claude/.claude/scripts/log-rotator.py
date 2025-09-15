#!/usr/bin/env python3
"""
Efficient Log Rotator for Claude Hooks

Fast, reliable log rotation with compression and atomic operations.
Optimized for high-frequency hook execution with minimal overhead.
"""

import json
import gzip
import os
from pathlib import Path
from typing import Dict, Any
import time


class LogRotator:
    """High-performance log rotator with size/entry limits and compression"""
    
    def __init__(self, log_path: str, format: str = "jsonl", 
                 max_size_mb: float = 5.0, max_entries: int = 1000,
                 max_archives: int = 3, compress: bool = True):
        self.log_path = Path(log_path).expanduser()
        self.format = format
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        self.max_entries = max_entries
        self.max_archives = max_archives
        self.compress = compress
        
        # Ensure directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Cache for performance
        self._last_check = 0
        self._cached_size = 0
        self._check_interval = 10  # Check rotation need every 10 appends
        self._append_count = 0
    
    def append(self, entry: Dict[str, Any]) -> None:
        """Append entry with minimal overhead rotation checking"""
        try:
            # Add timestamp
            entry.setdefault('timestamp', time.time())
            
            # Efficient rotation check (not every append)
            self._append_count += 1
            if self._append_count % self._check_interval == 0:
                if self._should_rotate():
                    self._rotate()
            
            # Fast append
            with open(self.log_path, 'a') as f:
                json.dump(entry, f, separators=(',', ':'))
                f.write('\n')
        
        except Exception:
            pass  # Never disrupt calling process
    
    def _should_rotate(self) -> bool:
        """Efficient rotation check with caching"""
        if not self.log_path.exists():
            return False
        
        try:
            stat = self.log_path.stat()
            
            # Size check (fast)
            if stat.st_size > self.max_size_bytes:
                return True
            
            # Entry count check (only if size is close to limit)
            if stat.st_size > self.max_size_bytes * 0.8:
                return self._count_entries() >= self.max_entries
            
            return False
        
        except Exception:
            return False
    
    def _count_entries(self) -> int:
        """Fast line counting for JSONL files"""
        try:
            with open(self.log_path, 'rb') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
    
    def _rotate(self) -> None:
        """Atomic log rotation with error recovery"""
        if not self.log_path.exists():
            return
        
        try:
            timestamp = int(time.time())
            temp_path = self.log_path.with_suffix(f'.rotating.{timestamp}')
            
            # Atomic move to temp file
            self.log_path.rename(temp_path)
            
            # Create new log immediately
            self.log_path.touch()
            
            # Background compression and cleanup
            self._archive_file(temp_path, timestamp)
            self._cleanup_archives()
        
        except Exception:
            # Recovery: if rotation failed, ensure log exists
            if not self.log_path.exists():
                self.log_path.touch()
    
    def _archive_file(self, source_path: Path, timestamp: int) -> None:
        """Archive and optionally compress log file"""
        try:
            base_name = self.log_path.stem
            
            if self.compress:
                archive_path = self.log_path.parent / f"{base_name}_{timestamp}.gz"
                with open(source_path, 'rb') as f_in:
                    with gzip.open(archive_path, 'wb', compresslevel=6) as f_out:
                        f_out.writelines(f_in)
                source_path.unlink()  # Remove temp file
            else:
                archive_path = self.log_path.parent / f"{base_name}_{timestamp}.log"
                source_path.rename(archive_path)
        
        except Exception:
            # Cleanup temp file on failure
            try:
                source_path.unlink()
            except Exception:
                pass
    
    def _cleanup_archives(self) -> None:
        """Remove excess archive files"""
        try:
            base_name = self.log_path.stem
            ext = "*.gz" if self.compress else "*.log"
            pattern = f"{base_name}_*[0-9].{ext.lstrip('*.')}"
            
            archives = list(self.log_path.parent.glob(pattern))
            archives.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            
            # Remove excess archives
            for archive in archives[self.max_archives:]:
                archive.unlink()
        
        except Exception:
            pass


# Simple test when run directly
if __name__ == "__main__":
    rotator = LogRotator("test.jsonl", max_entries=5, max_size_mb=0.001)
    for i in range(12):
        rotator.append({"test": i, "data": "x" * 200})
    print("Test complete")