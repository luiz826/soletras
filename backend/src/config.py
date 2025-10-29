"""
Configuration settings for the Brazilian Word Search API.
"""

import os


class Config:
    """Base configuration class."""
    
    # Flask settings
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # Word source configuration
    # Can be a single source (string) or multiple sources (list)
    # Environment variable WORD_SOURCES can be comma-separated URLs/paths
    WORD_SOURCES = os.getenv('WORD_SOURCES', None)
    
    if WORD_SOURCES:
        # Split by comma and strip whitespace
        WORD_SOURCES = [s.strip() for s in WORD_SOURCES.split(',') if s.strip()]
    else:
        # Default word sources - multiple dictionaries for comprehensive coverage
        WORD_SOURCES = [
            'https://www.ime.usp.br/~pf/dicios/br-sem-acentos.txt',
            'http://200.17.137.109:8081/novobsi/Members/cicerog/disciplinas/introducao-a-programacao/arquivos-2015-2/algoritmos/Lista-de-Palavras.txt',
            'https://cgit.freedesktop.org/libreoffice/dictionaries/plain/pt_BR/pt_BR.dic'
        ]
    
    # Legacy support - single source (deprecated but maintained for compatibility)
    WORD_SOURCE = WORD_SOURCES[0] if isinstance(WORD_SOURCES, list) else WORD_SOURCES
    
    # API metadata
    API_NAME = 'Brazilian Word Search API'
    API_VERSION = '1.0.0'
    
    # Request validation
    MIN_WORD_LENGTH = 4
    MAX_WORD_LENGTH = 25
    
    # Word filtering options
    FILTER_PLURALS = os.getenv('FILTER_PLURALS', 'True').lower() == 'true'
    FILTER_CONJUGATED_VERBS = os.getenv('FILTER_CONJUGATED_VERBS', 'True').lower() == 'true'
    USE_SPACY_FILTER = os.getenv('USE_SPACY_FILTER', 'True').lower() == 'true'
    
    # Cache configuration
    FILTER_CACHE_SIZE = int(os.getenv('FILTER_CACHE_SIZE', '10'))


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """
    Get configuration based on environment.
    
    Args:
        env: Environment name ('development', 'production', or None for default)
    
    Returns:
        Configuration class
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'default')
    
    return config.get(env, config['default'])
