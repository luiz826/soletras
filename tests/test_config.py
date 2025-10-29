"""
Configuration tests.
"""

import pytest
import os
from src.config import Config, DevelopmentConfig, ProductionConfig, get_config


class TestConfig:
    """Test suite for configuration classes."""
    
    def test_base_config_defaults(self):
        """Test base configuration defaults."""
        config = Config()
        
        assert config.API_NAME == 'Brazilian Word Search API'
        assert config.API_VERSION == '1.0.0'
        assert config.MIN_WORD_LENGTH == 4
        assert config.MAX_WORD_LENGTH == 25
        assert config.HOST == '0.0.0.0'
        assert config.PORT == 5000
    
    def test_development_config(self):
        """Test development configuration."""
        config = DevelopmentConfig()
        
        assert config.DEBUG is True
    
    def test_production_config(self):
        """Test production configuration."""
        config = ProductionConfig()
        
        assert config.DEBUG is False
    
    def test_get_config_development(self):
        """Test getting development configuration."""
        config = get_config('development')
        
        assert config == DevelopmentConfig
    
    def test_get_config_production(self):
        """Test getting production configuration."""
        config = get_config('production')
        
        assert config == ProductionConfig
    
    def test_get_config_default(self):
        """Test getting default configuration."""
        config = get_config()
        
        assert config == DevelopmentConfig
    
    def test_get_config_invalid(self):
        """Test getting configuration with invalid environment."""
        config = get_config('invalid')
        
        # Should fall back to default
        assert config == DevelopmentConfig
    
    def test_config_with_environment_variables(self):
        """Test configuration with environment variables."""
        # Import to reload config
        import importlib
        from src import config as config_module
        
        # Save original values
        original_debug = os.environ.get('FLASK_DEBUG')
        original_host = os.environ.get('FLASK_HOST')
        original_port = os.environ.get('FLASK_PORT')
        original_sources = os.environ.get('WORD_SOURCES')
        
        # Set environment variables
        os.environ['FLASK_DEBUG'] = 'false'  # Lowercase for proper parsing
        os.environ['FLASK_HOST'] = '127.0.0.1'
        os.environ['FLASK_PORT'] = '8000'
        os.environ['WORD_SOURCES'] = 'custom_words.txt'
        
        # Reload config module to pick up new environment variables
        importlib.reload(config_module)
        
        # Create new config instance
        test_config = config_module.Config()
        
        assert test_config.DEBUG is False
        assert test_config.HOST == '127.0.0.1'
        assert test_config.PORT == 8000
        assert test_config.WORD_SOURCES == ['custom_words.txt']
        assert test_config.WORD_SOURCE == 'custom_words.txt'  # Legacy support
        
        # Cleanup - restore original values
        for key, value in [
            ('FLASK_DEBUG', original_debug),
            ('FLASK_HOST', original_host),
            ('FLASK_PORT', original_port),
            ('WORD_SOURCES', original_sources)
        ]:
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        
        # Reload config module again to restore original state
        importlib.reload(config_module)
