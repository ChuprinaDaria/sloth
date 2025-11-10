import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { agentAPI } from '../../services/api';

const SmartAnalytics = () => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadInsights();
  }, []);

  const loadInsights = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await agentAPI.getSmartInsights('uk');
      setInsights(response);
    } catch (err) {
      console.error('Error loading insights:', err);
      setError(err.response?.data?.error || 'Не вдалося завантажити аналітику');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadInsights();
  };

  const getInsightIcon = (type) => {
    const icons = {
      trend: '📈',
      warning: '⚠️',
      time: '🕐',
      clients: '👥',
      recommendation: '💡',
      holiday: '📅',
      pricing: '💰',
      vip: '⭐',
    };
    return icons[type] || '🧠';
  };

  const getInsightColor = (type) => {
    const colors = {
      trend: '#3b82f6',
      warning: '#f97316',
      time: '#a855f7',
      clients: '#10b981',
      recommendation: '#eab308',
      holiday: '#6366f1',
      pricing: '#059669',
      vip: '#f59e0b',
    };
    return colors[type] || '#6b7280';
  };

  if (loading && !refreshing) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headerIcon}>🧠</Text>
          <Text style={styles.headerTitle}>Розумна аналітика</Text>
        </View>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#6366f1" />
          <Text style={styles.loadingText}>Аналіз даних...</Text>
        </View>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headerIcon}>🧠</Text>
          <Text style={styles.headerTitle}>Розумна аналітика</Text>
        </View>
        <View style={styles.errorContainer}>
          <Text style={styles.errorIcon}>⚠️</Text>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={loadInsights}>
            <Text style={styles.retryButtonText}>Спробувати знову</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  if (!insights || insights.insights?.length === 0) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headerIcon}>🧠</Text>
          <Text style={styles.headerTitle}>Розумна аналітика</Text>
        </View>
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyIcon}>🧠</Text>
          <Text style={styles.emptyText}>Поки немає даних</Text>
          <Text style={styles.emptyDescription}>
            Почніть використовувати Sloth AI для отримання персональних рекомендацій
          </Text>
        </View>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={styles.headerIcon}>🧠</Text>
          <Text style={styles.headerTitle}>Розумна аналітика</Text>
        </View>
        <TouchableOpacity onPress={loadInsights}>
          <Text style={styles.refreshButton}>🔄</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.insightsContainer}>
        {insights.insights.map((insight, index) => {
          const icon = getInsightIcon(insight.type);
          const color = getInsightColor(insight.type);

          return (
            <View
              key={index}
              style={[
                styles.insightCard,
                { borderLeftColor: color, borderLeftWidth: 4 },
              ]}
            >
              <View style={styles.insightHeader}>
                <Text style={styles.insightIcon}>{icon}</Text>
                <Text style={styles.insightTitle}>{insight.title}</Text>
              </View>
              <Text style={styles.insightMessage}>{insight.message}</Text>
              {insight.action && (
                <View style={styles.actionContainer}>
                  <Text style={styles.actionIcon}>💡</Text>
                  <Text style={styles.actionText}>{insight.action}</Text>
                </View>
              )}
            </View>
          );
        })}
      </View>

      {insights.summary && (
        <View style={styles.summaryContainer}>
          <Text style={styles.summaryTitle}>Підсумок</Text>
          <Text style={styles.summaryText}>{insights.summary}</Text>
        </View>
      )}

      <Text style={styles.footerText}>
        Згенеровано AI • Оновлено: {new Date(insights.generated_at).toLocaleString('uk-UA')}
      </Text>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  headerIcon: {
    fontSize: 24,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  refreshButton: {
    fontSize: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6b7280',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  errorIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  errorText: {
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#6366f1',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: 16,
    opacity: 0.5,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 8,
  },
  emptyDescription: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
  },
  insightsContainer: {
    padding: 16,
    gap: 12,
  },
  insightCard: {
    backgroundColor: '#f9fafb',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  insightHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
    gap: 8,
  },
  insightIcon: {
    fontSize: 20,
  },
  insightTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    flex: 1,
  },
  insightMessage: {
    fontSize: 14,
    color: '#4b5563',
    lineHeight: 20,
  },
  actionContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
    padding: 12,
    backgroundColor: '#fff',
    borderRadius: 8,
    gap: 8,
  },
  actionIcon: {
    fontSize: 16,
  },
  actionText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#1f2937',
    flex: 1,
  },
  summaryContainer: {
    margin: 16,
    marginTop: 8,
    padding: 16,
    backgroundColor: '#f3f4f6',
    borderRadius: 12,
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 8,
  },
  summaryText: {
    fontSize: 14,
    color: '#4b5563',
    lineHeight: 20,
  },
  footerText: {
    fontSize: 12,
    color: '#9ca3af',
    textAlign: 'center',
    padding: 16,
  },
});

export default SmartAnalytics;
