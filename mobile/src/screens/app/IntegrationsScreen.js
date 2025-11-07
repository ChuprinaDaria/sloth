import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';

const INTEGRATIONS = [
  { id: '1', name: 'Telegram', icon: '✈️', connected: true, color: '#0088cc' },
  { id: '2', name: 'WhatsApp', icon: '💬', connected: true, color: '#25D366' },
  { id: '3', name: 'Instagram', icon: '📷', connected: false, color: '#E4405F' },
  { id: '4', name: 'Facebook', icon: '👥', connected: false, color: '#1877F2' },
  { id: '5', name: 'Google Calendar', icon: '📅', connected: false, color: '#4285F4' },
  { id: '6', name: 'Google Sheets', icon: '📊', connected: false, color: '#34A853' },
];

const IntegrationsScreen = () => {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Інтеграції</Text>
        <Text style={styles.headerSubtitle}>
          Підключіть ваші улюблені сервіси
        </Text>
      </View>

      <View style={styles.integrationsGrid}>
        {INTEGRATIONS.map((integration) => (
          <IntegrationCard key={integration.id} integration={integration} />
        ))}
      </View>
    </ScrollView>
  );
};

const IntegrationCard = ({ integration }) => {
  const { name, icon, connected, color } = integration;

  return (
    <TouchableOpacity style={[styles.card, { borderColor: color }]}>
      <View style={[styles.iconContainer, { backgroundColor: color + '20' }]}>
        <Text style={styles.icon}>{icon}</Text>
      </View>

      <Text style={styles.integrationName}>{name}</Text>

      {connected ? (
        <View style={[styles.statusBadge, styles.connectedBadge]}>
          <Text style={styles.statusText}>Підключено</Text>
        </View>
      ) : (
        <TouchableOpacity style={[styles.statusBadge, styles.connectButton]}>
          <Text style={[styles.statusText, styles.connectText]}>Підключити</Text>
        </TouchableOpacity>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6b7280',
  },
  integrationsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 12,
    gap: 12,
  },
  card: {
    width: '47%',
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    borderWidth: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  iconContainer: {
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  icon: {
    fontSize: 32,
  },
  integrationName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 12,
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    minWidth: 100,
    alignItems: 'center',
  },
  connectedBadge: {
    backgroundColor: '#d1fae5',
  },
  connectButton: {
    backgroundColor: '#6366f1',
  },
  statusText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#059669',
  },
  connectText: {
    color: '#fff',
  },
});

export default IntegrationsScreen;
