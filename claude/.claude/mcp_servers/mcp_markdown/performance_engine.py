"""
Performance optimization and caching engine.

This module provides caching, bulk operations, and performance optimizations
to address the performance penalties of process-based markdown tools.
"""

import gc
import hashlib
import os
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable

# Memory monitoring imports
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Warning: psutil not available. Memory monitoring disabled.")

try:
    from .core import PATTERNS, MarkdownParser, MarkdownError
except ImportError:
    from core import PATTERNS, MarkdownParser, MarkdownError


class Config:
    """Configuration for performance engine with memory protection."""
    MAX_MEMORY_MB = int(os.environ.get('MCP_MAX_MEMORY_MB', '2048'))
    MAX_BATCH_SIZE = int(os.environ.get('MCP_MAX_BATCH_SIZE', '100'))
    ENABLE_STREAMING = os.environ.get('MCP_ENABLE_STREAMING', 'true').lower() == 'true'
    CACHE_TTL = int(os.environ.get('MCP_CACHE_TTL', '3600'))
    ENABLE_MEMORY_MONITOR = os.environ.get('MCP_ENABLE_MEMORY_MONITOR', 'true').lower() == 'true'
    REGEX_TIMEOUT_SECONDS = int(os.environ.get('MCP_REGEX_TIMEOUT', '5'))
    STREAMING_CHUNK_SIZE = int(os.environ.get('MCP_STREAMING_CHUNK_SIZE', '100'))


class CacheEntry:
    """Cache entry with TTL and invalidation support."""
    
    def __init__(self, data: Any, file_mtime: float = None, ttl: int = 3600):
        self.data = data
        self.created_at = time.time()
        self.file_mtime = file_mtime
        self.ttl = ttl
    
    def is_valid(self, current_mtime: float = None) -> bool:
        """Check if cache entry is still valid."""
        now = time.time()
        
        # Check TTL expiration
        if now - self.created_at > self.ttl:
            return False
        
        # Check file modification time
        if current_mtime is not None and self.file_mtime is not None:
            if current_mtime > self.file_mtime:
                return False
        
        return True


