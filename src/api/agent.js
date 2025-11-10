import api from './axios';

export const agentAPI = {
  // Training - Documents (using documents API)
  uploadFile: (formData) => api.post('/documents/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getFiles: () => api.get('/documents/'),
  deleteFile: (fileId) => api.delete(`/documents/${fileId}/`),

  // Prompt
  getPrompt: () => api.get('/agent/prompt/'),
  updatePrompt: (prompt) => api.put('/agent/prompt/', { prompt }),

  // Training - Start embeddings processing
  startTraining: () => api.post('/embeddings/process-all/'),
  getTrainingStatus: () => api.get('/embeddings/status/'),

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

  // Telegram
  connectTelegram: (token) => api.post('/integrations/telegram/connect/', { bot_token: token }),

  // WhatsApp
  connectWhatsApp: (phoneId, token) => api.post('/integrations/whatsapp/connect/', { phone_number_id: phoneId, access_token: token }),

  // Google Calendar
  getCalendarAuthUrl: () => api.get('/integrations/calendar/auth/'),
  connectCalendar: (code) => api.post('/integrations/calendar/callback/', { code }),

  // Google Sheets
  connectGoogleSheets: () => api.post('/integrations/sheets/connect/'),
  exportToSheets: (exportType = 'all') => api.post('/integrations/sheets/export/', { export_type: exportType }),

  // Instagram
  getInstagramAuthUrl: () => api.get('/integrations/instagram/auth/'),
  connectInstagram: (code) => api.post('/integrations/instagram/callback/', { code }),

  // Website Widget
  setupWidget: (config) => api.post('/integrations/widget/setup/', config),
  getWidgetConfig: () => api.get('/integrations/widget/config/'),

  // General
  disconnectIntegration: (integrationId) => api.delete(`/integrations/${integrationId}/`),

  // Analytics
  getSmartInsights: (language = 'en') => api.get('/agent/analytics/insights/', { params: { language } }),

  // Google Reviews
  getGoogleReviewsAuthUrl: () => api.get('/integrations/google-reviews/auth/'),
  connectGoogleReviews: (code) => api.post('/integrations/google-reviews/callback/', { code }),
  getReviewsSummary: () => api.get('/integrations/google-reviews/summary/'),

  // Instagram Advanced
  createInstagramEmbeddings: () => api.post('/integrations/instagram/create-embeddings/'),
  getInstagramAnalytics: (period = 'month') => api.get('/integrations/instagram/analytics/', { params: { period } }),
  getContentRecommendations: () => api.get('/integrations/instagram/content-recommendations/'),

  // Email Integration
  connectEmail: (provider, credentials) => api.post('/integrations/email/connect/', { provider, credentials }),
  getEmailAnalytics: () => api.get('/integrations/email/analytics/'),
};
