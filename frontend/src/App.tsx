import React, { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000';
type Rating = 'Too Easy' | 'Just Right' | 'Too Hard';

function App() {
  const [story, setStory] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [hasRated, setHasRated] = useState<boolean>(false);

  useEffect(() => {
    fetchStory();
  }, []);

  const fetchStory = async (last_rating?: Rating) => {
    setLoading(true);
    setError(null);
    setHasRated(false);
    try {
      const res = await fetch(`${API_URL}/generate_story`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ last_rating }),
      });
      if (!res.ok) throw new Error('Failed to fetch story');
      const data = await res.json();
      setStory(data.story);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Unknown error');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRating = (rating: Rating) => {
    setHasRated(true);
    if (rating === 'Just Right') return;
    fetchStory(rating);
  };

  return (
    <div style={{ margin: 0, padding: 0 }}>
      <style>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
      `}</style>
      {loading && <div>Loading...</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {!loading && !error && <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>{story}</pre>}
      {hasRated && <div>Thank you for your feedback!</div>}
      <div style={{ marginTop: '1em' }}>
        {(['Too Easy', 'Just Right', 'Too Hard']).map((rating) => (
          <button
            key={rating}
            onClick={() => handleRating(rating as Rating)}
            disabled={loading || hasRated}
            style={{ marginRight: 8 }}
          >
            {rating}
          </button>
        ))}
      </div>
    </div>
  );
}

export default App;
