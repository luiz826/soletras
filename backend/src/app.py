"""
Flask application factory.
Creates and configures the Flask application.
"""

from flask import Flask
from flask_cors import CORS
import logging
from typing import Optional

from .config import get_config
from .word_loader import WordLoader
from .search_engine import SearchEngine
from .validators import RequestValidator
from .routes import api_bp, init_routes


def setup_logging(debug: bool = False) -> None:
    """
    Configure application logging.
    
    Args:
        debug: Enable debug logging
    """
    level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def create_app(env: Optional[str] = None) -> Flask:
    """
    Application factory function.
    
    Args:
        env: Environment name ('development', 'production', or None)
    
    Returns:
        Configured Flask application
    """
    # Get configuration
    config_class = get_config(env)
    
    # Setup logging
    setup_logging(config_class.DEBUG)
    logger = logging.getLogger(__name__)
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    logger.info("CORS enabled for all routes")
    
    # Load words
    logger.info("Initializing word loader...")
    word_loader = WordLoader(config_class.WORD_SOURCES)
    
    try:
        word_loader.load()
        logger.info(f"Loaded {word_loader.word_count} unique words from {len(config_class.WORD_SOURCES)} source(s)")
        
        # Log source statistics
        if hasattr(word_loader, 'source_stats'):
            for source, stats in word_loader.source_stats.items():
                source_name = source.split('/')[-1] if '/' in source else source
                if stats['status'] == 'success':
                    logger.debug(f"  - {source_name}: {stats['words_loaded']} words")
        
        # Apply word filters if enabled
        if hasattr(config_class, 'FILTER_PLURALS') or hasattr(config_class, 'FILTER_CONJUGATED_VERBS'):
            filter_plurals = getattr(config_class, 'FILTER_PLURALS', False)
            filter_verbs = getattr(config_class, 'FILTER_CONJUGATED_VERBS', False)
            use_spacy = getattr(config_class, 'USE_SPACY_FILTER', True)
            
            if filter_plurals or filter_verbs:
                logger.info("Applying word filters...")
                removed = word_loader.filter_words(
                    remove_plurals=filter_plurals,
                    remove_conjugated_verbs=filter_verbs,
                    use_spacy=use_spacy
                )
                logger.info(f"Filtered {removed} words. {word_loader.word_count} words remaining.")
    except Exception as e:
        logger.error(f"Failed to load words: {e}")
        logger.warning("Starting with empty word list")
    
    # Initialize search engine
    search_engine = SearchEngine(word_loader.words)
    logger.info("Search engine initialized")
    
    # Initialize validator
    validator = RequestValidator(
        min_word_length=config_class.MIN_WORD_LENGTH,
        max_word_length=config_class.MAX_WORD_LENGTH
    )
    logger.info("Request validator initialized")
    
    # Initialize routes with dependencies
    init_routes(search_engine, validator, config_class, word_loader)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register root routes separately
    @app.route('/', methods=['GET'])
    def root_index():
        """Root endpoint with API information."""
        from .routes import index
        return index()
    
    logger.info("Routes registered")
    
    logger.info(f"Application created successfully ({config_class.__name__})")
    
    return app
