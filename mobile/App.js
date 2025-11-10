import React, { useEffect, useRef } from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { NavigationContainer } from '@react-navigation/native';
import { useAuthStore } from './src/stores/authStore';
import AuthNavigator from './src/navigation/AuthNavigator';
import AppNavigator from './src/navigation/AppNavigator';
import {
  registerForPushNotificationsAsync,
  addNotificationReceivedListener,
  addNotificationResponseReceivedListener,
  handleNotificationNavigation,
} from './src/services/notifications';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      staleTime: 30000, // 30 seconds
    },
  },
});

export default function App() {
  const { isAuthenticated } = useAuthStore();
  const navigationRef = useRef(null);
  const notificationListener = useRef();
  const responseListener = useRef();

  useEffect(() => {
    if (isAuthenticated) {
      // Register for push notifications
      registerForPushNotificationsAsync().catch((error) => {
        console.error('Error registering for push notifications:', error);
      });

      // Listen for notifications received while app is in foreground
      notificationListener.current = addNotificationReceivedListener((notification) => {
        console.log('Notification received in foreground:', notification);
        // You can show a custom in-app notification here if desired
      });

      // Listen for user tapping on notification
      responseListener.current = addNotificationResponseReceivedListener((notificationData) => {
        console.log('Notification tapped:', notificationData);

        // Navigate to appropriate screen based on notification action
        if (navigationRef.current) {
          handleNotificationNavigation(navigationRef.current, notificationData);
        }
      });

      return () => {
        // Cleanup listeners
        if (notificationListener.current) {
          notificationListener.current.remove();
        }
        if (responseListener.current) {
          responseListener.current.remove();
        }
      };
    }
  }, [isAuthenticated]);

  return (
    <QueryClientProvider client={queryClient}>
      <SafeAreaProvider>
        <NavigationContainer ref={navigationRef}>
          {isAuthenticated ? <AppNavigator /> : <AuthNavigator />}
        </NavigationContainer>
        <StatusBar style="auto" />
      </SafeAreaProvider>
    </QueryClientProvider>
  );
}
