"""
Application entry point.
Run this file to start the Flask development server.
"""

from src.app import create_app
from src.config import get_config

if __name__ == '__main__':
    # Create application
    app = create_app()
    
    # Get configuration
    config = get_config()
    
    # Print startup information
    print("\n" + "="*60)
    print(f"🚀 {config.API_NAME} v{config.API_VERSION}")
    print("="*60)
    print(f"Environment: {config.__class__.__name__}")
    print(f"Server running on http://{config.HOST}:{config.PORT}")
    print(f"Word source: {config.WORD_SOURCE}")
    print("\nEndpoints:")
    print("  GET /api/search        - Search for words")
    print("  GET /api/health        - Health check")
    print("  GET /                  - API information")
    print("\nPress CTRL+C to quit")
    print("="*60 + "\n")
    
    # Run development server
    app.run(
        debug=config.DEBUG,
        host=config.HOST,
        port=config.PORT
    )
