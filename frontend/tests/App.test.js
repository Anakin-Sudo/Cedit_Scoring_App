import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../src/App.jsx';
import * as api from '../src/api.js';

// Mock the API module
jest.mock('../src/api.js');

describe('App component', () => {
  test('renders form fields based on schema', async () => {
    // Arrange: mock the schema API to return two fields
    api.fetchSchema.mockResolvedValue({
      data: { features: [{ name: 'Status' }, { name: 'Duration' }] },
    });
    // Act
    render(<App />);
    // Assert
    await waitFor(() => {
      expect(screen.getByLabelText('Status')).toBeInTheDocument();
      expect(screen.getByLabelText('Duration')).toBeInTheDocument();
    });
  });
});