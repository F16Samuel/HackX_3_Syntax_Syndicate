import axios from 'axios';

// Get the API URL from environment variables, with a fallback
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_SEC = import.meta.env.VITE_API_SEC || 'http://localhost:8081';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiSec = axios.create({
  baseURL: API_SEC,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to add the auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor to handle auth errors (like 401 Unauthorized)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear stale auth data
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_role');
      localStorage.removeItem('user_email');
      
      // Redirect to login page
      // Use window.location to force a full refresh, clearing any app state
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

