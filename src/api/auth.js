import api from './axios';

export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  logout: () => api.post('/auth/logout/'),
  getProfile: () => api.get('/auth/me/'),
  refreshToken: (refreshToken) => api.post('/auth/refresh/', { refresh: refreshToken }),
};
