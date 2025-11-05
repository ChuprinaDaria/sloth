import api from './axios';

export const subscriptionAPI = {
  // Get all available plans
  getPlans: () => api.get('/subscriptions/plans/'),

  // Get current subscription
  getCurrentSubscription: () => api.get('/subscriptions/current/'),

  // Create Stripe checkout session
  createCheckout: (planId, billingCycle = 'monthly') =>
    api.post('/subscriptions/checkout/', {
      plan_id: planId,
      billing_cycle: billingCycle
    }),

  // Activate subscription with code
  activateCode: (code) => api.post('/subscriptions/activate-code/', { code }),

  // Cancel subscription
  cancelSubscription: () => api.post('/subscriptions/cancel/'),

  // Get usage stats
  getUsage: () => api.get('/subscriptions/usage/'),
};
