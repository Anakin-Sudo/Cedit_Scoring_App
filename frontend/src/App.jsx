import React, { useEffect, useState } from 'react';
import { fetchSchema, predict } from './api.js';
import PredictionForm from './components/PredictionForm.jsx';
import PredictionResult from './components/PredictionResult.jsx';

/**
 * Top‑level React component.  It fetches the feature schema on mount and
 * renders the prediction form.  After the user submits the form it shows
 * the prediction result.
 */
export default function App() {
  const [features, setFeatures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadSchema() {
      try {
        const res = await fetchSchema();
        setFeatures(res.data.features);
      } catch (err) {
        console.error(err);
        setError('Failed to load schema');
      } finally {
        setLoading(false);
      }
    }
    loadSchema();
  }, []);

  const handleSubmit = async (values) => {
    setSubmitting(true);
    setError('');
    try {
      const res = await predict(values);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Prediction failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Credit Scoring App</h1>
      {loading && <p>Loading form...</p>}
      {error && (
        <p className="text-red-600 mb-4">
          {error}
        </p>
      )}
      {!loading && !error && (
        <PredictionForm
          features={features}
          onSubmit={handleSubmit}
          submitting={submitting}
        />
      )}
      <PredictionResult result={result} />
    </div>
  );
}