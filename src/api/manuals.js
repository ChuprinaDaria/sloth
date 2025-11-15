import api from './axios';

export const manualsAPI = {
  // Get all manuals
  getManuals: (params = {}) => api.get('/manuals/', { params }),

  // Get manual by ID
  getManual: (id) => api.get(`/manuals/${id}/`),

  // Get featured manuals
  getFeaturedManuals: (language = 'en') => api.get('/manuals/featured/', { params: { language } }),

  // Get categories
  getCategories: () => api.get('/manuals/categories/'),

  // Submit feedback
  submitFeedback: (manualId, data) => api.post(`/manuals/${manualId}/feedback/`, data),
};

export default manualsAPI;
