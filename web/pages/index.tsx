import { useState } from 'react';

export default function Home() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleScore = async () => {
    if (!text.trim() || text.length < 10) {
      setError('Text must be at least 10 characters');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/score', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          options: {
            include_breakdown: true,
          },
        }),
      });

      if (!response.ok) {
        throw new Error('Scoring failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem' }}>
      <h1>🧠 TraceNeuro</h1>
      <p>Cognitive Authenticity Engine</p>

      <div style={{ marginTop: '2rem' }}>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste or type text to analyze..."
          style={{
            width: '100%',
            minHeight: '200px',
            padding: '1rem',
            fontSize: '1rem',
            border: '1px solid #ccc',
            borderRadius: '4px',
          }}
        />
      </div>

      <button
        onClick={handleScore}
        disabled={loading || text.length < 10}
        style={{
          marginTop: '1rem',
          padding: '0.75rem 2rem',
          fontSize: '1rem',
          backgroundColor: '#0070f3',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: loading ? 'not-allowed' : 'pointer',
        }}
      >
        {loading ? 'Analyzing...' : 'Analyze Text'}
      </button>

      {error && (
        <div
          style={{
            marginTop: '1rem',
            padding: '1rem',
            backgroundColor: '#fee',
            color: '#c00',
            borderRadius: '4px',
          }}
        >
          Error: {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: '2rem' }}>
          <h2>Results</h2>
          <div
            style={{
              padding: '1rem',
              backgroundColor: '#f5f5f5',
              borderRadius: '4px',
            }}
          >
            <h3>HumanScore™: {(result.humanscore * 100).toFixed(2)}%</h3>
            <div style={{ marginTop: '1rem' }}>
              <h4>Breakdown:</h4>
              <ul>
                {Object.entries(result.breakdown).map(([key, value]) => (
                  <li key={key}>
                    <strong>{key}:</strong> {(Number(value) * 100).toFixed(2)}%
                  </li>
                ))}
              </ul>
            </div>
            <div style={{ marginTop: '1rem' }}>
              <h4>Metadata:</h4>
              <ul>
                <li>Sentences: {result.metadata.sentence_count}</li>
                <li>Tokens: {result.metadata.token_count}</li>
                <li>Characters: {result.metadata.char_count}</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

