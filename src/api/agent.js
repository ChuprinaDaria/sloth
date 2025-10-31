import api from './axios';

export const agentAPI = {
  // Training
  uploadFile: (formData) => api.post('/agent/files/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getFiles: () => api.get('/agent/files/'),
  deleteFile: (fileId) => api.delete(`/agent/files/${fileId}/`),

  // Prompt
  getPrompt: () => api.get('/agent/prompt/'),
  updatePrompt: (prompt) => api.put('/agent/prompt/', { prompt }),

  // Training
  startTraining: () => api.post('/agent/train/'),
  getTrainingStatus: () => api.get('/agent/train/status/'),

  // Testing
  testChat: (message, photo = null) => {
    const formData = new FormData();
    formData.append('message', message);
    if (photo) {
      formData.append('photo', photo);
    }
    return api.post('/agent/test/', formData);
  },

  // History
  getChatHistory: () => api.get('/agent/history/'),
  getChatDetail: (chatId) => api.get(`/agent/history/${chatId}/`),

  // Integrations
  getIntegrations: () => api.get('/integrations/'),
  connectTelegram: (token) => api.post('/integrations/telegram/', { token }),
  connectWhatsApp: (phoneId, token) => api.post('/integrations/whatsapp/', { phone_id: phoneId, token }),
  connectCalendar: (email) => api.post('/integrations/calendar/', { email }),
  disconnectIntegration: (integrationId) => api.delete(`/integrations/${integrationId}/`),
};
