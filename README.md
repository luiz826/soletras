# 🔤 Soletras

Brazilian Portuguese Word Search Game - A full-stack application for word puzzles and games.

## 📁 Project Structure

```
soletras/
├── backend/           # Flask REST API
│   ├── src/          # Source code
│   ├── tests/        # Test suite (61 tests, 88% coverage)
│   ├── app.py        # Entry point
│   └── README.md     # Backend documentation
├── frontend/         # React + Vite frontend
│   ├── src/         # React components
│   ├── public/      # Static assets
│   └── README.md    # Frontend documentation
└── README.md        # This file
```

## 🚀 Quick Start

### Backend (Flask API)

```bash
cd backend

# Install dependencies
uv pip install -r requirements.txt

# Run server (http://localhost:5000)
uv run python app.py

# Run tests
uv run pytest tests
```

### Frontend (React)

```bash
cd frontend

# Install dependencies
npm install

# Run dev server (http://localhost:3000)
npm run dev
```

## 🎮 Features

### Backend
- 🔍 Fast word search with 253,989 Brazilian Portuguese words
- 🎯 Filter by allowed letters, required letters, and length
- 🧪 Comprehensive test suite (61 tests, 88% coverage)
- 🌐 CORS-enabled REST API
- ⚡ Optimized search algorithm

### Frontend
- 🎨 Modern React 18 + Vite
- 🌙 Dark mode support
- 📱 Responsive design
- 🔌 Real-time API integration
- ✨ Clean, customizable template

## 🔌 API Endpoints

### Search Words
```http
GET /api/search?allowed_letters=abc&required_letter=a&min_length=4&max_length=10
```

### Health Check
```http
GET /api/health
```

### Word Sources Info
```http
GET /api/sources
```

## 🛠️ Tech Stack

**Backend:**
- Python 3.13
- Flask 2.3.3
- pytest (testing)
- uv (package management)

**Frontend:**
- React 18
- Vite 6
- CSS Variables (theming)

## 📖 Documentation

- [Backend Documentation](backend/README.md)
- [Frontend Documentation](frontend/README.md)

## 🎨 Next Steps

1. Design the UI in Figma
2. Customize frontend styles
3. Add game features (scoring, hints, timer)
4. Deploy to production

## 🧪 Testing

```bash
# Backend tests
cd backend && uv run pytest tests --cov=src

# All 61 tests passing ✅
# Coverage: 88%
```

## 🤝 Contributing

Contributions are welcome! The project follows clean architecture principles with:
- Separation of concerns
- Dependency injection
- Comprehensive testing
- Professional code organization

## 📝 License

Open source and available for educational and commercial use.

---

Made with ❤️ for Brazilian Portuguese word enthusiasts
