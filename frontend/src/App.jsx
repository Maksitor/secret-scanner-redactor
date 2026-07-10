import { useState } from 'react'
import './App.css'

function App() {
  const [text, setText] = useState('')
  const [findings, setFindings] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleScan = async () => {
    if (!text.trim()) return
    setLoading(true)
    setError('')
    try {
      const response = await fetch('http://127.0.0.1:8000/scan', {
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

  // Kreiraj maskiranu verziju teksta
  const maskText = () => {
    if (findings.length === 0) return text
    let result = text
    // Slažemo opadajuće po poziciji da zamena ne poremeti indekse
    const sorted = [...findings].sort((a, b) => b.start - a.start)
    for (const f of sorted) {
      const before = result.substring(0, f.start)
      const after = result.substring(f.end)
      result = before + '[REDACTED]' + after
    }
    return result
  }

  // Preuzimanje očišćenog teksta kao .txt fajl
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

  return (
    <div className="app-container">
      <h1>🔍 Secret Scanner & Redactor</h1>
      <p>Pronađi i maskiraj API ključeve, lozinke, e‑mailove i druge osetljive podatke.</p>

      <textarea
        rows={8}
        placeholder="Unesite tekst koji želite da skenirate..."
        value={text}
        onChange={e => setText(e.target.value)}
      />

      <div className="button-group">
        <button onClick={handleScan} disabled={loading}>
          {loading ? 'Skeniram...' : 'Skeniraj'}
        </button>
        <button onClick={downloadClean} disabled={findings.length === 0}>
          Preuzmi očišćeni tekst
        </button>
      </div>

      {error && <div className="error">Greška: {error}</div>}

      {findings.length > 0 && (
        <>
          <h2>Rezultati</h2>
          <div className="results">
            <div className="highlighted-text">
              {maskText().split('[REDACTED]').reduce((acc, part, i) => {
                if (i === 0) return [part]
                return [...acc, <mark key={i}>[REDACTED]</mark>, part]
              }, [])}
            </div>

            <table>
              <thead>
                <tr>
                  <th>Tip</th>
                  <th>Vrednost</th>
                  <th>Pozicija</th>
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
        </>
      )}
    </div>
  )
}

export default App