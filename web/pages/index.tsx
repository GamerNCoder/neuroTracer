import { useState, useEffect } from 'react';

interface MarkerScore {
  name: string;
  label: string;
  description: string;
  score: number;
}

interface HistoryItem {
  id: number;
  text_preview: string;
  humanscore: number;
  breakdown: Record<string, number>;
  created_at: string;
}

const MARKER_INFO: Record<string, { label: string; description: string }> = {
  drift: { label: 'Semantic Drift', description: 'Meaning changes across sentences' },
  cadence: { label: 'Cadence Variability', description: 'Irregularity in sentence pacing' },
  hedging: { label: 'Hedging Language', description: 'Uncertainty markers and hedging patterns' },
  metaphor: { label: 'Metaphor Rarity', description: 'Uniqueness of metaphors used' },
  coherence: { label: 'Coherence Breaks', description: 'Mid-thought direction changes' },
  stylometry: { label: 'Stylometric Fingerprint', description: 'Individual writing style patterns' },
};

const SAMPLE_TEXTS = {
  human: `I've been thinking about this problem for a while now, and honestly, I'm not entirely sure what the best approach is. Maybe we should try a different angle? It seems like the current method isn't quite working, but then again, I might be missing something obvious. What do you think? Sometimes the simplest solutions are the ones we overlook.`,
  
  ai: `The implementation of this solution requires a systematic approach that addresses multiple key considerations. First, we must analyze the core requirements and identify potential challenges. Second, we should develop a comprehensive strategy that accounts for various edge cases. Finally, we will implement the solution using best practices and ensure proper testing. This methodology ensures optimal results.`
};

