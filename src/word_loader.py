"""
Word list loader module.
Handles loading and caching of word lists from various sources.
"""

import urllib.request
import os
from typing import List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class WordLoader:
    """Handles loading words from single or multiple URL/file sources."""
    
    def __init__(self, sources: Union[str, List[str]]):
        """
        Initialize the word loader.
        
        Args:
            sources: Single source (string) or list of sources (URLs or file paths)
        """
        # Convert single source to list for uniform handling
        if isinstance(sources, str):
            self.sources = [sources]
        else:
            self.sources = sources
        
        self._words: List[str] = []
        self._source_stats: dict = {}  # Track stats per source
    
    @property
    def source(self) -> str:
        """Get the first source (for backward compatibility)."""
        return self.sources[0] if self.sources else ""
    
    @property
    def words(self) -> List[str]:
        """Get the loaded words."""
        return self._words
    
    @property
    def word_count(self) -> int:
        """Get the number of loaded words."""
        return len(self._words)
    
    @property
    def source_stats(self) -> dict:
        """Get statistics per source."""
        return self._source_stats
    
    def load(self) -> None:
        """
        Load words from all configured sources and merge them.
        
        Raises:
            Exception: If all sources fail to load
        """
        all_words = set()  # Use set to automatically deduplicate
        successful_loads = 0
        failed_sources = []
        
        logger.info(f"Loading words from {len(self.sources)} source(s)...")
        
        for source in self.sources:
            try:
                words = self._load_single_source(source)
                initial_count = len(words)
                
                # Add to set (deduplicates automatically)
                all_words.update(words)
                
                # Track stats
                self._source_stats[source] = {
                    'words_loaded': initial_count,
                    'status': 'success'
                }
                
                successful_loads += 1
                logger.info(f"✓ Loaded {initial_count} words from: {self._truncate_source(source)}")
            
            except Exception as e:
                logger.warning(f"✗ Failed to load from {self._truncate_source(source)}: {e}")
                self._source_stats[source] = {
                    'words_loaded': 0,
                    'status': 'failed',
                    'error': str(e)
                }
                failed_sources.append(source)
        
        if successful_loads == 0:
            error_msg = f"Failed to load from all {len(self.sources)} source(s)"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        # Convert set to sorted list
        self._words = sorted(list(all_words))
        
        logger.info(
            f"Successfully loaded {self.word_count} unique words from "
            f"{successful_loads}/{len(self.sources)} source(s)"
        )
        
        if failed_sources:
            logger.warning(f"Failed sources: {len(failed_sources)}/{len(self.sources)}")
    
    def _truncate_source(self, source: str, max_length: int = 60) -> str:
        """Truncate source string for logging."""
        if len(source) <= max_length:
            return source
        return source[:max_length] + "..."
    
    def _load_single_source(self, source: str) -> List[str]:
        """
        Load words from a single source.
        
        Args:
            source: URL or file path
        
        Returns:
            List of words from this source
        
        Raises:
            Exception: If loading fails
        """
        if self._is_url(source):
            return self._load_from_url(source)
        else:
            return self._load_from_file(source)
    
    def _is_url(self, source: str) -> bool:
        """Check if source is a URL."""
        return source.startswith('http://') or source.startswith('https://')
    
    def _load_from_url(self, url: str) -> List[str]:
        """
        Load words from a URL.
        
        Args:
            url: URL to load from
        
        Returns:
            List of words
        """
        with urllib.request.urlopen(url, timeout=30) as response:
            content = response.read().decode('utf-8', errors='ignore')
            return self._parse_content(content)
    
    def _load_from_file(self, filepath: str) -> List[str]:
        """
        Load words from a local file.
        
        Args:
            filepath: Path to file
        
        Returns:
            List of words
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Word file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            return self._parse_content(content)
    
    def _parse_content(self, content: str) -> List[str]:
        """
        Parse content and extract words.
        
        Special handling for different file formats:
        - .dic files (LibreOffice): Skip first line (word count) and remove suffix markers
        - Plain text: One word per line
        
        Args:
            content: Raw text content
        
        Returns:
            List of cleaned, normalized words
        """
        words = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip first line if it looks like a count (common in .dic files)
            if i == 0 and line.isdigit():
                continue
            
            # Remove suffix markers from .dic files (e.g., "palavra/123")
            if '/' in line:
                line = line.split('/')[0].strip()
            
            # Convert to lowercase and filter out non-alphabetic entries
            word = line.lower()
            
            # Only include if it contains at least some alphabetic characters
            if word and any(c.isalpha() for c in word):
                # Remove non-alphabetic characters except hyphens
                word = ''.join(c for c in word if c.isalpha() or c == '-')
                if word:
                    words.append(word)
        
        return words
