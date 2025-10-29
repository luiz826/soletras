"""
Unit tests for the WordLoader class.
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from src.word_loader import WordLoader


class TestWordLoader:
    """Test suite for WordLoader."""
    
    def test_init(self):
        """Test WordLoader initialization."""
        loader = WordLoader("https://example.com/words.txt")
        assert loader.source == "https://example.com/words.txt"
        assert loader.word_count == 0
        assert loader.words == []
    
    def test_is_url_with_http(self):
        """Test URL detection with http."""
        loader = WordLoader("http://example.com/words.txt")
        assert loader._is_url("http://example.com/words.txt") is True
    
    def test_is_url_with_https(self):
        """Test URL detection with https."""
        loader = WordLoader("https://example.com/words.txt")
        assert loader._is_url("https://example.com/words.txt") is True
    
    def test_is_url_with_file_path(self):
        """Test URL detection with file path."""
        loader = WordLoader("palavras.txt")
        assert loader._is_url("palavras.txt") is False
    
    def test_parse_content(self):
        """Test content parsing."""
        loader = WordLoader("test.txt")
        content = "casa\ncarro\n\npato\n  gato  \n"
        words = loader._parse_content(content)
        
        assert len(words) == 4
        assert words == ["casa", "carro", "pato", "gato"]
    
    def test_parse_content_with_uppercase(self):
        """Test content parsing with uppercase letters."""
        loader = WordLoader("test.txt")
        content = "CASA\nCARRO\nPato"
        words = loader._parse_content(content)
        
        assert words == ["casa", "carro", "pato"]
    
    def test_parse_content_empty(self):
        """Test parsing empty content."""
        loader = WordLoader("test.txt")
        words = loader._parse_content("")
        
        assert words == []
    
    @patch('urllib.request.urlopen')
    def test_load_from_url(self, mock_urlopen):
        """Test loading words from URL."""
        # Mock response
        mock_response = Mock()
        mock_response.read.return_value = b"casa\ncarro\npato"
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        loader = WordLoader("https://example.com/words.txt")
        loader.load()
        
        assert loader.word_count == 3
        assert "casa" in loader.words
        assert "carro" in loader.words
        assert "pato" in loader.words
    
    @patch('builtins.open', new_callable=mock_open, read_data="casa\ncarro\npato")
    @patch('os.path.exists', return_value=True)
    def test_load_from_file(self, mock_exists, mock_file):
        """Test loading words from file."""
        loader = WordLoader("palavras.txt")
        loader.load()
        
        assert loader.word_count == 3
        assert "casa" in loader.words
        assert "carro" in loader.words
    
    @patch('os.path.exists', return_value=False)
    def test_load_from_nonexistent_file(self, mock_exists):
        """Test loading from nonexistent file raises error."""
        loader = WordLoader("nonexistent.txt")
        
        with pytest.raises(Exception, match="Failed to load from all"):
            loader.load()
    
    @patch('urllib.request.urlopen')
    def test_load_from_url_failure(self, mock_urlopen):
        """Test handling URL loading failure."""
        mock_urlopen.side_effect = Exception("Network error")
        
        loader = WordLoader("https://example.com/words.txt")
        
        with pytest.raises(Exception):
            loader.load()
