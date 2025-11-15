import api from './axios';

export const photoRecognitionAPI = {
  // Get available providers (filtered by subscription tier)
  getProviders: () => api.get('/integrations/photo-recognition/providers/'),

  // Get user's configured providers
  getMyConfigs: () => api.get('/integrations/photo-recognition/configure/'),

  // Configure a new provider
  configureProvider: (data) => api.post('/integrations/photo-recognition/configure/', data),

  // Delete provider configuration
  deleteConfig: (id) => api.delete(`/integrations/photo-recognition/configure/${id}/`),

  // Set provider as default
  setDefault: (id) => api.patch(`/integrations/photo-recognition/configure/${id}/set-default/`),
};

export default photoRecognitionAPI;
