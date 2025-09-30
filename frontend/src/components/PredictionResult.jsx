import React from 'react';

/**
 * Simple component to display the prediction result.  It shows a message
 * indicating approval or rejection and the underlying probability.
 */
export default function PredictionResult({ result }) {
  if (!result) return null;
  const { prediction, probability } = result;
  const approved = prediction === 0;
  return (
    <div className="p-4 mt-4 border rounded bg-gray-50">
      <p className="text-lg font-bold">
        {approved ? 'Loan Approved' : 'Loan Denied'}
      </p>
      <p>
        Probability of default: {(probability * 100).toFixed(2)}%
      </p>
    </div>
  );
}