export default function Home() {
  const [text, setText] = useState('');
  const [text2, setText2] = useState('');
  const [loading, setLoading] = useState(false);
  const [loading2, setLoading2] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [result2, setResult2] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [error2, setError2] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [comparisonMode, setComparisonMode] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [copied, setCopied] = useState(false);

  // Load history on mount
  useEffect(() => {
    loadHistory();
  }, []);

  // Apply dark mode
  useEffect(() => {
    if (darkMode) {
      document.documentElement.style.backgroundColor = '#111827';
    } else {
      document.documentElement.style.backgroundColor = '#f9fafb';
    }
  }, [darkMode]);

  const loadHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/history?limit=5');
      if (response.ok) {
        const data = await response.json();
        setHistory(data);
      }
    } catch (err) {
      // Silently fail - history is optional
    }
  };

  const handleScore = async (textToScore: string, isSecond = false) => {
    if (!textToScore.trim() || textToScore.length < 10) {
      if (isSecond) {
        setError2('Text must be at least 10 characters');
      } else {
        setError('Text must be at least 10 characters');
      }
      return;
    }

    if (isSecond) {
      setLoading2(true);
      setError2(null);
    } else {
      setLoading(true);
      setError(null);
    }

    try {
      const response = await fetch('http://localhost:8000/api/v1/score', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: textToScore,
          options: {
            include_breakdown: true,
          },
        }),
      });

      if (!response.ok) {
        throw new Error('Scoring failed');
      }

      const data = await response.json();
      if (isSecond) {
        setResult2(data);
      } else {
        setResult(data);
      }
      loadHistory(); // Refresh history
    } catch (err) {
      if (isSecond) {
        setError2(err instanceof Error ? err.message : 'An error occurred');
      } else {
        setError(err instanceof Error ? err.message : 'An error occurred');
      }
    } finally {
      if (isSecond) {
        setLoading2(false);
      } else {
        setLoading(false);
      }
    }
  };

  const handleSampleText = (type: 'human' | 'ai') => {
    const sample = SAMPLE_TEXTS[type];
    if (comparisonMode) {
      if (type === 'human') {
        setText(sample);
      } else {
        setText2(sample);
      }
    } else {
      setText(sample);
    }
  };

  const handleClear = () => {
    setText('');
    setText2('');
    setResult(null);
    setResult2(null);
    setError(null);
    setError2(null);
  };

  const handleCopyResults = async (format: 'json' | 'text') => {
    if (!result) return;

    let content = '';
    if (format === 'json') {
      content = JSON.stringify(result, null, 2);
    } else {
      content = `TraceNeuro Analysis Report\n`;
      content += `========================\n\n`;
      content += `Overall HumanScore: ${(result.humanscore * 100).toFixed(2)}%\n`;
      content += `Classification: ${getScoreLabel(result.humanscore)}\n\n`;
      content += `Marker Breakdown:\n`;
      Object.entries(result.breakdown).forEach(([key, value]) => {
        const info = MARKER_INFO[key] || { label: key, description: '' };
        content += `  ${info.label}: ${(Number(value) * 100).toFixed(2)}%\n`;
      });
      content += `\nMetadata:\n`;
      content += `  Sentences: ${result.metadata.sentence_count}\n`;
      content += `  Tokens: ${result.metadata.token_count}\n`;
      content += `  Characters: ${result.metadata.char_count}\n`;
    }

    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExport = (format: 'json' | 'text') => {
    if (!result) return;

    let content = '';
    let filename = '';
    let mimeType = '';

    if (format === 'json') {
      content = JSON.stringify(result, null, 2);
      filename = `traceneuro-analysis-${Date.now()}.json`;
      mimeType = 'application/json';
    } else {
      content = `TraceNeuro Analysis Report\n`;
      content += `Generated: ${new Date().toLocaleString()}\n`;
      content += `========================\n\n`;
      content += `Overall HumanScore: ${(result.humanscore * 100).toFixed(2)}%\n`;
      content += `Classification: ${getScoreLabel(result.humanscore)}\n\n`;
      content += `Marker Breakdown:\n`;
      Object.entries(result.breakdown).forEach(([key, value]) => {
        const info = MARKER_INFO[key] || { label: key, description: '' };
        content += `  ${info.label}: ${(Number(value) * 100).toFixed(2)}%\n`;
        content += `    ${info.description}\n`;
      });
      content += `\nMetadata:\n`;
      content += `  Sentences: ${result.metadata.sentence_count}\n`;
      content += `  Tokens: ${result.metadata.token_count}\n`;
      content += `  Characters: ${result.metadata.char_count}\n`;
      filename = `traceneuro-analysis-${Date.now()}.txt`;
      mimeType = 'text/plain';
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const calculateTextStats = (textToAnalyze: string, resultData: any) => {
    if (!textToAnalyze || !resultData) return null;

    const words = textToAnalyze.trim().split(/\s+/).filter(w => w.length > 0);
    const sentences = resultData.metadata?.sentence_count || 0;
    const avgWordsPerSentence = sentences > 0 ? (words.length / sentences).toFixed(1) : '0';
    const avgCharsPerWord = words.length > 0 ? (textToAnalyze.length / words.length).toFixed(1) : '0';
    
    // Simple readability estimate (Flesch-like)
    const avgSentenceLength = parseFloat(avgWordsPerSentence);
    const avgWordLength = parseFloat(avgCharsPerWord);
    const readability = Math.max(0, Math.min(100, 206.835 - (1.015 * avgSentenceLength) - (84.6 * avgWordLength / 5)));

    return {
      avgWordsPerSentence,
      avgCharsPerWord,
      readability: readability.toFixed(0),
      longestSentence: Math.max(...(resultData.metadata?.marker_details?.cadence?.sentence_length_variance ? [resultData.metadata.marker_details.cadence.sentence_length_variance] : [0])),
    };
  };

  const getScoreColor = (score: number): string => {
    if (score >= 0.7) return darkMode ? '#10b981' : '#10b981';
    if (score >= 0.4) return darkMode ? '#f59e0b' : '#f59e0b';
    return darkMode ? '#ef4444' : '#ef4444';
  };

  const getScoreLabel = (score: number): string => {
    if (score >= 0.7) return 'Likely Human';
    if (score >= 0.4) return 'Uncertain/Hybrid';
    return 'Likely AI';
  };

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
  const wordCount2 = text2.trim() ? text2.trim().split(/\s+/).length : 0;
  const textStats = calculateTextStats(text, result);
  const textStats2 = calculateTextStats(text2, result2);

  const bgColor = darkMode ? '#111827' : '#f9fafb';
  const cardBg = darkMode ? '#1f2937' : '#ffffff';
  const textColor = darkMode ? '#f3f4f6' : '#1f2937';
  const textColorSecondary = darkMode ? '#9ca3af' : '#6b7280';
  const borderColor = darkMode ? '#374151' : '#e5e7eb';

  return (
    <div style={{ 
      minHeight: '100vh',
      backgroundColor: bgColor,
      transition: 'background-color 0.3s',
    }}>
      <div style={{ 
        maxWidth: '1400px', 
        margin: '0 auto', 
        padding: '2rem',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      }}>
        {/* Header with Dark Mode Toggle */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '3rem',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div style={{ textAlign: 'center', flex: 1 }}>
            <h1 style={{ fontSize: '2.5rem', margin: '0 0 0.5rem 0', color: textColor }}>
              🧠 TraceNeuro
            </h1>
            <p style={{ fontSize: '1.1rem', color: textColorSecondary, margin: 0 }}>
              Cognitive Authenticity Engine - Analyze Human vs AI Writing Patterns
            </p>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <button
              onClick={() => setDarkMode(!darkMode)}
              style={{
                padding: '0.5rem 1rem',
                fontSize: '0.875rem',
                backgroundColor: darkMode ? '#374151' : '#e5e7eb',
                color: darkMode ? '#f3f4f6' : '#1f2937',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
              }}
            >
              {darkMode ? '☀️ Light' : '🌙 Dark'}
            </button>
            <button
              onClick={() => setShowHistory(!showHistory)}
              style={{
                padding: '0.5rem 1rem',
                fontSize: '0.875rem',
                backgroundColor: showHistory ? '#3b82f6' : (darkMode ? '#374151' : '#e5e7eb'),
                color: showHistory ? 'white' : (darkMode ? '#f3f4f6' : '#1f2937'),
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
              }}
            >
              📜 History
            </button>
            <button
              onClick={() => {
                setComparisonMode(!comparisonMode);
                if (!comparisonMode) {
                  setText2('');
                  setResult2(null);
                }
              }}
              style={{
                padding: '0.5rem 1rem',
                fontSize: '0.875rem',
                backgroundColor: comparisonMode ? '#3b82f6' : (darkMode ? '#374151' : '#e5e7eb'),
                color: comparisonMode ? 'white' : (darkMode ? '#f3f4f6' : '#1f2937'),
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
              }}
            >
              {comparisonMode ? '📊 Single' : '⚖️ Compare'}
            </button>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '2rem', alignItems: 'flex-start' }}>
          {/* Main Content */}
          <div style={{ flex: 1, minWidth: 0 }}>
            {/* Sample Text Buttons */}
            <div style={{ 
              display: 'flex', 
              gap: '0.5rem', 
              marginBottom: '1rem',
              flexWrap: 'wrap'
            }}>
              <button
                onClick={() => handleSampleText('human')}
                style={{
                  padding: '0.5rem 1rem',
                  fontSize: '0.875rem',
                  backgroundColor: darkMode ? '#374151' : '#e5e7eb',
                  color: textColor,
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                }}
              >
                📝 Sample Human Text
              </button>
              <button
                onClick={() => handleSampleText('ai')}
                style={{
                  padding: '0.5rem 1rem',
                  fontSize: '0.875rem',
                  backgroundColor: darkMode ? '#374151' : '#e5e7eb',
                  color: textColor,
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                }}
              >
                🤖 Sample AI Text
              </button>
            </div>

            {/* Input Section */}
            <div style={{ 
              backgroundColor: cardBg,
              borderRadius: '12px',
              padding: '2rem',
              boxShadow: darkMode ? '0 1px 3px rgba(0,0,0,0.3)' : '0 1px 3px rgba(0,0,0,0.1)',
              marginBottom: '2rem'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h2 style={{ margin: 0, fontSize: '1.25rem', color: textColor }}>
                  {comparisonMode ? 'Text 1' : 'Enter Text to Analyze'}
                </h2>
                <div style={{ fontSize: '0.875rem', color: textColorSecondary }}>
                  {text.length} chars • {wordCount} words
                </div>
              </div>
              
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste or type text to analyze... (minimum 10 characters)"
                style={{
                  width: '100%',
                  minHeight: '200px',
                  padding: '1rem',
                  fontSize: '1rem',
                  border: `2px solid ${borderColor}`,
                  borderRadius: '8px',
                  fontFamily: 'inherit',
                  resize: 'vertical',
                  backgroundColor: darkMode ? '#111827' : '#ffffff',
                  color: textColor,
                }}
              />

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', flexWrap: 'wrap' }}>
                <button
                  onClick={() => handleScore(text, false)}
                  disabled={loading || text.length < 10}
                  style={{
                    padding: '0.75rem 2rem',
                    fontSize: '1rem',
                    fontWeight: '600',
                    backgroundColor: loading || text.length < 10 ? '#9ca3af' : '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: loading || text.length < 10 ? 'not-allowed' : 'pointer',
                  }}
                >
                  {loading ? '⏳ Analyzing...' : '🔍 Analyze Text'}
                </button>
                
                {text && (
                  <button
                    onClick={handleClear}
                    disabled={loading}
                    style={{
                      padding: '0.75rem 2rem',
                      fontSize: '1rem',
                      backgroundColor: 'transparent',
                      color: textColorSecondary,
                      border: `2px solid ${borderColor}`,
                      borderRadius: '8px',
                      cursor: loading ? 'not-allowed' : 'pointer',
                    }}
                  >
                    Clear
                  </button>
                )}
              </div>

              {error && (
                <div style={{
                  marginTop: '1rem',
                  padding: '1rem',
                  backgroundColor: darkMode ? '#7f1d1d' : '#fef2f2',
                  color: '#dc2626',
                  borderRadius: '8px',
                  border: '1px solid #fecaca',
                }}>
                  ⚠️ {error}
                </div>
              )}
            </div>

            {/* Comparison Mode - Second Text */}
            {comparisonMode && (
              <div style={{ 
                backgroundColor: cardBg,
                borderRadius: '12px',
                padding: '2rem',
                boxShadow: darkMode ? '0 1px 3px rgba(0,0,0,0.3)' : '0 1px 3px rgba(0,0,0,0.1)',
                marginBottom: '2rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h2 style={{ margin: 0, fontSize: '1.25rem', color: textColor }}>Text 2</h2>
                  <div style={{ fontSize: '0.875rem', color: textColorSecondary }}>
                    {text2.length} chars • {wordCount2} words
                  </div>
                </div>
                
                <textarea
                  value={text2}
                  onChange={(e) => setText2(e.target.value)}
                  placeholder="Paste or type second text to compare... (minimum 10 characters)"
                  style={{
                    width: '100%',
                    minHeight: '200px',
                    padding: '1rem',
                    fontSize: '1rem',
                    border: `2px solid ${borderColor}`,
                    borderRadius: '8px',
                    fontFamily: 'inherit',
                    resize: 'vertical',
                    backgroundColor: darkMode ? '#111827' : '#ffffff',
                    color: textColor,
                  }}
                />

                <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                  <button
                    onClick={() => handleScore(text2, true)}
                    disabled={loading2 || text2.length < 10}
                    style={{
                      padding: '0.75rem 2rem',
                      fontSize: '1rem',
                      fontWeight: '600',
                      backgroundColor: loading2 || text2.length < 10 ? '#9ca3af' : '#3b82f6',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: loading2 || text2.length < 10 ? 'not-allowed' : 'pointer',
                    }}
                  >
                    {loading2 ? '⏳ Analyzing...' : '🔍 Analyze Text 2'}
                  </button>
                </div>

                {error2 && (
                  <div style={{
                    marginTop: '1rem',
                    padding: '1rem',
                    backgroundColor: darkMode ? '#7f1d1d' : '#fef2f2',
                    color: '#dc2626',
                    borderRadius: '8px',
                    border: '1px solid #fecaca',
                  }}>
                    ⚠️ {error2}
                  </div>
                )}
              </div>
            )}

            {/* Results Section */}
            {result && (
              <div style={{ marginTop: '2rem' }}>
                {/* Action Buttons */}
                <div style={{ 
                  display: 'flex', 
                  gap: '0.5rem', 
                  marginBottom: '1rem',
                  flexWrap: 'wrap'
                }}>
                  <button
                    onClick={() => handleCopyResults('text')}
                    style={{
                      padding: '0.5rem 1rem',
                      fontSize: '0.875rem',
                      backgroundColor: darkMode ? '#374151' : '#e5e7eb',
                      color: textColor,
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                    }}
                  >
                    {copied ? '✓ Copied!' : '📋 Copy Results'}
                  </button>
                  <button
                    onClick={() => handleExport('text')}
                    style={{
                      padding: '0.5rem 1rem',
                      fontSize: '0.875rem',
                      backgroundColor: darkMode ? '#374151' : '#e5e7eb',
                      color: textColor,
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                    }}
                  >
                    💾 Export Text
                  </button>
                  <button
                    onClick={() => handleExport('json')}
                    style={{
                      padding: '0.5rem 1rem',
                      fontSize: '0.875rem',
                      backgroundColor: darkMode ? '#374151' : '#e5e7eb',
                      color: textColor,
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                    }}
                  >
                    💾 Export JSON
                  </button>
                </div>

                {/* Overall Score Card */}
                <div style={{
                  backgroundColor: cardBg,
                  borderRadius: '12px',
                  padding: '2rem',
                  boxShadow: darkMode ? '0 1px 3px rgba(0,0,0,0.3)' : '0 1px 3px rgba(0,0,0,0.1)',
                  marginBottom: '2rem',
                  textAlign: 'center',
                }}>
                  <h2 style={{ margin: '0 0 1rem 0', fontSize: '1.25rem', color: textColor }}>
                    Overall HumanScore™ {comparisonMode && '(Text 1)'}
                  </h2>
                  <div style={{ 
                    fontSize: '4rem', 
                    fontWeight: 'bold',
                    color: getScoreColor(result.humanscore),
                    marginBottom: '0.5rem'
                  }}>
                    {(result.humanscore * 100).toFixed(1)}%
                  </div>
                  <div style={{ 
                    fontSize: '1.25rem', 
                    color: getScoreColor(result.humanscore),
                    fontWeight: '600',
                    marginBottom: '1rem'
                  }}>
                    {getScoreLabel(result.humanscore)}
                  </div>
                  <div style={{ 
                    width: '100%', 
                    height: '12px', 
                    backgroundColor: borderColor, 
                    borderRadius: '6px',
                    overflow: 'hidden',
                    marginBottom: '1rem'
                  }}>
                    <div style={{
                      width: `${result.humanscore * 100}%`,
                      height: '100%',
                      backgroundColor: getScoreColor(result.humanscore),
                      transition: 'width 0.3s ease',
                    }} />
                  </div>
                  <div style={{ fontSize: '0.875rem', color: textColorSecondary }}>
                    {result.metadata.sentence_count} sentences • {result.metadata.token_count} tokens • {result.metadata.char_count} characters
                  </div>
                </div>

                {/* Text Stats Panel */}
                {textStats && (
                  <div style={{
                    backgroundColor: cardBg,
                    borderRadius: '12px',
                    padding: '1.5rem',
                    boxShadow: darkMode ? '0 1px 3px rgba(0,0,0,0.3)' : '0 1px 3px rgba(0,0,0,0.1)',
                    marginBottom: '2rem',
                  }}>
                    <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem', color: textColor }}>
                      📊 Text Statistics
                    </h3>
                    <div style={{ 
                      display: 'grid', 
                      gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                      gap: '1rem'
                    }}>
                      <div>
                        <div style={{ fontSize: '0.875rem', color: textColorSecondary, marginBottom: '0.25rem' }}>Avg Words/Sentence</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: '600', color: textColor }}>{textStats.avgWordsPerSentence}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.875rem', color: textColorSecondary, marginBottom: '0.25rem' }}>Avg Chars/Word</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: '600', color: textColor }}>{textStats.avgCharsPerWord}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.875rem', color: textColorSecondary, marginBottom: '0.25rem' }}>Readability Score</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: '600', color: textColor }}>{textStats.readability}</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Marker Scores Grid */}
                <div>
                  <h2 style={{ margin: '0 0 1.5rem 0', fontSize: '1.5rem', color: textColor }}>
                    Cognitive Marker Breakdown {comparisonMode && '(Text 1)'}
                  </h2>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                    gap: '1.5rem',
                  }}>
                    {Object.entries(result.breakdown).map(([key, value]) => {
                      const score = Number(value);
                      const info = MARKER_INFO[key] || { label: key, description: '' };
                      return (
                        <div
                          key={key}
                          style={{
                            backgroundColor: cardBg,
                            borderRadius: '12px',
                            padding: '1.5rem',
                            boxShadow: darkMode ? '0 1px 3px rgba(0,0,0,0.3)' : '0 1px 3px rgba(0,0,0,0.1)',
                            border: `1px solid ${borderColor}`,
                          }}
                        >
                          <div style={{ marginBottom: '1rem' }}>
                            <h3 style={{ 
                              margin: '0 0 0.25rem 0', 
                              fontSize: '1.1rem', 
                              color: textColor,
                              fontWeight: '600'
                            }}>
                              {info.label}
                            </h3>
                            <p style={{ 
                              margin: 0, 
                              fontSize: '0.875rem', 
                              color: textColorSecondary 
                            }}>
                              {info.description}
                            </p>
                          </div>
                          
                          <div style={{ marginBottom: '0.75rem' }}>
                            <div style={{ 
                              display: 'flex', 
                              justifyContent: 'space-between',
                              marginBottom: '0.5rem'
                            }}>
                              <span style={{ fontSize: '0.875rem', color: textColorSecondary }}>Score</span>
                              <span style={{ 
                                fontSize: '1.25rem', 
                                fontWeight: '600',
                                color: getScoreColor(score)
                              }}>
                                {(score * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div style={{ 
                              width: '100%', 
                              height: '8px', 
                              backgroundColor: borderColor, 
                              borderRadius: '4px',
                              overflow: 'hidden'
                            }}>
                              <div style={{
                                width: `${score * 100}%`,
                                height: '100%',
                                backgroundColor: getScoreColor(score),
                                transition: 'width 0.3s ease',
                              }} />
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* Comparison Results - Text 2 */}
            {comparisonMode && result2 && (
              <div style={{ marginTop: '3rem' }}>
                <div style={{
                  backgroundColor: cardBg,
                  borderRadius: '12px',
                  padding: '2rem',
                  boxShadow: darkMode ? '0 1px 3px rgba(0,0,0,0.3)' : '0 1px 3px rgba(0,0,0,0.1)',
                  marginBottom: '2rem',
                  textAlign: 'center',
                }}>
                  <h2 style={{ margin: '0 0 1rem 0', fontSize: '1.25rem', color: textColor }}>
                    Overall HumanScore™ (Text 2)
                  </h2>
                  <div style={{ 
                    fontSize: '4rem', 
                    fontWeight: 'bold',
                    color: getScoreColor(result2.humanscore),
                    marginBottom: '0.5rem'
                  }}>
                    {(result2.humanscore * 100).toFixed(1)}%
                  </div>
                  <div style={{ 
                    fontSize: '1.25rem', 
                    color: getScoreColor(result2.humanscore),
                    fontWeight: '600',
                    marginBottom: '1rem'
                  }}>
                    {getScoreLabel(result2.humanscore)}
                  </div>
                  <div style={{ 
                    width: '100%', 
                    height: '12px', 
                    backgroundColor: borderColor, 
                    borderRadius: '6px',
                    overflow: 'hidden',
                    marginBottom: '1rem'
                  }}>
                    <div style={{
                      width: `${result2.humanscore * 100}%`,
                      height: '100%',
                      backgroundColor: getScoreColor(result2.humanscore),
                      transition: 'width 0.3s ease',
                    }} />
                  </div>
                  <div style={{ fontSize: '0.875rem', color: textColorSecondary }}>
                    {result2.metadata.sentence_count} sentences • {result2.metadata.token_count} tokens • {result2.metadata.char_count} characters
                  </div>
                </div>

                {textStats2 && (
                  <div style={{
                    backgroundColor: cardBg,
                    borderRadius: '12px',
                    padding: '1.5rem',
                    boxShadow: darkMode ? '0 1px 3px rgba(0,0,0,0.3)' : '0 1px 3px rgba(0,0,0,0.1)',
                    marginBottom: '2rem',
                  }}>
                    <h3 style={{ margin: '0 0 1rem 0', fontSize: '1.1rem', color: textColor }}>
                      📊 Text Statistics (Text 2)
                    </h3>
                    <div style={{ 
                      display: 'grid', 
                      gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                      gap: '1rem'
                    }}>
                      <div>
                        <div style={{ fontSize: '0.875rem', color: textColorSecondary, marginBottom: '0.25rem' }}>Avg Words/Sentence</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: '600', color: textColor }}>{textStats2.avgWordsPerSentence}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.875rem', color: textColorSecondary, marginBottom: '0.25rem' }}>Avg Chars/Word</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: '600', color: textColor }}>{textStats2.avgCharsPerWord}</div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.875rem', color: textColorSecondary, marginBottom: '0.25rem' }}>Readability Score</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: '600', color: textColor }}>{textStats2.readability}</div>
                      </div>
                    </div>
                  </div>
                )}

                <div>
                  <h2 style={{ margin: '0 0 1.5rem 0', fontSize: '1.5rem', color: textColor }}>
                    Cognitive Marker Breakdown (Text 2)
                  </h2>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                    gap: '1.5rem',
                  }}>
                    {Object.entries(result2.breakdown).map(([key, value]) => {
                      const score = Number(value);
                      const info = MARKER_INFO[key] || { label: key, description: '' };
                      return (
                        <div
                          key={key}
                          style={{
                            backgroundColor: cardBg,
                            borderRadius: '12px',
                            padding: '1.5rem',
                            boxShadow: darkMode ? '0 1px 3px rgba(0,0,0,0.3)' : '0 1px 3px rgba(0,0,0,0.1)',
                            border: `1px solid ${borderColor}`,
                          }}
                        >
                          <div style={{ marginBottom: '1rem' }}>
                            <h3 style={{ 
                              margin: '0 0 0.25rem 0', 
                              fontSize: '1.1rem', 
                              color: textColor,
                              fontWeight: '600'
                            }}>
                              {info.label}
                            </h3>
                            <p style={{ 
                              margin: 0, 
                              fontSize: '0.875rem', 
                              color: textColorSecondary 
                            }}>
                              {info.description}
                            </p>
                          </div>
                          
                          <div style={{ marginBottom: '0.75rem' }}>
                            <div style={{ 
                              display: 'flex', 
                              justifyContent: 'space-between',
                              marginBottom: '0.5rem'
                            }}>
                              <span style={{ fontSize: '0.875rem', color: textColorSecondary }}>Score</span>
                              <span style={{ 
                                fontSize: '1.25rem', 
                                fontWeight: '600',
                                color: getScoreColor(score)
                              }}>
                                {(score * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div style={{ 
                              width: '100%', 
                              height: '8px', 
                              backgroundColor: borderColor, 
                              borderRadius: '4px',
                              overflow: 'hidden'
                            }}>
                              <div style={{
                                width: `${score * 100}%`,
                                height: '100%',
                                backgroundColor: getScoreColor(score),
                                transition: 'width 0.3s ease',
                              }} />
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* History Sidebar */}
          {showHistory && (
            <div style={{
              width: '320px',
              backgroundColor: cardBg,
              borderRadius: '12px',
              padding: '1.5rem',
              boxShadow: darkMode ? '0 1px 3px rgba(0,0,0,0.3)' : '0 1px 3px rgba(0,0,0,0.1)',
              position: 'sticky',
              top: '2rem',
              maxHeight: 'calc(100vh - 4rem)',
              overflowY: 'auto',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ margin: 0, fontSize: '1.1rem', color: textColor }}>Recent History</h3>
                <button
                  onClick={() => setShowHistory(false)}
                  style={{
                    padding: '0.25rem 0.5rem',
                    fontSize: '0.75rem',
                    backgroundColor: 'transparent',
                    color: textColorSecondary,
                    border: 'none',
                    cursor: 'pointer',
                  }}
                >
                  ✕
                </button>
              </div>
              {history.length === 0 ? (
                <div style={{ color: textColorSecondary, fontSize: '0.875rem', textAlign: 'center', padding: '2rem 0' }}>
                  No history yet
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {history.map((item) => (
                    <div
                      key={item.id}
                      onClick={() => {
                        setText(item.text_preview);
                        setResult({
                          humanscore: item.humanscore,
                          breakdown: item.breakdown,
                          metadata: { sentence_count: 0, token_count: 0, char_count: 0 }
                        });
                        setShowHistory(false);
                      }}
                      style={{
                        padding: '1rem',
                        backgroundColor: darkMode ? '#111827' : '#f9fafb',
                        borderRadius: '8px',
                        border: `1px solid ${borderColor}`,
                        cursor: 'pointer',
                        transition: 'transform 0.2s',
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                      onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                    >
                      <div style={{ 
                        fontSize: '1.5rem', 
                        fontWeight: 'bold',
                        color: getScoreColor(item.humanscore),
                        marginBottom: '0.5rem'
                      }}>
                        {(item.humanscore * 100).toFixed(1)}%
                      </div>
                      <div style={{ 
                        fontSize: '0.75rem', 
                        color: textColorSecondary,
                        marginBottom: '0.5rem'
                      }}>
                        {new Date(item.created_at).toLocaleString()}
                      </div>
                      <div style={{ 
                        fontSize: '0.875rem', 
                        color: textColor,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 3,
                        WebkitBoxOrient: 'vertical',
                      }}>
                        {item.text_preview}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
