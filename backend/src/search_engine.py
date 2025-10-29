"""
Word search engine module.
Implements the core search algorithm for finding words based on constraints.
"""

from typing import List, Set, Optional
import logging

logger = logging.getLogger(__name__)


class SearchEngine:
    """Implements word search algorithm with constraint-based filtering."""
    
    def __init__(self, word_list: List[str]):
        """
        Initialize the search engine.
        
        Args:
            word_list: List of words to search through
        """
        self.word_list = word_list
    
    def search(
        self,
        allowed_letters: str,
        required_letter: str,
        min_length: int,
        max_length: Optional[int] = None
    ) -> List[str]:
        """
        Search for words matching the given criteria.
        
        The algorithm applies filters in sequence:
        1. Length filter: min_length <= word length <= max_length
        2. Required letter filter: required_letter in word
        3. Allowed letters filter: all letters in word are allowed
        
        Args:
            allowed_letters: String of all valid letters
            required_letter: Single letter that must be in the word
            min_length: Minimum number of letters in the word
            max_length: Maximum number of letters in the word (optional)
        
        Returns:
            List of words matching all criteria, sorted by length (desc) then alphabetically
        """
        # Normalize inputs
        allowed_letters = allowed_letters.lower()
        required_letter = required_letter.lower()
        allowed_set = set(allowed_letters)
        
        # Filter words
        results = self._filter_words(allowed_set, required_letter, min_length, max_length)
        
        # Sort results: shortest first, then alphabetically
        sorted_results = sorted(results, key=lambda w: (len(w), w))
        
        max_info = f", max_len={max_length}" if max_length else ""
        logger.info(
            f"Search completed: {len(results)} results "
            f"(allowed={allowed_letters[:10]}..., required={required_letter}, min_len={min_length}{max_info})"
        )
        
        return sorted_results
    
    def _filter_words(
        self,
        allowed_set: Set[str],
        required_letter: str,
        min_length: int,
        max_length: Optional[int] = None
    ) -> List[str]:
        """
        Apply all filters to the word list.
        
        Args:
            allowed_set: Set of allowed letters for O(1) lookup
            required_letter: Letter that must be present
            min_length: Minimum word length
            max_length: Maximum word length (optional)
        
        Returns:
            List of words passing all filters
        """
        results = []
        
        for word in self.word_list:
            if self._passes_filters(word, allowed_set, required_letter, min_length, max_length):
                results.append(word)
        
        return results
    
    def _passes_filters(
        self,
        word: str,
        allowed_set: Set[str],
        required_letter: str,
        min_length: int,
        max_length: Optional[int] = None
    ) -> bool:
        """
        Check if a word passes all filters.
        
        Filters are applied in order of increasing complexity for optimization.
        
        Args:
            word: Word to check
            allowed_set: Set of allowed letters
            required_letter: Letter that must be present
            min_length: Minimum word length
            max_length: Maximum word length (optional)
        
        Returns:
            True if word passes all filters
        """
        word_len = len(word)
        
        # Filter 1: Length check (cheapest operation)
        if word_len < min_length:
            return False
        
        if max_length is not None and word_len > max_length:
            return False
        
        # Filter 2: Required letter check (O(n) where n is word length)
        if required_letter not in word:
            return False
        
        # Filter 3: All letters allowed check (most expensive)
        if not set(word).issubset(allowed_set):
            return False
        
        return True
