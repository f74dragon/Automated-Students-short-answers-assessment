import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api';

// Create a reusable axios instance with the base URL
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add request interceptor to include the auth token in all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Helper function to handle errors
export const handleApiError = (error) => {
  let errorMessage = 'Something went wrong. Please try again.';
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    if (error.response.data && error.response.data.detail) {
      errorMessage = error.response.data.detail;
    } else {
      errorMessage = `Error ${error.response.status}: ${error.response.statusText}`;
    }
  } else if (error.request) {
    // The request was made but no response was received
    errorMessage = 'Server did not respond. Please check your connection.';
  }
  return errorMessage;
};

export default api;
