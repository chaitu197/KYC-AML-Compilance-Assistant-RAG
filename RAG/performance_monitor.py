"""
Performance Metrics Module
Track and monitor system performance for production readiness
"""

import time
from typing import Dict, List, Optional
from datetime import datetime
from collections import deque
import statistics


class PerformanceMonitor:
    """Monitor system performance metrics."""
    
    def __init__(self, history_size: int = 1000):
        """Initialize performance monitor."""
        self.history_size = history_size
        
        # Metric queues (keep last N measurements)
        self.query_times = deque(maxlen=history_size)
        self.embedding_times = deque(maxlen=history_size)
        self.search_times = deque(maxlen=history_size)
        self.llm_times = deque(maxlen=history_size)
        
        # Counters
        self.total_queries = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Start time
        self.start_time = datetime.now()
    
    def record_query_time(self, duration: float):
        """Record query processing time."""
        self.query_times.append(duration)
        self.total_queries += 1
    
    def record_embedding_time(self, duration: float):
        """Record embedding generation time."""
        self.embedding_times.append(duration)
    
    def record_search_time(self, duration: float):
        """Record vector search time."""
        self.search_times.append(duration)
    
    def record_llm_time(self, duration: float):
        """Record LLM generation time."""
        self.llm_times.append(duration)
    
    def record_cache_hit(self):
        """Record cache hit."""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record cache miss."""
        self.cache_misses += 1
    
    def get_metrics(self) -> Dict:
        """Get current performance metrics."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        metrics = {
            "uptime_seconds": round(uptime, 2),
            "uptime_formatted": self._format_uptime(uptime),
            "total_queries": self.total_queries,
            "queries_per_minute": round((self.total_queries / uptime) * 60, 2) if uptime > 0 else 0,
            "cache_hit_rate": round((self.cache_hits / (self.cache_hits + self.cache_misses)) * 100, 2) 
                if (self.cache_hits + self.cache_misses) > 0 else 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Query time statistics
        if self.query_times:
            metrics["query_time"] = {
                "avg": round(statistics.mean(self.query_times), 3),
                "median": round(statistics.median(self.query_times), 3),
                "min": round(min(self.query_times), 3),
                "max": round(max(self.query_times), 3),
                "p95": round(self._percentile(list(self.query_times), 95), 3),
                "p99": round(self._percentile(list(self.query_times), 99), 3)
            }
        
        # Embedding time statistics
        if self.embedding_times:
            metrics["embedding_time"] = {
                "avg": round(statistics.mean(self.embedding_times), 3),
                "median": round(statistics.median(self.embedding_times), 3)
            }
        
        # Search time statistics
        if self.search_times:
            metrics["search_time"] = {
                "avg": round(statistics.mean(self.search_times), 3),
                "median": round(statistics.median(self.search_times), 3)
            }
        
        # LLM time statistics
        if self.llm_times:
            metrics["llm_time"] = {
                "avg": round(statistics.mean(self.llm_times), 3),
                "median": round(statistics.median(self.llm_times), 3)
            }
        
        return metrics
    
    def get_performance_summary(self) -> str:
        """Get formatted performance summary."""
        metrics = self.get_metrics()
        
        summary = f"""
# Performance Metrics
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Uptime
- Uptime: {metrics['uptime_formatted']}
- Total Queries: {metrics['total_queries']}
- Queries/Minute: {metrics['queries_per_minute']}

## Cache Performance
- Cache Hit Rate: {metrics['cache_hit_rate']}%
- Cache Hits: {self.cache_hits}
- Cache Misses: {self.cache_misses}

## Query Performance
"""
        
        if 'query_time' in metrics:
            qt = metrics['query_time']
            summary += f"""- Average: {qt['avg']}s
- Median: {qt['median']}s
- Min: {qt['min']}s
- Max: {qt['max']}s
- P95: {qt['p95']}s
- P99: {qt['p99']}s

"""
        
        if 'embedding_time' in metrics:
            summary += f"""## Embedding Generation
- Average: {metrics['embedding_time']['avg']}s
- Median: {metrics['embedding_time']['median']}s

"""
        
        if 'search_time' in metrics:
            summary += f"""## Vector Search
- Average: {metrics['search_time']['avg']}s
- Median: {metrics['search_time']['median']}s

"""
        
        if 'llm_time' in metrics:
            summary += f"""## LLM Generation
- Average: {metrics['llm_time']['avg']}s
- Median: {metrics['llm_time']['median']}s
"""
        
        return summary
    
    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format."""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile."""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]


class TimingContext:
    """Context manager for timing operations."""
    
    def __init__(self, monitor: PerformanceMonitor, metric_name: str):
        """Initialize timing context."""
        self.monitor = monitor
        self.metric_name = metric_name
        self.start_time = None
    
    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and record."""
        duration = time.time() - self.start_time
        
        if self.metric_name == 'query':
            self.monitor.record_query_time(duration)
        elif self.metric_name == 'embedding':
            self.monitor.record_embedding_time(duration)
        elif self.metric_name == 'search':
            self.monitor.record_search_time(duration)
        elif self.metric_name == 'llm':
            self.monitor.record_llm_time(duration)


# Example usage
if __name__ == "__main__":
    monitor = PerformanceMonitor()
    
    # Simulate some queries
    import random
    for _ in range(100):
        monitor.record_query_time(random.uniform(0.5, 2.0))
        monitor.record_embedding_time(random.uniform(0.1, 0.3))
        monitor.record_search_time(random.uniform(0.2, 0.5))
        monitor.record_llm_time(random.uniform(0.3, 1.0))
    
    # Simulate cache
    for _ in range(50):
        if random.random() > 0.3:
            monitor.record_cache_hit()
        else:
            monitor.record_cache_miss()
    
    print(monitor.get_performance_summary())
