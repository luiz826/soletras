import { useState } from 'react'
import './App.css'

function App() {
  const [allowedLetters, setAllowedLetters] = useState('')
  const [requiredLetter, setRequiredLetter] = useState('')
  const [minLength, setMinLength] = useState(4)
  const [maxLength, setMaxLength] = useState('')
  const [filterPlurals, setFilterPlurals] = useState(true)
  const [filterConjugatedVerbs, setFilterConjugatedVerbs] = useState(true)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSearch = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams({
        allowed_letters: allowedLetters.toLowerCase(),
        required_letter: requiredLetter.toLowerCase(),
        min_length: minLength,
        filter_plurals: filterPlurals,
        filter_conjugated_verbs: filterConjugatedVerbs,
      })

      if (maxLength) {
        params.append('max_length', maxLength)
      }

      const response = await fetch(`/api/search?${params}`)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to search')
      }

      setResults(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🔤 Soletras</h1>
        <p>Brazilian Word Search Game</p>
      </header>

      <main className="app-main">
        <form onSubmit={handleSearch} className="search-form">
          <div className="form-group">
            <label htmlFor="allowed-letters">
              Allowed Letters *
            </label>
            <input
              id="allowed-letters"
              type="text"
              value={allowedLetters}
              onChange={(e) => setAllowedLetters(e.target.value)}
              placeholder="abcdefg"
              required
              className="input"
            />
            <small>Letters you can use to form words</small>
          </div>

          <div className="form-group">
            <label htmlFor="required-letter">
              Required Letter *
            </label>
            <input
              id="required-letter"
              type="text"
              value={requiredLetter}
              onChange={(e) => setRequiredLetter(e.target.value)}
              placeholder="a"
              maxLength={1}
              required
              className="input"
            />
            <small>Letter that must appear in all words</small>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="min-length">
                Min Length *
              </label>
              <input
                id="min-length"
                type="number"
                value={minLength}
                onChange={(e) => setMinLength(e.target.value)}
                min={4}
                max={20}
                required
                className="input"
              />
            </div>

            <div className="form-group">
              <label htmlFor="max-length">
                Max Length
              </label>
              <input
                id="max-length"
                type="number"
                value={maxLength}
                onChange={(e) => setMaxLength(e.target.value)}
                min={4}
                max={20}
                placeholder="Optional"
                className="input"
              />
            </div>
          </div>

          <div className="filter-options">
            <h3>🧠 Filtros NLP (SpaCy)</h3>
            <p className="filter-description">
              Use análise linguística para filtrar palavras
            </p>
            
            <div className="checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={filterPlurals}
                  onChange={(e) => setFilterPlurals(e.target.checked)}
                  className="checkbox"
                />
                <span className="checkbox-text">
                  <strong>Remover Plurais</strong>
                  <small>Mantém apenas singular (ex: casa ✓, casas ✗)</small>
                </span>
              </label>

              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={filterConjugatedVerbs}
                  onChange={(e) => setFilterConjugatedVerbs(e.target.checked)}
                  className="checkbox"
                />
                <span className="checkbox-text">
                  <strong>Remover Verbos Conjugados</strong>
                  <small>Mantém apenas infinitivos (ex: amar ✓, amava ✗)</small>
                </span>
              </label>
            </div>
          </div>

          <button 
            type="submit" 
            className="btn-primary"
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Search Words'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}

        {results && (
          <div className="results">
            <div className="results-header">
              <h2>Found {results.count} words</h2>
              <div className="results-info">
                <span>Letters: {results.query.allowed_letters}</span>
                <span>Required: {results.query.required_letter}</span>
                <span>Length: {results.query.min_length}{results.query.max_length ? `-${results.query.max_length}` : '+'}</span>
                {results.query.filter_plurals && (
                  <span className="filter-badge">🚫 Plurals</span>
                )}
                {results.query.filter_conjugated_verbs && (
                  <span className="filter-badge">🚫 Conjugated</span>
                )}
              </div>
            </div>

            <div className="words-grid">
              {results.words.map((word, index) => (
                <div key={index} className="word-card">
                  {word}
                </div>
              ))}
            </div>

            {results.count === 0 && (
              <p className="no-results">
                No words found with these criteria. Try different letters or disable filters!
              </p>
            )}
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>Powered by Brazilian Portuguese word database</p>
      </footer>
    </div>
  )
}

export default App
