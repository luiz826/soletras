# Soletras - Backend API

Flask-based REST API for Brazilian Portuguese word search with advanced NLP filtering.

## ✨ Features

- 🔍 **Smart Word Search**: Find words based on allowed/required letters
- 🧠 **NLP Filtering with SpaCy**: Remove plurals and conjugated verbs using linguistic analysis
- ⚡ **Intelligent Cache**: LRU cache for filtered word lists (up to 200x faster)
- 📚 **Large Database**: 550,633+ unique Portuguese words
- 🚀 **High Performance**: Optimized batch processing and caching
- 🧪 **Well Tested**: 61+ tests with 88% coverage
- 🔧 **Flexible Configuration**: Environment variables and code-based config

## �🚀 Quick Start

```bash
# Install dependencies with uv
uv pip install -r requirements.txt

# Download SpaCy Portuguese model (for filtering)
# Option 1: Via spacy download (may fail with rate limits)
uv run python -m spacy download pt_core_news_sm

# Option 2: Direct install from GitHub (recommended with uv)
uv pip install https://github.com/explosion/spacy-models/releases/download/pt_core_news_sm-3.8.0/pt_core_news_sm-3.8.0-py3-none-any.whl

# Run the server
uv run python app.py

# Run tests
uv run pytest tests

# Run tests with coverage
uv run pytest tests --cov=src --cov-report=html
```

## 🆕 Word Filtering (NEW!)

The backend now includes **advanced word filtering** using SpaCy NLP:

- ✅ **Remove Plurals**: Keeps only singular forms (`casa` ✓, `casas` ✗)
- ✅ **Remove Conjugated Verbs**: Keeps only infinitives (`amar` ✓, `amava` ✗)
- ✅ **Smart Analysis**: Uses morphological analysis for accuracy
- ✅ **Fallback Available**: Rule-based filtering if SpaCy unavailable

## 🔧 Configuration

### Environment Variables

```bash
# Filtering options
export FILTER_PLURALS=True
export FILTER_CONJUGATED_VERBS=True
export USE_SPACY_FILTER=True

# Cache settings
export FILTER_CACHE_SIZE=10  # Number of filter combinations to cache

# Run server
python app.py
```

### Performance

- **Without Cache**: 2-5 seconds for 100k words (SpaCy processing)
- **With Cache Hit**: 10-50ms (200x faster!)
- **Cache Memory**: ~6MB per 100k words cached

See **[CACHE_SYSTEM.md](CACHE_SYSTEM.md)** for complete cache documentation.

### Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick installation guide
- **[FILTER_GUIDE.md](FILTER_GUIDE.md)** - Complete filtering guide
- **[SPACY_IMPLEMENTATION.md](SPACY_IMPLEMENTATION.md)** - Technical documentation
- **[CACHE_SYSTEM.md](CACHE_SYSTEM.md)** - Cache system documentation
- **[example_filter_usage.py](example_filter_usage.py)** - Usage examples

## 📁 Structure

```
backend/
├── src/
│   ├── app.py              # Application factory
│   ├── config.py           # Configuration
│   ├── routes.py           # API endpoints
│   ├── word_loader.py      # Word loading logic
│   ├── search_engine.py    # Search algorithm
│   └── validators.py       # Request validation
├── tests/                  # Test suite (61 tests, 88% coverage)
├── app.py                  # Entry point
└── requirements.txt        # Dependencies
```

## 🔌 API Endpoints

### Search Words

```http
GET /api/search?allowed_letters=abc&required_letter=a&min_length=4&max_length=10&filter_plurals=true&filter_conjugated_verbs=true
```

### Cache Management

**Get Cache Statistics**
```http
GET /api/cache/stats
```

Returns:
```json
{
  "cache_size": 3,
  "max_size": 10,
  "hits": 15,
  "misses": 3,
  "hit_rate": 0.833,
  "entries": [...]
}
```

**Clear Cache**
```http
POST /api/cache/clear
```

### Health Check

```http
GET /api/health
```

### Word Sources Info

```http
GET /api/sources
```

## 📊 Word Database

Currently loads **550,633+ unique words** from:
- IME-USP Brazilian Portuguese dictionary
- BSI word list
- LibreOffice pt_BR dictionary (.dic format)

## 🧪 Testing

Run the comprehensive test suite:
```bash
uv run pytest tests -v
```

All 61 tests passing ✅
