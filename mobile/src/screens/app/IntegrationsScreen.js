import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Modal,
} from 'react-native';
import GoogleReviewsSetup from '../../components/integrations/GoogleReviewsSetup';
import InstagramAnalytics from '../../components/integrations/InstagramAnalytics';
import EmailSetup from '../../components/integrations/EmailSetup';

const INTEGRATIONS = [
  { id: 'telegram', name: 'Telegram', icon: '✈️', connected: false, color: '#0088cc', type: 'basic' },
  { id: 'whatsapp', name: 'WhatsApp', icon: '💬', connected: false, color: '#25D366', type: 'basic' },
  { id: 'instagram', name: 'Instagram', icon: '📷', connected: false, color: '#E4405F', type: 'advanced' },
  { id: 'google-reviews', name: 'Google Reviews', icon: '⭐', connected: false, color: '#FBBC04', type: 'advanced' },
  { id: 'email', name: 'Email', icon: '📧', connected: false, color: '#4285F4', type: 'advanced' },
  { id: 'facebook', name: 'Facebook', icon: '👥', connected: false, color: '#1877F2', type: 'basic' },
  { id: 'google-calendar', name: 'Google Calendar', icon: '📅', connected: false, color: '#4285F4', type: 'basic' },
  { id: 'google-sheets', name: 'Google Sheets', icon: '📊', connected: false, color: '#34A853', type: 'basic' },
];

const IntegrationsScreen = () => {
  const [selectedIntegration, setSelectedIntegration] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);

  const handleIntegrationPress = (integration) => {
    if (integration.type === 'advanced') {
      setSelectedIntegration(integration);
      setModalVisible(true);
    }
  };

  const handleCloseModal = () => {
    setModalVisible(false);
    setSelectedIntegration(null);
  };

  const renderIntegrationModal = () => {
    if (!selectedIntegration) return null;

    switch (selectedIntegration.id) {
      case 'google-reviews':
        return <GoogleReviewsSetup onClose={handleCloseModal} />;
      case 'instagram':
        return <InstagramAnalytics onClose={handleCloseModal} />;
      case 'email':
        return <EmailSetup onClose={handleCloseModal} />;
      default:
        return null;
    }
  };

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
          <IntegrationCard
            key={integration.id}
            integration={integration}
            onPress={() => handleIntegrationPress(integration)}
          />
        ))}
      </View>

      {/* Modal for advanced integrations */}
      <Modal
        visible={modalVisible}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={handleCloseModal}
      >
        {renderIntegrationModal()}
      </Modal>
    </ScrollView>
  );
};

const IntegrationCard = ({ integration, onPress }) => {
  const { name, icon, connected, color, type } = integration;

  return (
    <TouchableOpacity
      style={[styles.card, { borderColor: color }]}
      onPress={type === 'advanced' ? onPress : null}
      activeOpacity={type === 'advanced' ? 0.7 : 1}
    >
      <View style={[styles.iconContainer, { backgroundColor: color + '20' }]}>
        <Text style={styles.icon}>{icon}</Text>
      </View>

      <Text style={styles.integrationName}>{name}</Text>

      {type === 'advanced' && (
        <View style={styles.advancedBadge}>
          <Text style={styles.advancedBadgeText}>PRO</Text>
        </View>
      )}

      {connected ? (
        <View style={[styles.statusBadge, styles.connectedBadge]}>
          <Text style={styles.statusText}>Підключено</Text>
        </View>
      ) : (
        <View style={[styles.statusBadge, styles.connectButton]}>
          <Text style={[styles.statusText, styles.connectText]}>
            {type === 'advanced' ? 'Налаштувати' : 'Скоро'}
          </Text>
        </View>
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
    position: 'relative',
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
    textAlign: 'center',
  },
  advancedBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: '#fbbf24',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
  },
  advancedBadgeText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#fff',
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
