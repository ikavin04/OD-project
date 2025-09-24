import axios from 'axios';

// Create the main API instance
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
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

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - just remove token, don't redirect
      // Let the app's routing handle the redirect naturally
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
      console.log('401 error: Token removed, letting app handle redirect');
    }
    return Promise.reject(error);
  }
);

export default api;