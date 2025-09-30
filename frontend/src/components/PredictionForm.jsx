import React, { useState } from 'react';

/**
 * Form component for collecting applicant features.  It renders a simple
 * input for each feature and calls the supplied `onSubmit` handler with a
 * dictionary of values when the form is submitted.
 */
export default function PredictionForm({ features, onSubmit, submitting }) {
  // Initialise form state
  const [values, setValues] = useState(() => {
    const initial = {};
    features.forEach((f) => {
      initial[f.name] = '';
    });
    return initial;
  });

  // Handle change to any input
  const handleChange = (e, name) => {
    setValues({
      ...values,
      [name]: e.target.value,
    });
  };

  // Handle submit event
  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSubmit) {
      onSubmit(values);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      {features.map((f) => (
        <div key={f.name} className="flex flex-col">
          <label className="mb-1 font-semibold" htmlFor={f.name}>
            {f.name}
          </label>
          <input
            id={f.name}
            type="text"
            className="border rounded px-2 py-1"
            value={values[f.name]}
            onChange={(e) => handleChange(e, f.name)}
            required
          />
        </div>
      ))}
      <button
        type="submit"
        disabled={submitting}
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {submitting ? 'Submitting...' : 'Predict'}
      </button>
    </form>
  );
}