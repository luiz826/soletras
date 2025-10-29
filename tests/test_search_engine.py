"""
Unit tests for the SearchEngine class.
"""

import pytest
from src.search_engine import SearchEngine


class TestSearchEngine:
    """Test suite for SearchEngine."""
    
    @pytest.fixture
    def word_list(self):
        """Fixture providing a sample word list."""
        return [
            "casa",
            "carro",
            "pato",
            "gato",
            "mesa",
            "papel",
            "computador",
            "teclado",
            "amor",
            "amora"
        ]
    
    @pytest.fixture
    def engine(self, word_list):
        """Fixture providing a SearchEngine instance."""
        return SearchEngine(word_list)
    
    def test_init(self, word_list):
        """Test SearchEngine initialization."""
        engine = SearchEngine(word_list)
        assert engine.word_list == word_list
    
    def test_search_basic(self, engine):
        """Test basic search functionality."""
        results = engine.search(
            allowed_letters="abcdefghijklmnoprst",  # Added more letters including 'r' and 's'
            required_letter="a",
            min_length=4
        )
        
        assert "casa" in results
        assert "carro" in results
        # "pato" has 'p' which is now in allowed
        assert "pato" in results
    
    def test_search_min_length_filter(self, engine):
        """Test minimum length filtering."""
        results = engine.search(
            allowed_letters="abcdefghijklmnopqrstuvwxyz",
            required_letter="a",
            min_length=5
        )
        
        # Should include "papel", "carro" (5 letters)
        # Should exclude "casa", "pato", "gato", "mesa", "amor" (4 letters)
        assert "papel" in results
        assert "carro" in results
        assert "casa" not in results
        assert "pato" not in results
    
    def test_search_required_letter_filter(self, engine):
        """Test required letter filtering."""
        results = engine.search(
            allowed_letters="abcdefghijklmnopqrstuvwxyz",
            required_letter="o",
            min_length=3
        )
        
        # Should include words with 'o': "carro", "pato", "gato", "amor", "amora", "computador", "teclado"
        # Should exclude: "casa", "mesa", "papel"
        assert "amor" in results
        assert "amora" in results
        assert "casa" not in results
        assert "mesa" not in results
    
    def test_search_allowed_letters_filter(self, engine):
        """Test allowed letters filtering."""
        results = engine.search(
            allowed_letters="aeiou",
            required_letter="a",
            min_length=3
        )
        
        # Only words with letters from "aeiou" and containing "a"
        # None of our test words use only vowels
        assert len(results) == 0
    
    def test_search_sorted_by_length(self, engine):
        """Test results are sorted by length (descending)."""
        results = engine.search(
            allowed_letters="abcdefghijklmnopqrstuvwxyz",
            required_letter="a",
            min_length=3
        )
        
        # Should be sorted longest first
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert len(results[i]) >= len(results[i + 1])
    
    def test_search_sorted_alphabetically_same_length(self):
        """Test words of same length are sorted alphabetically."""
        word_list = ["zebra", "apple", "table", "chair"]
        engine = SearchEngine(word_list)
        
        results = engine.search(
            allowed_letters="abcdefghijklmnopqrstuvwxyz",
            required_letter="a",
            min_length=5
        )
        
        # All 5-letter words with 'a', should be alphabetically sorted
        assert results == ["apple", "chair", "table", "zebra"]
    
    def test_search_no_results(self, engine):
        """Test search with no matching results."""
        results = engine.search(
            allowed_letters="xyz",
            required_letter="x",
            min_length=3
        )
        
        assert results == []
    
    def test_search_empty_word_list(self):
        """Test search with empty word list."""
        engine = SearchEngine([])
        results = engine.search(
            allowed_letters="abc",
            required_letter="a",
            min_length=3
        )
        
        assert results == []
    
    def test_passes_filters_all_pass(self, engine):
        """Test _passes_filters when all filters pass."""
        result = engine._passes_filters(
            word="casa",
            allowed_set=set("abcdefghijklmnopqrstuvwxyz"),  # Include all letters
            required_letter="a",
            min_length=4
        )
        
        assert result is True
    
    def test_passes_filters_length_fail(self, engine):
        """Test _passes_filters when length filter fails."""
        result = engine._passes_filters(
            word="casa",
            allowed_set=set("abcdefghijklmno"),
            required_letter="a",
            min_length=5
        )
        
        assert result is False
    
    def test_passes_filters_required_letter_fail(self, engine):
        """Test _passes_filters when required letter filter fails."""
        result = engine._passes_filters(
            word="casa",
            allowed_set=set("abcdefghijklmno"),
            required_letter="z",
            min_length=4
        )
        
        assert result is False
    
    def test_passes_filters_allowed_letters_fail(self, engine):
        """Test _passes_filters when allowed letters filter fails."""
        result = engine._passes_filters(
            word="casa",
            allowed_set=set("abc"),  # Missing 's'
            required_letter="a",
            min_length=4
        )
        
        assert result is False
