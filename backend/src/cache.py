"""
Cache module for storing filtered word lists.
Implements an in-memory cache with LRU eviction policy.
"""

from typing import List, Optional, Tuple
import hashlib
import logging
from collections import OrderedDict
from threading import Lock

logger = logging.getLogger(__name__)


class FilterCache:
    """
    LRU cache for filtered word lists.
    
    Caches different combinations of filters to avoid re-processing
    the same filter combinations multiple times.
    """
    
    def __init__(self, max_size: int = 10):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of cached filter combinations
        """
        self._cache: OrderedDict[str, List[str]] = OrderedDict()
        self._max_size = max_size
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
        
        logger.info(f"Filter cache initialized (max_size={max_size})")
    
    def _generate_key(
        self,
        filter_plurals: bool,
        filter_conjugated_verbs: bool,
        original_word_count: int
    ) -> str:
        """
        Generate a cache key for a filter combination.
        
        Args:
            filter_plurals: Whether plurals are filtered
            filter_conjugated_verbs: Whether conjugated verbs are filtered
            original_word_count: Number of words in original list (for invalidation)
        
        Returns:
            Cache key string
        """
        key_data = f"{filter_plurals}:{filter_conjugated_verbs}:{original_word_count}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(
        self,
        filter_plurals: bool,
        filter_conjugated_verbs: bool,
        original_word_count: int
    ) -> Optional[List[str]]:
        """
        Get cached filtered word list if available.
        
        Args:
            filter_plurals: Whether plurals are filtered
            filter_conjugated_verbs: Whether conjugated verbs are filtered
            original_word_count: Number of words in original list
        
        Returns:
            Cached word list or None if not found
        """
        if not filter_plurals and not filter_conjugated_verbs:
            # No filters, no cache needed
            return None
        
        key = self._generate_key(filter_plurals, filter_conjugated_verbs, original_word_count)
        
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                self._hits += 1
                logger.debug(
                    f"Cache HIT (plurals={filter_plurals}, verbs={filter_conjugated_verbs}) "
                    f"- Hit rate: {self.hit_rate:.1%}"
                )
                return self._cache[key].copy()  # Return copy to prevent modification
            else:
                self._misses += 1
                logger.debug(
                    f"Cache MISS (plurals={filter_plurals}, verbs={filter_conjugated_verbs}) "
                    f"- Hit rate: {self.hit_rate:.1%}"
                )
                return None
    
    def set(
        self,
        filter_plurals: bool,
        filter_conjugated_verbs: bool,
        original_word_count: int,
        filtered_words: List[str]
    ) -> None:
        """
        Store filtered word list in cache.
        
        Args:
            filter_plurals: Whether plurals are filtered
            filter_conjugated_verbs: Whether conjugated verbs are filtered
            original_word_count: Number of words in original list
            filtered_words: Filtered word list to cache
        """
        if not filter_plurals and not filter_conjugated_verbs:
            # No filters, no cache needed
            return
        
        key = self._generate_key(filter_plurals, filter_conjugated_verbs, original_word_count)
        
        with self._lock:
            # Store copy to prevent external modifications
            self._cache[key] = filtered_words.copy()
            self._cache.move_to_end(key)
            
            # Evict oldest entry if cache is full
            if len(self._cache) > self._max_size:
                evicted_key = next(iter(self._cache))
                del self._cache[evicted_key]
                logger.debug(f"Cache eviction - Size: {len(self._cache)}/{self._max_size}")
            
            logger.debug(
                f"Cache SET (plurals={filter_plurals}, verbs={filter_conjugated_verbs}) "
                f"- {len(filtered_words)} words cached - Size: {len(self._cache)}/{self._max_size}"
            )
    
    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            size = len(self._cache)
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            logger.info(f"Cache cleared - {size} entries removed")
    
    @property
    def size(self) -> int:
        """Get current number of cached entries."""
        return len(self._cache)
    
    @property
    def hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total
    
    @property
    def stats(self) -> dict:
        """Get cache statistics."""
        return {
            'size': self.size,
            'max_size': self._max_size,
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': self.hit_rate,
            'entries': [
                {
                    'key': key[:8],  # First 8 chars of hash
                    'words_count': len(words)
                }
                for key, words in self._cache.items()
            ]
        }
