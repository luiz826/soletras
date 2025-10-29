"""
API route handlers.
Defines all API endpoints and their logic.
"""

from flask import Blueprint, request, jsonify
from typing import Tuple
import logging

from .validators import RequestValidator, ValidationError
from .search_engine import SearchEngine

logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)

# Global references (will be set by create_app)
search_engine: SearchEngine = None
validator: RequestValidator = None
config = None
word_loader = None  # Add word_loader reference


def init_routes(engine: SearchEngine, req_validator: RequestValidator, app_config, loader=None):
    """
    Initialize routes with dependencies.
    
    Args:
        engine: SearchEngine instance
        req_validator: RequestValidator instance
        app_config: Application configuration
        loader: WordLoader instance (optional)
    """
    global search_engine, validator, config, word_loader
    search_engine = engine
    validator = req_validator
    config = app_config
    word_loader = loader


@api_bp.route('/search', methods=['GET'])
def search_words():
    """
    Search for words matching the given criteria.
    
    Query Parameters:
    - allowed_letters (required): String of all valid letters
    - required_letter (required): Single letter that must be in the word
    - min_length (required): Minimum number of letters in the word
    - max_length (optional): Maximum number of letters in the word
    
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
        
        # Perform search
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
            'min_length': params.min_length
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


@api_bp.route('/', methods=['GET'])
def index():
    """Root endpoint with API information."""
    return jsonify({
        'name': config.API_NAME if config else 'Brazilian Word Search API',
        'version': config.API_VERSION if config else '1.0.0',
        'endpoints': {
            '/api/search': 'Search for words (GET)',
            '/api/health': 'Health check (GET)',
            '/api/sources': 'List word sources (GET)'
        },
        'words_loaded': len(search_engine.word_list) if search_engine else 0
    }), 200
