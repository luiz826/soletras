"""
Integration tests for the API endpoints.
"""

import pytest
from src.app import create_app
from src.search_engine import SearchEngine


@pytest.fixture
def app():
    """Create application instance for testing."""
    # Create app with test configuration
    app = create_app('development')
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def mock_app_with_sample_words():
    """Create app with a small sample word list for testing."""
    import os
    os.environ['WORD_SOURCE'] = 'test_words.txt'
    
    # Create temporary word file
    from unittest.mock import patch, mock_open
    test_words = "casa\ncarro\npato\ngato\nmesa\npapel\namor\namora"
    
    with patch('builtins.open', mock_open(read_data=test_words)):
        with patch('os.path.exists', return_value=True):
            app = create_app('development')
            app.config['TESTING'] = True
    
    return app


class TestHealthEndpoint:
    """Tests for /api/health endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint returns 200."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert 'words_loaded' in data
        assert isinstance(data['words_loaded'], int)


class TestRootEndpoint:
    """Tests for / endpoint."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = client.get('/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'name' in data
        assert 'version' in data
        assert 'endpoints' in data
        assert 'words_loaded' in data


class TestSearchEndpoint:
    """Tests for /api/search endpoint."""
    
    def test_search_success(self, client):
        """Test successful search request."""
        response = client.get('/api/search', query_string={
            'allowed_letters': 'abcdefghijklmnopqrstuvwxyz',
            'required_letter': 'a',
            'min_length': '4'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'words' in data
        assert 'count' in data
        assert 'query' in data
        assert isinstance(data['words'], list)
        assert isinstance(data['count'], int)
        assert data['count'] == len(data['words'])
    
    def test_search_query_parameters_preserved(self, client):
        """Test that query parameters are returned in response."""
        response = client.get('/api/search', query_string={
            'allowed_letters': 'abcdefg',
            'required_letter': 'a',
            'min_length': '5'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['query']['allowed_letters'] == 'abcdefg'
        assert data['query']['required_letter'] == 'a'
        assert data['query']['min_length'] == 5
    
    def test_search_missing_allowed_letters(self, client):
        """Test search with missing allowed_letters parameter."""
        response = client.get('/api/search', query_string={
            'required_letter': 'a',
            'min_length': '5'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'allowed_letters' in data['error']
    
    def test_search_missing_required_letter(self, client):
        """Test search with missing required_letter parameter."""
        response = client.get('/api/search', query_string={
            'allowed_letters': 'abc',
            'min_length': '5'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'required_letter' in data['error']
    
    def test_search_missing_min_length(self, client):
        """Test search with missing min_length parameter."""
        response = client.get('/api/search', query_string={
            'allowed_letters': 'abc',
            'required_letter': 'a'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'min_length' in data['error']
    
    def test_search_invalid_min_length(self, client):
        """Test search with invalid min_length parameter."""
        response = client.get('/api/search', query_string={
            'allowed_letters': 'abc',
            'required_letter': 'a',
            'min_length': 'invalid'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'integer' in data['error'].lower()
    
    def test_search_min_length_too_small(self, client):
        """Test search with min_length below minimum."""
        response = client.get('/api/search', query_string={
            'allowed_letters': 'abc',
            'required_letter': 'a',
            'min_length': '0'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_search_required_letter_not_in_allowed(self, client):
        """Test search with required_letter not in allowed_letters."""
        response = client.get('/api/search', query_string={
            'allowed_letters': 'abc',
            'required_letter': 'z',
            'min_length': '3'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_search_case_normalization(self, client):
        """Test that search parameters are normalized to lowercase."""
        response = client.get('/api/search', query_string={
            'allowed_letters': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            'required_letter': 'A',
            'min_length': '4'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['query']['allowed_letters'] == 'abcdefghijklmnopqrstuvwxyz'
        assert data['query']['required_letter'] == 'a'
    
    def test_search_no_results(self, client):
        """Test search that returns no results."""
        response = client.get('/api/search', query_string={
            'allowed_letters': 'xyz',
            'required_letter': 'x',
            'min_length': '4'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['words'] == []
        assert data['count'] == 0
    
    def test_search_results_sorted(self, client):
        """Test that search results are properly sorted."""
        response = client.get('/api/search', query_string={
            'allowed_letters': 'abcdefghijklmnopqrstuvwxyz',
            'required_letter': 'a',
            'min_length': '4'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        if len(data['words']) > 1:
            # Check that words are sorted by length (desc) then alphabetically
            for i in range(len(data['words']) - 1):
                current_len = len(data['words'][i])
                next_len = len(data['words'][i + 1])
                
                # Either current is longer, or same length and alphabetically before/equal
                assert current_len >= next_len
                if current_len == next_len:
                    assert data['words'][i] <= data['words'][i + 1]
