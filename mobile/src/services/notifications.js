import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import { notificationsAPI } from './api';

// Configure notification behavior
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

/**
 * Register for push notifications and get Expo push token
 */
export async function registerForPushNotificationsAsync() {
  let token;

  if (Device.isDevice) {
    // Check existing permissions
    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;

    // Ask for permissions if not granted
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }

    if (finalStatus !== 'granted') {
      console.warn('Failed to get push token for push notification!');
      return null;
    }

    // Get the Expo push token
    token = (await Notifications.getExpoPushTokenAsync()).data;
    console.log('Expo Push Token:', token);

    // Register token with backend
    try {
      const deviceName = Device.modelName || 'Unknown Device';
      const deviceType = Device.deviceType === Device.DeviceType.TABLET ? 'tablet' : 'mobile';

      await notificationsAPI.registerPushToken(token, deviceName, deviceType);
      console.log('Push token registered with backend');
    } catch (error) {
      console.error('Failed to register push token with backend:', error);
    }
  } else {
    console.warn('Must use physical device for Push Notifications');
  }

  // Configure notification channels for Android
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('critical', {
      name: 'Критичні повідомлення',
      description: 'VIP клієнти, відгуки, проблеми з інтеграціями',
      importance: Notifications.AndroidImportance.HIGH,
      vibrationPattern: [0, 250, 250, 250],
      sound: 'default',
      enableLights: true,
      lightColor: '#FF0000',
    });

    await Notifications.setNotificationChannelAsync('important', {
      name: 'Важливі повідомлення',
      description: 'Аналітика, свята, досягнення',
      importance: Notifications.AndroidImportance.DEFAULT,
      vibrationPattern: [0, 250],
      sound: 'default',
    });

    await Notifications.setNotificationChannelAsync('useful', {
      name: 'Корисні повідомлення',
      description: 'Звіти, рекомендації',
      importance: Notifications.AndroidImportance.LOW,
      sound: null,
    });
  }

  return token;
}

/**
 * Unregister push notifications
 */
export async function unregisterPushNotifications() {
  try {
    const token = (await Notifications.getExpoPushTokenAsync()).data;
    if (token) {
      await notificationsAPI.unregisterPushToken(token);
      console.log('Push token unregistered');
    }
  } catch (error) {
    console.error('Failed to unregister push token:', error);
  }
}

/**
 * Handle notification received while app is in foreground
 */
export function addNotificationReceivedListener(callback) {
  return Notifications.addNotificationReceivedListener((notification) => {
    console.log('Notification received:', notification);
    callback(notification);
  });
}

/**
 * Handle notification tap (when user opens the notification)
 */
export function addNotificationResponseReceivedListener(callback) {
  return Notifications.addNotificationResponseReceivedListener((response) => {
    console.log('Notification tapped:', response);
    const data = response.notification.request.content.data;
    callback(data);
  });
}

/**
 * Get badge count
 */
export async function getBadgeCount() {
  return await Notifications.getBadgeCountAsync();
}

/**
 * Set badge count
 */
export async function setBadgeCount(count) {
  await Notifications.setBadgeCountAsync(count);
}

/**
 * Clear badge
 */
export async function clearBadge() {
  await Notifications.setBadgeCountAsync(0);
}

/**
 * Dismiss all notifications
 */
export async function dismissAllNotifications() {
  await Notifications.dismissAllNotificationsAsync();
}

/**
 * Schedule a local notification (for testing)
 */
export async function scheduleLocalNotification(title, body, data = {}) {
  await Notifications.scheduleNotificationAsync({
    content: {
      title,
      body,
      data,
      sound: true,
    },
    trigger: null, // null means immediately
  });
}

/**
 * Navigate to screen based on notification data
 */
export function handleNotificationNavigation(navigation, notificationData) {
  const { action, ...params } = notificationData;

  switch (action) {
    case 'open_conversation':
      navigation.navigate('Conversations', params);
      break;

    case 'open_integrations':
      navigation.navigate('Integrations', params);
      break;

    case 'open_reviews':
      // Navigate to reviews section (if exists)
      navigation.navigate('Home', params);
      break;

    case 'open_analytics':
      navigation.navigate('Home', params);
      break;

    case 'open_instagram':
      navigation.navigate('Integrations', params);
      break;

    case 'open_profile':
      navigation.navigate('Profile', params);
      break;

    case 'open_home':
    default:
      navigation.navigate('Home', params);
      break;
  }
}

export default {
  registerForPushNotificationsAsync,
  unregisterPushNotifications,
  addNotificationReceivedListener,
  addNotificationResponseReceivedListener,
  getBadgeCount,
  setBadgeCount,
  clearBadge,
  dismissAllNotifications,
  scheduleLocalNotification,
  handleNotificationNavigation,
};