class PerformanceEngine:
    """Engine for performance optimization and intelligent caching."""
    
    def __init__(self, cache_ttl: int = 3600, max_cache_size: int = 1000):
        """Initialize performance engine with configurable cache settings."""
        self.cache_ttl = cache_ttl
        self.max_cache_size = max_cache_size
        
        # Multi-level caching
        self.file_content_cache = {}  # file_path -> CacheEntry(content)
        self.result_cache = {}        # (file_path, operation_hash) -> CacheEntry(result)
        self.bulk_cache = {}          # (files_hash, operation) -> CacheEntry(results)
        
        # Performance tracking
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "files_processed": 0,
            "total_processing_time": 0.0
        }
    
    def get_cached_content(self, file_path: str) -> Optional[str]:
        """Get cached file content with automatic invalidation."""
        if file_path not in self.file_content_cache:
            return None
        
        # Check if file exists and get mtime
        path = Path(file_path)
        if not path.exists():
            # File deleted, remove from cache
            del self.file_content_cache[file_path]
            return None
        
        current_mtime = path.stat().st_mtime
        cache_entry = self.file_content_cache[file_path]
        
        if cache_entry.is_valid(current_mtime):
            self.stats["cache_hits"] += 1
            return cache_entry.data
        else:
            # Cache invalid, remove entry
            del self.file_content_cache[file_path]
            self.stats["cache_misses"] += 1
            return None
    
    def cache_content(self, file_path: str, content: str) -> None:
        """Cache file content with metadata."""
        # Implement LRU-style cache size management
        if len(self.file_content_cache) >= self.max_cache_size:
            self._evict_oldest_cache_entries(self.file_content_cache, 0.2)  # Remove 20%
        
        path = Path(file_path)
        mtime = path.stat().st_mtime if path.exists() else None
        
        self.file_content_cache[file_path] = CacheEntry(
            data=content,
            file_mtime=mtime,
            ttl=self.cache_ttl
        )
    
    def get_cached_result(self, file_path: str, operation: str, params: Dict = None) -> Optional[Any]:
        """Get cached operation result."""
        cache_key = self._generate_cache_key(file_path, operation, params)
        
        if cache_key not in self.result_cache:
            return None
        
        # Check file modification time
        path = Path(file_path)
        if not path.exists():
            del self.result_cache[cache_key]
            return None
        
        current_mtime = path.stat().st_mtime
        cache_entry = self.result_cache[cache_key]
        
        if cache_entry.is_valid(current_mtime):
            self.stats["cache_hits"] += 1
            return cache_entry.data
        else:
            del self.result_cache[cache_key]
            self.stats["cache_misses"] += 1
            return None
    
    def cache_result(self, file_path: str, operation: str, result: Any, params: Dict = None) -> None:
        """Cache operation result."""
        if len(self.result_cache) >= self.max_cache_size:
            self._evict_oldest_cache_entries(self.result_cache, 0.2)
        
        cache_key = self._generate_cache_key(file_path, operation, params)
        path = Path(file_path)
        mtime = path.stat().st_mtime if path.exists() else None
        
        self.result_cache[cache_key] = CacheEntry(
            data=result,
            file_mtime=mtime,
            ttl=self.cache_ttl
        )
    
    def bulk_operation_optimized(self, file_paths: List[str], operation_func: Callable, 
                               operation_name: str, batch_size: int = 50, 
                               use_cache: bool = True) -> Dict[str, Any]:
        """Execute bulk operations with intelligent batching and caching."""
        start_time = time.time()
        results = {}
        cache_hits = 0
        cache_misses = 0
        
        # Memory protection - initialize monitoring
        process = None
        memory_limit_mb = Config.MAX_MEMORY_MB
        
        if HAS_PSUTIL and Config.ENABLE_MEMORY_MONITOR:
            process = psutil.Process()
            initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
            
            if initial_memory > memory_limit_mb * 0.8:  # 80% threshold
                return {
                    "error": f"Memory usage {initial_memory:.1f}MB exceeds safety threshold ({memory_limit_mb * 0.8:.1f}MB)",
                    "suggestion": "Reduce batch size or use streaming mode"
                }
        
        # Adaptive batch sizing based on file count and memory constraints
        if len(file_paths) > 100:
            batch_size = min(batch_size, Config.MAX_BATCH_SIZE)
        
        # Enable streaming mode for very large datasets
        if Config.ENABLE_STREAMING and len(file_paths) > Config.STREAMING_CHUNK_SIZE * 2:
            return self._stream_bulk_operation(file_paths, operation_func, operation_name)
        
        # Check for bulk cache hit
        files_hash = self._hash_file_list(file_paths)
        bulk_cache_key = f"{files_hash}_{operation_name}"
        
        if use_cache and bulk_cache_key in self.bulk_cache:
            cache_entry = self.bulk_cache[bulk_cache_key]
            if self._is_bulk_cache_valid(file_paths, cache_entry):
                self.stats["cache_hits"] += 1
                return cache_entry.data
        
        # Process files in batches for memory efficiency
        for i in range(0, len(file_paths), batch_size):
            batch = file_paths[i:i + batch_size]
            
            # Memory monitoring during processing
            if HAS_PSUTIL and Config.ENABLE_MEMORY_MONITOR and i % (batch_size * 2) == 0:
                current_memory = process.memory_info().rss / (1024 * 1024)
                if current_memory > memory_limit_mb:
                    # Force garbage collection and cache cleanup
                    gc.collect()
                    self._cleanup_expired_cache()
                    
                    # Check again after cleanup
                    current_memory = process.memory_info().rss / (1024 * 1024)
                    if current_memory > memory_limit_mb:
                        return {
                            "error": f"Memory limit exceeded: {current_memory:.1f}MB > {memory_limit_mb}MB",
                            "processed_files": len(results),
                            "suggestion": "Reduce batch size or increase memory limit"
                        }
            
            for file_path in batch:
                try:
                    # Try cache first
                    if use_cache:
                        cached_result = self.get_cached_result(file_path, operation_name)
                        if cached_result is not None:
                            results[file_path] = cached_result
                            cache_hits += 1
                            continue
                    
                    # Execute operation
                    cache_misses += 1
                    result = operation_func(file_path)
                    results[file_path] = result
                    
                    # Cache result
                    if use_cache:
                        self.cache_result(file_path, operation_name, result)
                        
                except Exception as e:
                    results[file_path] = {"error": str(e)}
        
        # Cache bulk result
        if use_cache and len(file_paths) > 10:  # Only cache larger bulk operations
            self._cache_bulk_result(bulk_cache_key, results, file_paths)
        
        processing_time = time.time() - start_time
        
        # Update stats
        self.stats["files_processed"] += len(file_paths)
        self.stats["total_processing_time"] += processing_time
        self.stats["cache_hits"] += cache_hits
        self.stats["cache_misses"] += cache_misses
        
        return {
            "results": results,
            "performance": {
                "files_processed": len(file_paths),
                "processing_time": processing_time,
                "cache_hits": cache_hits,
                "cache_misses": cache_misses,
                "cache_hit_ratio": cache_hits / (cache_hits + cache_misses) if (cache_hits + cache_misses) > 0 else 0
            }
        }
    
    def stream_large_operation(self, file_paths: List[str], operation_func: Callable, 
                             chunk_size: int = 100) -> Any:
        """Stream processing for very large datasets to minimize memory usage."""
        for i in range(0, len(file_paths), chunk_size):
            chunk = file_paths[i:i + chunk_size]
            
            # Process chunk and yield results
            for file_path in chunk:
                try:
                    result = operation_func(file_path)
                    yield file_path, result
                except Exception as e:
                    yield file_path, {"error": str(e)}
                
                # Periodic cache cleanup during long operations
                if i % (chunk_size * 10) == 0:
                    self._cleanup_expired_cache()
    
    def _stream_bulk_operation(self, file_paths: List[str], operation_func: Callable, 
                             operation_name: str) -> Dict[str, Any]:
        """Stream processing for large bulk operations with memory protection."""
        results = {}
        processed_count = 0
        error_count = 0
        
        if HAS_PSUTIL and Config.ENABLE_MEMORY_MONITOR:
            process = psutil.Process()
            memory_limit_mb = Config.MAX_MEMORY_MB
        
        chunk_size = Config.STREAMING_CHUNK_SIZE
        
        for i in range(0, len(file_paths), chunk_size):
            chunk = file_paths[i:i + chunk_size]
            
            # Memory check before each chunk
            if HAS_PSUTIL and Config.ENABLE_MEMORY_MONITOR:
                current_memory = process.memory_info().rss / (1024 * 1024)
                if current_memory > memory_limit_mb * 0.9:  # 90% threshold for streaming
                    gc.collect()
                    self._cleanup_expired_cache()
            
            # Process chunk
            for file_path in chunk:
                try:
                    # Try cache first
                    cached_result = self.get_cached_result(file_path, operation_name)
                    if cached_result is not None:
                        results[file_path] = cached_result
                    else:
                        result = operation_func(file_path)
                        results[file_path] = result
                        self.cache_result(file_path, operation_name, result)
                    
                    processed_count += 1
                    
                except Exception as e:
                    results[file_path] = {"error": str(e)}
                    error_count += 1
        
        return {
            "results": results,
            "streaming_stats": {
                "total_files": len(file_paths),
                "processed": processed_count,
                "errors": error_count,
                "chunk_size": chunk_size
            }
        }
    
    def intelligent_file_discovery(self, search_path: str, pattern: str = "*.md", 
                                 max_size_mb: int = 100) -> List[str]:
        """Intelligently discover files with size and performance constraints."""
        path = Path(search_path)
        discovered_files = []
        total_size = 0
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if path.is_file():
            return [str(path)] if path.suffix == '.md' else []
        
        # Sort by modification time (most recent first) for better cache locality
        files = sorted(path.rglob(pattern), key=lambda f: f.stat().st_mtime, reverse=True)
        
        for file_path in files:
            try:
                file_size = file_path.stat().st_size
                if total_size + file_size > max_size_bytes:
                    break  # Respect size limits
                
                discovered_files.append(str(file_path))
                total_size += file_size
                
            except (OSError, IOError):
                continue  # Skip files we can't access
        
        return discovered_files
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        total_requests = self.stats["cache_hits"] + self.stats["cache_misses"]
        
        return {
            "cache_performance": {
                "hits": self.stats["cache_hits"],
                "misses": self.stats["cache_misses"],
                "hit_ratio": self.stats["cache_hits"] / total_requests if total_requests > 0 else 0,
                "total_requests": total_requests
            },
            "processing_stats": {
                "files_processed": self.stats["files_processed"],
                "total_time": self.stats["total_processing_time"],
                "avg_time_per_file": self.stats["total_processing_time"] / self.stats["files_processed"] if self.stats["files_processed"] > 0 else 0
            },
            "cache_sizes": {
                "content_cache": len(self.file_content_cache),
                "result_cache": len(self.result_cache),
                "bulk_cache": len(self.bulk_cache),
                "total_entries": len(self.file_content_cache) + len(self.result_cache) + len(self.bulk_cache)
            }
        }
    
    def clear_cache(self, cache_type: str = "all") -> None:
        """Clear specified cache or all caches."""
        if cache_type == "all":
            self.file_content_cache.clear()
            self.result_cache.clear()
            self.bulk_cache.clear()
        elif cache_type == "content":
            self.file_content_cache.clear()
        elif cache_type == "results":
            self.result_cache.clear()
        elif cache_type == "bulk":
            self.bulk_cache.clear()
    
    def optimize_for_dataset(self, file_count: int, avg_file_size_kb: int) -> None:
        """Automatically optimize cache settings based on dataset characteristics."""
        total_size_mb = (file_count * avg_file_size_kb) / 1024
        
        if total_size_mb > 500:  # Large dataset
            self.cache_ttl = 7200  # Longer TTL for large datasets
            self.max_cache_size = 2000  # Larger cache
        elif total_size_mb > 100:  # Medium dataset
            self.cache_ttl = 3600  # Standard TTL
            self.max_cache_size = 1000  # Standard cache
        else:  # Small dataset
            self.cache_ttl = 1800   # Shorter TTL for small datasets
            self.max_cache_size = 500   # Smaller cache
    
    # Private helper methods
    def _generate_cache_key(self, file_path: str, operation: str, params: Dict = None) -> str:
        """Generate unique cache key for operation."""
        key_parts = [file_path, operation]
        if params:
            key_parts.append(str(sorted(params.items())))
        
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _hash_file_list(self, file_paths: List[str]) -> str:
        """Generate hash for list of files."""
        files_string = "|".join(sorted(file_paths))
        return hashlib.md5(files_string.encode()).hexdigest()
    
    def _is_bulk_cache_valid(self, file_paths: List[str], cache_entry: CacheEntry) -> bool:
        """Check if bulk cache entry is still valid."""
        if not cache_entry.is_valid():
            return False
        
        # Check if any file has been modified
        for file_path in file_paths:
            path = Path(file_path)
            if path.exists():
                current_mtime = path.stat().st_mtime
                if cache_entry.file_mtime is None or current_mtime > cache_entry.file_mtime:
                    return False
            else:
                return False  # File deleted
        
        return True
    
    def _cache_bulk_result(self, cache_key: str, results: Dict, file_paths: List[str]) -> None:
        """Cache bulk operation result."""
        if len(self.bulk_cache) >= self.max_cache_size // 4:  # Use 1/4 of cache for bulk operations
            self._evict_oldest_cache_entries(self.bulk_cache, 0.3)
        
        # Get latest mtime from all files
        latest_mtime = 0
        for file_path in file_paths:
            path = Path(file_path)
            if path.exists():
                latest_mtime = max(latest_mtime, path.stat().st_mtime)
        
        self.bulk_cache[cache_key] = CacheEntry(
            data=results,
            file_mtime=latest_mtime,
            ttl=self.cache_ttl
        )
    
    def _evict_oldest_cache_entries(self, cache_dict: Dict, evict_ratio: float) -> None:
        """Evict oldest cache entries based on creation time."""
        entries_to_remove = int(len(cache_dict) * evict_ratio)
        if entries_to_remove == 0:
            return
        
        # Sort by creation time and remove oldest
        sorted_entries = sorted(cache_dict.items(), key=lambda x: x[1].created_at)
        for i in range(entries_to_remove):
            del cache_dict[sorted_entries[i][0]]
    
    def _cleanup_expired_cache(self) -> None:
        """Remove expired entries from all caches."""
        current_time = time.time()
        
        # Cleanup content cache
        expired_keys = [key for key, entry in self.file_content_cache.items() 
                       if current_time - entry.created_at > entry.ttl]
        for key in expired_keys:
            del self.file_content_cache[key]
        
        # Cleanup result cache
        expired_keys = [key for key, entry in self.result_cache.items() 
                       if current_time - entry.created_at > entry.ttl]
        for key in expired_keys:
            del self.result_cache[key]
        
        # Cleanup bulk cache
        expired_keys = [key for key, entry in self.bulk_cache.items() 
                       if current_time - entry.created_at > entry.ttl]
        for key in expired_keys:
            del self.bulk_cache[key]