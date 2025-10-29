"""
Tests for cache module.
"""

import pytest
from src.cache import FilterCache


class TestFilterCache:
    """Test filter cache functionality."""
    
    def test_cache_initialization(self):
        """Test cache initialization."""
        cache = FilterCache(max_size=5)
        assert cache.size == 0
        assert cache.hit_rate == 0.0
        assert cache.stats['max_size'] == 5
    
    def test_cache_set_and_get(self):
        """Test setting and getting cached values."""
        cache = FilterCache()
        words = ['casa', 'livro', 'escola']
        
        # Set cache
        cache.set(
            filter_plurals=True,
            filter_conjugated_verbs=False,
            original_word_count=1000,
            filtered_words=words
        )
        
        # Get from cache
        cached = cache.get(
            filter_plurals=True,
            filter_conjugated_verbs=False,
            original_word_count=1000
        )
        
        assert cached is not None
        assert cached == words
        assert cache.size == 1
        assert cache.hit_rate == 1.0
    
    def test_cache_miss(self):
        """Test cache miss."""
        cache = FilterCache()
        
        # Try to get non-existent entry
        cached = cache.get(
            filter_plurals=True,
            filter_conjugated_verbs=True,
            original_word_count=1000
        )
        
        assert cached is None
        assert cache.size == 0
        assert cache.hit_rate == 0.0
    
    def test_cache_different_filters(self):
        """Test cache with different filter combinations."""
        cache = FilterCache()
        
        words1 = ['casa', 'livro']
        words2 = ['amar', 'comer']
        words3 = ['escola', 'aluno']
        
        # Cache different combinations
        cache.set(True, False, 1000, words1)
        cache.set(False, True, 1000, words2)
        cache.set(True, True, 1000, words3)
        
        # Get each combination
        assert cache.get(True, False, 1000) == words1
        assert cache.get(False, True, 1000) == words2
        assert cache.get(True, True, 1000) == words3
        
        assert cache.size == 3
    
    def test_cache_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = FilterCache(max_size=3)
        
        # Fill cache
        cache.set(True, False, 1000, ['a'])
        cache.set(False, True, 1000, ['b'])
        cache.set(True, True, 1000, ['c'])
        
        assert cache.size == 3
        
        # Add one more - should evict oldest
        cache.set(False, False, 1000, ['d'])
        
        assert cache.size == 3
        # First entry should be evicted
        assert cache.get(True, False, 1000) is None
        # Others should still be there
        assert cache.get(False, True, 1000) == ['b']
        assert cache.get(True, True, 1000) == ['c']
        assert cache.get(False, False, 1000) == ['d']
    
    def test_cache_lru_ordering(self):
        """Test that accessing entries updates LRU order."""
        cache = FilterCache(max_size=2)
        
        cache.set(True, False, 1000, ['a'])
        cache.set(False, True, 1000, ['b'])
        
        # Access first entry to make it recently used
        cache.get(True, False, 1000)
        
        # Add third entry - should evict second entry, not first
        cache.set(True, True, 1000, ['c'])
        
        assert cache.get(True, False, 1000) == ['a']  # Still there
        assert cache.get(False, True, 1000) is None   # Evicted
        assert cache.get(True, True, 1000) == ['c']   # New entry
    
    def test_cache_clear(self):
        """Test cache clearing."""
        cache = FilterCache()
        
        cache.set(True, False, 1000, ['a'])
        cache.set(False, True, 1000, ['b'])
        
        assert cache.size == 2
        
        cache.clear()
        
        assert cache.size == 0
        assert cache.hit_rate == 0.0
        assert cache.get(True, False, 1000) is None
    
    def test_cache_no_filters(self):
        """Test that no filters returns None (no caching)."""
        cache = FilterCache()
        
        # Should not cache when both filters are False
        cache.set(False, False, 1000, ['a', 'b', 'c'])
        
        assert cache.size == 0
        
        # Should return None for no filters
        assert cache.get(False, False, 1000) is None
    
    def test_cache_word_count_invalidation(self):
        """Test that different word counts result in cache miss."""
        cache = FilterCache()
        
        words = ['casa', 'livro']
        
        cache.set(True, False, 1000, words)
        
        # Same filters but different word count - should miss
        assert cache.get(True, False, 1000) == words
        assert cache.get(True, False, 2000) is None
    
    def test_cache_stats(self):
        """Test cache statistics."""
        cache = FilterCache(max_size=5)
        
        cache.set(True, False, 1000, ['a', 'b'])
        cache.set(False, True, 1000, ['c', 'd', 'e'])
        
        cache.get(True, False, 1000)  # Hit
        cache.get(False, True, 1000)  # Hit
        cache.get(True, True, 1000)   # Miss
        
        stats = cache.stats
        
        assert stats['size'] == 2
        assert stats['max_size'] == 5
        assert stats['hits'] == 2
        assert stats['misses'] == 1
        assert stats['hit_rate'] == 2/3
        assert len(stats['entries']) == 2
    
    def test_cache_returns_copy(self):
        """Test that cache returns a copy, not reference."""
        cache = FilterCache()
        
        original = ['casa', 'livro']
        cache.set(True, False, 1000, original)
        
        # Get from cache and modify
        cached = cache.get(True, False, 1000)
        cached.append('escola')
        
        # Original should be unchanged
        assert original == ['casa', 'livro']
        
        # Cache should return original unmodified list on next get
        cached2 = cache.get(True, False, 1000)
        assert cached2 == ['casa', 'livro']
    
    def test_cache_concurrent_access(self):
        """Test thread safety of cache."""
        import threading
        
        cache = FilterCache()
        errors = []
        
        def worker(filter_plurals, filter_verbs, words):
            try:
                cache.set(filter_plurals, filter_verbs, 1000, words)
                result = cache.get(filter_plurals, filter_verbs, 1000)
                assert result == words
            except Exception as e:
                errors.append(e)
        
        threads = []
        for i in range(10):
            t = threading.Thread(
                target=worker,
                args=(i % 2 == 0, i % 3 == 0, [f'word{i}'])
            )
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        assert len(errors) == 0
