import axios from 'axios';
import * as SecureStore from 'expo-secure-store';
import Constants from 'expo-constants';

// API Base URL from app.json config
const API_URL = Constants.expoConfig?.extra?.apiUrl || 'https://sloth-ai.lazysoft.pl/api';

// Create axios instance
const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
api.interceptors.request.use(
  async (config) => {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error getting auth token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 - unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh token
        const refreshToken = await SecureStore.getItemAsync('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_URL}/auth/refresh/`, {
            refresh: refreshToken,
          });

          const { access } = response.data;
          await SecureStore.setItemAsync('auth_token', access);

          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed - logout user
        await SecureStore.deleteItemAsync('auth_token');
        await SecureStore.deleteItemAsync('refresh_token');
        // Navigate to login screen
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// API methods
export const authAPI = {
  // Login
  login: async (email, password) => {
    const response = await api.post('/auth/login/', { email, password });
    const { access, refresh } = response.data;

    // Save tokens securely
    await SecureStore.setItemAsync('auth_token', access);
    await SecureStore.setItemAsync('refresh_token', refresh);

    return response.data;
  },

  // Register
  register: async (userData) => {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },

  // Logout
  logout: async () => {
    await SecureStore.deleteItemAsync('auth_token');
    await SecureStore.deleteItemAsync('refresh_token');
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await api.get('/auth/me/');
    return response.data;
  },
};

export const agentAPI = {
  // Get conversations
  getConversations: async (page = 1) => {
    const response = await api.get(`/agent/conversations/?page=${page}`);
    return response.data;
  },

  // Get conversation by ID
  getConversation: async (id) => {
    const response = await api.get(`/agent/conversations/${id}/`);
    return response.data;
  },

  // Send message
  sendMessage: async (conversationId, message) => {
    const response = await api.post(`/agent/conversations/${conversationId}/messages/`, {
      content: message,
    });
    return response.data;
  },

  // Create new conversation
  createConversation: async () => {
    const response = await api.post('/agent/conversations/');
    return response.data;
  },

  // Smart Analytics
  getSmartInsights: async (language = 'uk') => {
    const response = await api.get('/agent/smart-insights/', {
      params: { language },
    });
    return response.data;
  },

  // Voice Communication
  textToSpeech: async (text, language = 'uk', voiceId = null) => {
    const response = await api.post('/agent/tts/', {
      text,
      language,
      voice_id: voiceId,
    });
    return response.data;
  },

  speechToText: async (audioFile) => {
    const formData = new FormData();
    formData.append('audio', audioFile);

    const response = await api.post('/agent/stt/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

export const integrationsAPI = {
  // Get all integrations
  getIntegrations: async () => {
    const response = await api.get('/integrations/');
    return response.data;
  },

  // Connect Telegram
  connectTelegram: async (botToken) => {
    const response = await api.post('/integrations/telegram/connect/', {
      bot_token: botToken,
    });
    return response.data;
  },

  // Disconnect integration
  disconnectIntegration: async (id) => {
    const response = await api.delete(`/integrations/${id}/`);
    return response.data;
  },

  // Google Reviews
  getGoogleReviewsAuthUrl: async () => {
    const response = await api.get('/integrations/google-reviews/auth/');
    return response.data;
  },

  connectGoogleReviews: async (code) => {
    const response = await api.post('/integrations/google-reviews/callback/', { code });
    return response.data;
  },

  getReviewsSummary: async () => {
    const response = await api.get('/integrations/google-reviews/summary/');
    return response.data;
  },

  disconnectGoogleReviews: async () => {
    const response = await api.delete('/integrations/google-reviews/disconnect/');
    return response.data;
  },

  // Instagram Advanced
  connectInstagram: async (accessToken) => {
    const response = await api.post('/integrations/instagram/connect/', { access_token: accessToken });
    return response.data;
  },

  createInstagramEmbeddings: async () => {
    const response = await api.post('/integrations/instagram/create-embeddings/');
    return response.data;
  },

  getInstagramAnalytics: async (period = 'month') => {
    const response = await api.get('/integrations/instagram/analytics/', {
      params: { period },
    });
    return response.data;
  },

  getContentRecommendations: async () => {
    const response = await api.get('/integrations/instagram/content-recommendations/');
    return response.data;
  },

  disconnectInstagram: async () => {
    const response = await api.delete('/integrations/instagram/disconnect/');
    return response.data;
  },

  // Email Integration
  connectEmail: async (provider, credentials) => {
    const response = await api.post('/integrations/email/connect/', {
      provider,
      ...credentials,
    });
    return response.data;
  },

  getEmailAnalytics: async () => {
    const response = await api.get('/integrations/email/analytics/');
    return response.data;
  },

  disconnectEmail: async () => {
    const response = await api.delete('/integrations/email/disconnect/');
    return response.data;
  },
};

export const documentsAPI = {
  // Get documents
  getDocuments: async (page = 1) => {
    const response = await api.get(`/documents/?page=${page}`);
    return response.data;
  },

  // Upload document
  uploadDocument: async (file, metadata) => {
    const formData = new FormData();
    formData.append('file', file);
    Object.keys(metadata).forEach(key => {
      formData.append(key, metadata[key]);
    });

    const response = await api.post('/documents/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Delete document
  deleteDocument: async (id) => {
    const response = await api.delete(`/documents/${id}/`);
    return response.data;
  },
};

export const subscriptionsAPI = {
  // Get subscription info
  getSubscription: async () => {
    const response = await api.get('/subscriptions/current/');
    return response.data;
  },

  // Get plans
  getPlans: async () => {
    const response = await api.get('/subscriptions/plans/');
    return response.data;
  },

  // Subscribe to plan
  subscribe: async (planId, paymentMethodId) => {
    const response = await api.post('/subscriptions/subscribe/', {
      plan_id: planId,
      payment_method_id: paymentMethodId,
    });
    return response.data;
  },
};

export const notificationsAPI = {
  // Register push token
  registerPushToken: async (expoPushToken, deviceName = '', deviceType = 'mobile') => {
    const response = await api.post('/notifications/register-token/', {
      expo_push_token: expoPushToken,
      device_name: deviceName,
      device_type: deviceType,
    });
    return response.data;
  },

  // Unregister push token
  unregisterPushToken: async (expoPushToken) => {
    const response = await api.post('/notifications/unregister-token/', {
      expo_push_token: expoPushToken,
    });
    return response.data;
  },

  // Get notification settings
  getSettings: async () => {
    const response = await api.get('/notifications/settings/');
    return response.data;
  },

  // Update notification settings
  updateSettings: async (settings) => {
    const response = await api.put('/notifications/settings/', settings);
    return response.data;
  },

  // Get notification history
  getHistory: async (limit = 50, offset = 0) => {
    const response = await api.get('/notifications/history/', {
      params: { limit, offset },
    });
    return response.data;
  },

  // Send test notification
  sendTest: async () => {
    const response = await api.post('/notifications/test/');
    return response.data;
  },
};

export default api;
