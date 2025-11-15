import api from './axios';

export const bookingPreferencesAPI = {
  // Get booking preferences
  getPreferences: () => api.get('/auth/booking-preferences/'),

  // Update booking preferences
  updatePreferences: (data) => api.put('/auth/booking-preferences/', data),
};

export default bookingPreferencesAPI;
