# Brazilian Word Search API 🇧🇷

A Flask-based REST API for searching Brazilian Portuguese words based on letter constraints. Perfect for word games, puzzles, and educational applications.

## Features

- 🔍 Fast in-memory word searching
- 🎯 Filter by allowed letters, required letters, and minimum length
- 🌐 CORS-enabled for frontend integration
- 📝 UTF-8 support for Portuguese characters (á, é, í, ó, ú, ã, õ, ç)
- ⚡ Optimized search algorithm using set operations

## Installation

### Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) - Ultra-fast Python package installer (recommended)

### Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd /Users/luizfernando/dev/soletras
   ```

2. **Install dependencies using uv (recommended):**
   ```bash
   # uv automatically manages the virtual environment
   uv pip install flask flask-cors
   ```

   **Alternative: Using traditional pip:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Prepare your word list:**
   - Replace the sample `palavras.txt` with your comprehensive Brazilian Portuguese word list
   - Format: one word per line, lowercase, no punctuation
   - Ensure UTF-8 encoding

## Running the Server

**Using uv (recommended):**
```bash
uv run python app.py
```

**Or with traditional Python:**
```bash
python app.py
```

The server will start on `http://localhost:5000`

### Environment Variables

You can customize the application using environment variables:

```bash
# Set environment (development/production)
export FLASK_ENV=production

# Custom word source
export WORD_SOURCE=https://example.com/custom-words.txt

# Custom host and port
export FLASK_HOST=127.0.0.1
export FLASK_PORT=8000

# Run with custom settings
uv run python app.py
```

## API Endpoints

### 1. Search Words

**Endpoint:** `GET /api/search`

**Query Parameters:**
- `allowed_letters` (required): String of all valid letters (e.g., "abcdefg")
- `required_letter` (required): Single letter that must appear in the word (e.g., "e")
- `min_length` (required): Minimum number of letters in the word (e.g., 4)
- `max_length` (optional): Maximum number of letters in the word (e.g., 8)

**Example Request:**
```bash
curl "http://localhost:5000/api/search?allowed_letters=abcdefghijklm&required_letter=a&min_length=4&max_length=6"
```
curl "http://localhost:5000/api/search?allowed_letters=abcdefghijklm&required_letter=a&min_length=4"
```

**Example Response:**
```json
{
  "words": ["amora", "cama", "casa"],
  "count": 3,
  "query": {
    "allowed_letters": "abcdefghijklm",
    "required_letter": "a",
    "min_length": 4,
    "max_length": 6
  }
}
```

**Note:** When `max_length` is not provided, it won't appear in the query response.

### 2. Health Check

**Endpoint:** `GET /api/health`

**Example Response:**
```json
{
  "status": "ok",
  "words_loaded": 50
}
```

### 3. API Info

**Endpoint:** `GET /`

**Example Response:**
```json
{
  "name": "Brazilian Word Search API",
  "version": "1.0.0",
  "endpoints": {
    "/api/search": "Search for words (GET)",
    "/api/health": "Health check (GET)"
  },
  "words_loaded": 50
}
```

## Algorithm Overview

The search algorithm applies three filters in sequence:

1. **Length Filter:** Check if word length ≥ `min_length`
2. **Required Letter Filter:** Check if `required_letter` is in the word
3. **Allowed Letters Filter:** Check if all letters in the word are in `allowed_letters`

The algorithm uses Python sets for O(1) lookup time, making searches very efficient even with large word lists.

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- **400 Bad Request:** Missing or invalid parameters
- **200 OK:** Successful search (even if no words found)

Example error response:
```json
{
  "error": "Missing required parameter: allowed_letters"
}
```

## Testing

## Testing

The project includes comprehensive test coverage using pytest.

### Run Tests

```bash
# Install test dependencies
uv pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_search_engine.py
```

### Test Structure

```
tests/
├── conftest.py              # Pytest configuration
├── test_config.py           # Configuration tests
├── test_word_loader.py      # Word loader tests
├── test_search_engine.py    # Search engine tests
├── test_validators.py       # Validator tests
└── test_api.py              # API integration tests
```

For detailed testing documentation, see [TESTING.md](TESTING.md).

## Performance

- **Word Loading:** Once at startup (not per request)
- **Memory Usage:** ~500KB for 50,000 words
- **Search Time:** <100ms for typical queries
- **Optimization:** Set-based lookups provide O(1) complexity

## Project Structure

```
soletras/
├── src/                    # Source code package
│   ├── __init__.py        # Package initialization
│   ├── app.py             # Application factory
│   ├── config.py          # Configuration management
│   ├── word_loader.py     # Word list loading logic
│   ├── search_engine.py   # Core search algorithm
│   ├── validators.py      # Request validation
│   └── routes.py          # API route handlers
├── app.py                 # Application entry point
├── palavras.txt           # Brazilian Portuguese word list (optional)
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## Architecture

The application follows clean architecture principles with clear separation of concerns:

- **`config.py`**: Centralized configuration with environment support
- **`word_loader.py`**: Handles loading words from URL or file sources
- **`search_engine.py`**: Implements the core search algorithm
- **`validators.py`**: Validates and sanitizes request parameters
- **`routes.py`**: Defines API endpoints (thin controllers)
- **`app.py`**: Application factory with dependency injection

### Design Patterns Used

- **Factory Pattern**: `create_app()` function for application creation
- **Dependency Injection**: Components receive dependencies explicitly
- **Single Responsibility**: Each module has one clear purpose
- **Configuration Management**: Environment-based configuration

## Future Enhancements

- [ ] Add caching for repeated queries
- [ ] Implement word sorting options
- [ ] Add word definitions/meanings
- [ ] Rate limiting
- [ ] Database integration
- [ ] Docker containerization
- [ ] Production deployment configuration

## Troubleshooting

### "palavras.txt not found" warning

Make sure `palavras.txt` exists in the project root directory with your word list.

### CORS issues

The API has CORS enabled by default. If you still experience issues, check your frontend origin configuration.

### Port already in use

If port 5000 is in use, modify the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change to 5001
```

## License

This project is open source and available for educational and commercial use.

## Contributing

Contributions are welcome! Please ensure your code follows Python best practices and includes appropriate error handling.

---

Made with ❤️ for Brazilian Portuguese word enthusiasts
