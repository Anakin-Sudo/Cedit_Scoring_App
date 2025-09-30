import axios from 'axios';

// Determine the base URL for API calls.  Vite exposes variables under
// import.meta.env while Create React App uses process.env.REACT_APP_*.  Fall
// back to relative paths if none are specified.
const API_URL =
  (import.meta.env && import.meta.env.VITE_API_URL) ||
  process.env.REACT_APP_API_URL ||
  '';

const api = axios.create({
  baseURL: API_URL,
});

export const fetchSchema = () => api.get('/schema');
export const predict = (features) => api.post('/predict', { features });

export default api;