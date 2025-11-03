import axios from 'axios';

const MOCK_MODE = import.meta.env.VITE_MOCK_MODE === 'true' || !import.meta.env.VITE_API_URL;

// Use Vite proxy in development (relative URL) or full URL in production
const getBaseURL = () => {
  // In development, use relative URL to leverage Vite proxy
  if (import.meta.env.DEV) {
    return '/api';
  }
  // In production, use full URL from env
  const envURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  // If URL doesn't end with /api, add it
  if (!envURL.endsWith('/api')) {
    return envURL.endsWith('/') ? `${envURL}api` : `${envURL}/api`;
  }
  return envURL;
};

const api = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor для додавання токена
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor для обробки помилок
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    // Якщо це помилка мережі, додаємо мок позначку для обробки в AuthContext
    if (error.code === 'ERR_NETWORK' || error.code === 'ERR_CONNECTION_REFUSED') {
      error.mock = true;
    }
    
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
export { MOCK_MODE };
