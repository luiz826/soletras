"""
API route handlers.
Defines all API endpoints and their logic.
"""

from flask import Blueprint, request, jsonify
from typing import Tuple
import logging

from .validators import RequestValidator, ValidationError
from .search_engine import SearchEngine
from .cache import FilterCache

logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)

# Global references (will be set by create_app)
search_engine: SearchEngine = None
validator: RequestValidator = None
config = None
word_loader = None
filter_cache: FilterCache = None  # Cache for filtered word lists


def init_routes(engine: SearchEngine, req_validator: RequestValidator, app_config, loader=None):
    """
    Initialize routes with dependencies.
    
    Args:
        engine: SearchEngine instance
        req_validator: RequestValidator instance
        app_config: Application configuration
        loader: WordLoader instance (optional)
    """
    global search_engine, validator, config, word_loader, filter_cache
    search_engine = engine
    validator = req_validator
    config = app_config
    word_loader = loader
    
    # Initialize cache
    cache_size = getattr(app_config, 'FILTER_CACHE_SIZE', 10)
    filter_cache = FilterCache(max_size=cache_size)
    logger.info(f"Filter cache initialized with size {cache_size}")


@api_bp.route('/search', methods=['GET'])
def search_words():
    """
    Search for words matching the given criteria.
    
    Query Parameters:
    - allowed_letters (required): String of all valid letters
    - required_letter (required): Single letter that must be in the word
    - min_length (required): Minimum number of letters in the word
    - max_length (optional): Maximum number of letters in the word
    - filter_plurals (optional): Remove plural words (true/false, default: false)
    - filter_conjugated_verbs (optional): Remove conjugated verbs (true/false, default: false)
    
    Returns:
    JSON object with matching words, count, and query parameters
    """
    try:
        # Extract and validate parameters
        params = validator.validate_search_params(
            allowed_letters=request.args.get('allowed_letters'),
            required_letter=request.args.get('required_letter'),
            min_length=request.args.get('min_length'),
            max_length=request.args.get('max_length')
        )
        
        # Get filter parameters
        filter_plurals = request.args.get('filter_plurals', 'false').lower() == 'true'
        filter_conjugated_verbs = request.args.get('filter_conjugated_verbs', 'false').lower() == 'true'
        import pdb
        pdb.set_trace()
        # Apply filters if requested and word_loader is available
        if (filter_plurals or filter_conjugated_verbs) and word_loader:
            # Try to get from cache first
            cached_words = filter_cache.get(
                filter_plurals=filter_plurals,
                filter_conjugated_verbs=filter_conjugated_verbs,
                original_word_count=len(search_engine.word_list)
            )
            
            if cached_words is not None:
                # Cache hit - use cached filtered words
                logger.debug(f"Using cached filtered words ({len(cached_words)} words)")
                temp_engine = SearchEngine(cached_words)
            else:
                # Cache miss - apply filters and cache result
                logger.debug("Cache miss - applying filters with SpaCy")
                
                from .word_loader import WordLoader
                
                # Create a copy of the word loader to avoid modifying the original
                temp_loader = WordLoader([])
                temp_loader._words = list(search_engine.word_list)
                
                # Apply filters
                temp_loader.filter_words(
                    remove_plurals=filter_plurals,
                    remove_conjugated_verbs=filter_conjugated_verbs,
                    use_spacy=True
                )
                
                # Cache the filtered words
                filter_cache.set(
                    filter_plurals=filter_plurals,
                    filter_conjugated_verbs=filter_conjugated_verbs,
                    original_word_count=len(search_engine.word_list),
                    filtered_words=temp_loader.words
                )
                
                # Create temporary search engine with filtered words
                temp_engine = SearchEngine(temp_loader.words)
            
            # Perform search with filtered engine
            results = temp_engine.search(
                allowed_letters=params.allowed_letters,
                required_letter=params.required_letter,
                min_length=params.min_length,
                max_length=params.max_length
            )
        else:
            # Perform search with original engine (no filters)
            results = search_engine.search(
                allowed_letters=params.allowed_letters,
                required_letter=params.required_letter,
                min_length=params.min_length,
                max_length=params.max_length
            )
        
        # Build query response
        query_response = {
            'allowed_letters': params.allowed_letters,
            'required_letter': params.required_letter,
            'min_length': params.min_length,
            'filter_plurals': filter_plurals,
            'filter_conjugated_verbs': filter_conjugated_verbs
        }
        if params.max_length is not None:
            query_response['max_length'] = params.max_length
        
        # Return response
        return jsonify({
            'words': results,
            'count': len(results),
            'query': query_response
        }), 200
    
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        logger.error(f"Unexpected error in search: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({
        'status': 'ok',
        'words_loaded': len(search_engine.word_list) if search_engine else 0
    }), 200


@api_bp.route('/sources', methods=['GET'])
def list_sources():
    """
    Get information about word sources.
    
    Returns statistics about each configured word source including
    success/failure status and word counts.
    """
    if not word_loader:
        return jsonify({
            'error': 'Word loader not initialized'
        }), 500
    
    sources_info = []
    
    if hasattr(word_loader, 'sources'):
        for source in word_loader.sources:
            info = {
                'url': source,
                'name': source.split('/')[-1] if '/' in source else source
            }
            
            # Add stats if available
            if hasattr(word_loader, 'source_stats') and source in word_loader.source_stats:
                stats = word_loader.source_stats[source]
                info.update({
                    'status': stats['status'],
                    'words_loaded': stats['words_loaded']
                })
                if 'error' in stats:
                    info['error'] = stats['error']
            
            sources_info.append(info)
    
    return jsonify({
        'total_sources': len(sources_info),
        'total_unique_words': len(search_engine.word_list) if search_engine else 0,
        'sources': sources_info
    }), 200


@api_bp.route('/cache/stats', methods=['GET'])
def cache_stats():
    """
    Get cache statistics.
    
    Returns information about cache usage, hit rate, and stored entries.
    """
    if not filter_cache:
        return jsonify({
            'error': 'Cache not initialized'
        }), 500
    
    return jsonify(filter_cache.stats), 200


@api_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """
    Clear the filter cache.
    
    Useful for debugging or if word list is updated.
    """
    if not filter_cache:
        return jsonify({
            'error': 'Cache not initialized'
        }), 500
    
    old_size = filter_cache.size
    filter_cache.clear()
    
    return jsonify({
        'message': 'Cache cleared successfully',
        'entries_removed': old_size
    }), 200


@api_bp.route('/', methods=['GET'])
def index():
    """Root endpoint with API information."""
    return jsonify({
        'name': config.API_NAME if config else 'Brazilian Word Search API',
        'version': config.API_VERSION if config else '1.0.0',
        'endpoints': {
            '/api/search': 'Search for words (GET)',
            '/api/health': 'Health check (GET)',
            '/api/sources': 'List word sources (GET)',
            '/api/cache/stats': 'Get cache statistics (GET)',
            '/api/cache/clear': 'Clear cache (POST)'
        },
        'words_loaded': len(search_engine.word_list) if search_engine else 0,
        'cache_enabled': filter_cache is not None
    }), 200
