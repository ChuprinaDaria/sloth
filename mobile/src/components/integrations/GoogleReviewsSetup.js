import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Linking,
} from 'react-native';
import { integrationsAPI } from '../../services/api';

const GoogleReviewsSetup = ({ onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      const data = await integrationsAPI.getReviewsSummary();
      if (data) {
        setConnected(true);
        setSummary(data);
      }
    } catch (err) {
      // Not connected
      setConnected(false);
    }
  };

  const handleConnect = async () => {
    try {
      setLoading(true);
      const { auth_url } = await integrationsAPI.getGoogleReviewsAuthUrl();

      // Open OAuth URL in browser
      const supported = await Linking.canOpenURL(auth_url);
      if (supported) {
        await Linking.openURL(auth_url);
        Alert.alert(
          'Авторизація',
          'Після авторизації в браузері поверніться до додатку та натисніть "Перевірити підключення"',
          [
            {
              text: 'OK',
              onPress: () => {
                // User will manually check connection
              },
            },
          ]
        );
      } else {
        Alert.alert('Помилка', 'Не вдалося відкрити браузер');
      }
    } catch (err) {
      console.error('Error connecting Google Reviews:', err);
      Alert.alert('Помилка', err.response?.data?.error || 'Не вдалося підключитися');
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    Alert.alert(
      'Відключити інтеграцію?',
      'Ви впевнені, що хочете відключити Google Reviews?',
      [
        { text: 'Скасувати', style: 'cancel' },
        {
          text: 'Відключити',
          style: 'destructive',
          onPress: async () => {
            try {
              setLoading(true);
              await integrationsAPI.disconnectGoogleReviews();
              setConnected(false);
              setSummary(null);
              Alert.alert('Успіх', 'Google Reviews відключено');
            } catch (err) {
              Alert.alert('Помилка', 'Не вдалося відключити інтеграцію');
            } finally {
              setLoading(false);
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#6366f1" />
        <Text style={styles.loadingText}>Завантаження...</Text>
      </View>
    );
  }

  if (connected && summary) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.icon}>⭐</Text>
          <Text style={styles.title}>Google Reviews</Text>
        </View>

        <View style={styles.connectedBadge}>
          <Text style={styles.connectedText}>✓ Підключено</Text>
        </View>

        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{summary.total_reviews || 0}</Text>
            <Text style={styles.statLabel}>Відгуків</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {summary.average_rating?.toFixed(1) || '0.0'}
            </Text>
            <Text style={styles.statLabel}>Рейтинг</Text>
          </View>
        </View>

        {summary.recent_reviews && summary.recent_reviews.length > 0 && (
          <View style={styles.reviewsSection}>
            <Text style={styles.sectionTitle}>Останні відгуки</Text>
            {summary.recent_reviews.slice(0, 3).map((review, index) => (
              <View key={index} style={styles.reviewCard}>
                <View style={styles.reviewHeader}>
                  <Text style={styles.reviewAuthor}>{review.author}</Text>
                  <Text style={styles.reviewRating}>
                    {'⭐'.repeat(review.rating)}
                  </Text>
                </View>
                <Text style={styles.reviewText} numberOfLines={3}>
                  {review.text}
                </Text>
              </View>
            ))}
          </View>
        )}

        <View style={styles.infoBox}>
          <Text style={styles.infoIcon}>💡</Text>
          <Text style={styles.infoText}>
            AI аналізує ваші відгуки та використовує їх для кращого спілкування з клієнтами
          </Text>
        </View>

        <TouchableOpacity
          style={styles.disconnectButton}
          onPress={handleDisconnect}
        >
          <Text style={styles.disconnectButtonText}>Відключити</Text>
        </TouchableOpacity>

        {onClose && (
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Text style={styles.closeButtonText}>Закрити</Text>
          </TouchableOpacity>
        )}
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.icon}>⭐</Text>
        <Text style={styles.title}>Google Reviews</Text>
      </View>

      <Text style={styles.description}>
        Підключіть Google My Business для аналізу відгуків та покращення роботи з клієнтами
      </Text>

      <View style={styles.featuresContainer}>
        <View style={styles.feature}>
          <Text style={styles.featureIcon}>✓</Text>
          <Text style={styles.featureText}>Аналіз відгуків за допомогою AI</Text>
        </View>
        <View style={styles.feature}>
          <Text style={styles.featureIcon}>✓</Text>
          <Text style={styles.featureText}>Рекомендації для роботи із запереченнями</Text>
        </View>
        <View style={styles.feature}>
          <Text style={styles.featureIcon}>✓</Text>
          <Text style={styles.featureText}>Розумна аналітика відгуків</Text>
        </View>
        <View style={styles.feature}>
          <Text style={styles.featureIcon}>✓</Text>
          <Text style={styles.featureText}>Автоматичне покращення спілкування</Text>
        </View>
      </View>

      <TouchableOpacity
        style={styles.connectButton}
        onPress={handleConnect}
        disabled={loading}
      >
        <Text style={styles.connectButtonText}>
          {loading ? 'Підключення...' : 'Підключити Google Reviews'}
        </Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.checkButton}
        onPress={checkConnection}
      >
        <Text style={styles.checkButtonText}>Перевірити підключення</Text>
      </TouchableOpacity>

      {onClose && (
        <TouchableOpacity style={styles.closeButton} onPress={onClose}>
          <Text style={styles.closeButtonText}>Закрити</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 20,
  },
  icon: {
    fontSize: 48,
    marginBottom: 12,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  description: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 24,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
  },
  connectedBadge: {
    backgroundColor: '#d1fae5',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    alignSelf: 'center',
    marginBottom: 24,
  },
  connectedText: {
    color: '#059669',
    fontWeight: '600',
    fontSize: 14,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 24,
  },
  statCard: {
    alignItems: 'center',
    backgroundColor: '#f9fafb',
    padding: 20,
    borderRadius: 12,
    minWidth: 120,
  },
  statValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#6366f1',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 14,
    color: '#6b7280',
  },
  reviewsSection: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 12,
  },
  reviewCard: {
    backgroundColor: '#f9fafb',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  reviewHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  reviewAuthor: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1f2937',
  },
  reviewRating: {
    fontSize: 12,
  },
  reviewText: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
  },
  featuresContainer: {
    marginBottom: 24,
  },
  feature: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  featureIcon: {
    fontSize: 20,
    color: '#10b981',
    marginRight: 12,
  },
  featureText: {
    fontSize: 16,
    color: '#4b5563',
  },
  infoBox: {
    flexDirection: 'row',
    backgroundColor: '#fef3c7',
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
  },
  infoIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#92400e',
    lineHeight: 20,
  },
  connectButton: {
    backgroundColor: '#6366f1',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  connectButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  checkButton: {
    backgroundColor: '#f3f4f6',
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  checkButtonText: {
    color: '#6366f1',
    fontSize: 14,
    fontWeight: '600',
  },
  disconnectButton: {
    backgroundColor: '#fee2e2',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  disconnectButtonText: {
    color: '#dc2626',
    fontSize: 16,
    fontWeight: '600',
  },
  closeButton: {
    paddingVertical: 12,
    alignItems: 'center',
  },
  closeButtonText: {
    color: '#6b7280',
    fontSize: 16,
  },
});

export default GoogleReviewsSetup;
