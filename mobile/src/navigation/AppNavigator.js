import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import HomeScreen from '../screens/app/HomeScreen';
import ConversationsScreen from '../screens/app/ConversationsScreen';
import IntegrationsScreen from '../screens/app/IntegrationsScreen';
import ProfileScreen from '../screens/app/ProfileScreen';

const Tab = createBottomTabNavigator();

const AppNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Home') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Conversations') {
            iconName = focused ? 'chatbubbles' : 'chatbubbles-outline';
          } else if (route.name === 'Integrations') {
            iconName = focused ? 'extension-puzzle' : 'extension-puzzle-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#6366f1',
        tabBarInactiveTintColor: 'gray',
        headerStyle: {
          backgroundColor: '#6366f1',
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
      })}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{ title: 'Головна' }}
      />
      <Tab.Screen
        name="Conversations"
        component={ConversationsScreen}
        options={{ title: 'Чати' }}
      />
      <Tab.Screen
        name="Integrations"
        component={IntegrationsScreen}
        options={{ title: 'Інтеграції' }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{ title: 'Профіль' }}
      />
    </Tab.Navigator>
  );
};

export default AppNavigator;
