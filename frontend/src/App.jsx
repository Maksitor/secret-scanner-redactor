import { useState, useEffect } from 'react'
import './App.css'

const DEMO_TEXT = `Log in using email: admin@company.com and password: SuperSecret123!
AWS Access Key: AKIAIOSFODNN7EXAMPLE
GitHub token: ghp_1234567890abcdefghijklmnopqrstuv
Contact: John Doe from Google visited Paris last week.`

function App() {
  const [text, setText] = useState('')
  const [findings, setFindings] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('darkMode') === 'true'
  })

  useEffect(() => {
    document.body.classList.toggle('dark', darkMode)
    localStorage.setItem('darkMode', darkMode)
  }, [darkMode])

  const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

  const handleScan = async () => {
    if (!text.trim()) return
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_URL}/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      })
      if (!response.ok) throw new Error('Server error')
      const data = await response.json()
      setFindings(data.findings || [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const maskText = () => {
    if (findings.length === 0) return text
    let result = text
    const sorted = [...findings].sort((a, b) => b.start - a.start)
    for (const f of sorted) {
      const before = result.substring(0, f.start)
      const after = result.substring(f.end)
      result = before + '[REDACTED]' + after
    }
    return result
  }

  const downloadClean = () => {
    const cleanText = maskText()
    const blob = new Blob([cleanText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'cleaned_text.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  const loadDemo = () => {
    setText(DEMO_TEXT)
    setFindings([])
  }

  return (
    <div className={`app-container ${darkMode ? 'dark' : ''}`}>
      <header className="app-header">
        <div className="title-group">
          <h1>Secret Scanner & Redactor</h1>
          <p className="subtitle">
            Find and redact API keys, passwords, email addresses, and other sensitive data.
          </p>
        </div>
        <button className="theme-toggle" onClick={() => setDarkMode(!darkMode)}>
          {darkMode ? 'Light Mode' : 'Dark Mode'}
        </button>
      </header>

      <section className="input-section card">
        <textarea
          rows={8}
          placeholder="Enter text to scan..."
          value={text}
          onChange={e => setText(e.target.value)}
        />

        <div className="button-group">
          <button onClick={handleScan} disabled={loading}>
            {loading ? 'Scanning...' : 'Scan'}
          </button>
          <button onClick={downloadClean} disabled={findings.length === 0}>
            Download Clean Text
          </button>
          <button className="demo-btn" onClick={loadDemo}>
            Load Demo Text
          </button>
        </div>

        {error && <div className="error">Error: {error}</div>}
      </section>

      {findings.length > 0 && (
        <section className="results-section">
          <h2>Results <span className="badge">{findings.length}</span></h2>

          <div className="card">
            <h3>Redacted Preview</h3>
            <div className="highlighted-text">
              {maskText().split('[REDACTED]').reduce((acc, part, i) => {
                if (i === 0) return [part]
                return [...acc, <mark key={i} title="Sensitive data">[REDACTED]</mark>, part]
              }, [])}
            </div>
          </div>

          <div className="card">
            <h3>Detected Items</h3>
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Value</th>
                    <th>Position</th>
                  </tr>
                </thead>
                <tbody>
                  {findings.map((f, i) => (
                    <tr key={i}>
                      <td>{f.type}</td>
                      <td><code>{f.value}</code></td>
                      <td>{f.start}-{f.end}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}

export default App