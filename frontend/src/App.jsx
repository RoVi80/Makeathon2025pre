import { useState } from 'react';
import './HotelFinder.css';

export default function HotelFinder() {
  const [query, setQuery] = useState('');
  const [hotels, setHotels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const findHotels = async () => {
    setLoading(true);
    setError('');
    setHotels([]);

    try {
      const res = await fetch('http://127.0.0.1:8000/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query }),
      });

      const contentType = res.headers.get('content-type') || '';
      const isJson = contentType.includes('application/json');
      const data = isJson ? await res.json() : null;

      if (!res.ok || !data) {
        throw new Error(data?.error || `❌ Unexpected error (${res.status})`);
      }

      if (Array.isArray(data)) {
        if (data.length === 0) {
          setError('😕 No hotels matched your query.');
        } else {
          setHotels(data);
        }
      } else if (data.error) {
        setError(`❌ ${data.error}`);
      } else {
        setError('⚠️ Unexpected response format.');
      }
    } catch (err) {
      console.error('❌ Error:', err);
      setError(err.message || 'Server error or API unavailable.');
    } finally {
      setLoading(false);
    }
  };

  const isIdle = hotels.length === 0 && !loading && !error;

  // 🧠 Human-friendly filter labels
  const filterLabels = {
    pet_friendly: "🐾 Pet-Friendly",
    quiet: "🌿 Quiet",
    parking: "🅿️ Parking",
    breakfast_quality: "🍳 Breakfast",
    near_landmark: "📍 Near Landmark",
  };

  return (
    <div className="hotel-finder-container">
      <div className="hotel-finder-content">
        <h1>🔍 Smart Hotel Recommender</h1>

        <div className="search-container">
          <input
            type="text"
            placeholder="Describe your ideal hotel..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && query.trim()) {
                findHotels();
              }
            }}
          />
          <button
            onClick={findHotels}
            disabled={loading || !query.trim()}
          >
            {loading ? 'Finding...' : 'Find Hotels'}
          </button>
        </div>

        {error && <p className="error-message">{error}</p>}

        {hotels.length > 0 && (
          <div className="hotel-results">
            {hotels.map((hotel, index) => (
              <div key={index} className="hotel-card">
                <h2>🏨 {hotel.name}</h2>
                <p className="hotel-score">💯 Score: {hotel.score.toFixed(2)}</p>
                <p className="hotel-location">
                  📍 {hotel.location} — {hotel.near_landmark}
                </p>
                <ul className="hotel-details">
                  <li>🍳 Breakfast rating: {hotel.breakfast_rating}</li>
                  <li>🐾 Pet-friendly: {hotel.pet_friendly ? 'Yes' : 'No'}</li>
                  <li>🅿️ Parking: {hotel.parking ? 'Yes' : 'No'}</li>
                  <li>🌿 Quiet: {hotel.quiet ? 'Yes' : 'No'}</li>
                  <li>🚶‍♂️ Distance to center: {hotel.distance_to_center_km} km</li>
                </ul>

                <div className="hotel-match-info">
                  {hotel.matched_filters?.length > 0 && (
                    <>
                      <p><strong>Matched filters:</strong></p>
                      <ul className="matched-filters">
                        {hotel.matched_filters.map((filter, i) => (
                          <li key={i} className="match-tag">
                            ✅ {filterLabels[filter] || filter}
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
                  {hotel.failed_filters?.length > 0 && (
                    <>
                      <p><strong>Unmatched filters:</strong></p>
                      <ul className="unmatched-filters">
                        {hotel.failed_filters.map((filter, i) => (
                          <li key={i} className="miss-tag">
                            ❌ {filterLabels[filter] || filter}
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
