import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { integrationsAPI } from '../../services/api';

const InstagramAnalytics = ({ onClose }) => {
  const [analytics, setAnalytics] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('month');
  const [activeTab, setActiveTab] = useState('analytics');

  useEffect(() => {
    loadData();
  }, [period]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [analyticsData, recommendationsData] = await Promise.all([
        integrationsAPI.getInstagramAnalytics(period),
        integrationsAPI.getContentRecommendations(),
      ]);
      setAnalytics(analyticsData);
      setRecommendations(recommendationsData);
    } catch (err) {
      console.error('Error loading Instagram data:', err);
      Alert.alert('Помилка', 'Не вдалося завантажити дані Instagram');
    } finally {
      setLoading(false);
    }
  };

  const createEmbeddings = async () => {
    Alert.alert(
      'Створити ембедінги?',
      'Це може зайняти кілька хвилин. AI проаналізує всі ваші пости для покращення рекомендацій.',
      [
        { text: 'Скасувати', style: 'cancel' },
        {
          text: 'Створити',
          onPress: async () => {
            try {
              setLoading(true);
              await integrationsAPI.createInstagramEmbeddings();
              Alert.alert('Успіх', 'Ембедінги створено! Тепер AI може краще розуміти ваш контент');
              loadData();
            } catch (err) {
              Alert.alert('Помилка', err.response?.data?.error || 'Не вдалося створити ембедінги');
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
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#E4405F" />
        <Text style={styles.loadingText}>Завантаження аналітики...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerIcon}>📷</Text>
        <Text style={styles.headerTitle}>Instagram Analytics</Text>
      </View>

      {/* Tabs */}
      <View style={styles.tabs}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'analytics' && styles.activeTab]}
          onPress={() => setActiveTab('analytics')}
        >
          <Text style={[styles.tabText, activeTab === 'analytics' && styles.activeTabText]}>
            Аналітика
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'recommendations' && styles.activeTab]}
          onPress={() => setActiveTab('recommendations')}
        >
          <Text style={[styles.tabText, activeTab === 'recommendations' && styles.activeTabText]}>
            Рекомендації
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content}>
        {activeTab === 'analytics' ? (
          <>
            {/* Period Selector */}
            <View style={styles.periodSelector}>
              {['week', 'month', 'year'].map((p) => (
                <TouchableOpacity
                  key={p}
                  style={[styles.periodButton, period === p && styles.activePeriodButton]}
                  onPress={() => setPeriod(p)}
                >
                  <Text style={[styles.periodButtonText, period === p && styles.activePeriodButtonText]}>
                    {p === 'week' ? 'Тиждень' : p === 'month' ? 'Місяць' : 'Рік'}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            {analytics ? (
              <>
                {/* Key Metrics */}
                <View style={styles.metricsGrid}>
                  <View style={styles.metricCard}>
                    <Text style={styles.metricValue}>{analytics.total_posts || 0}</Text>
                    <Text style={styles.metricLabel}>Постів</Text>
                  </View>
                  <View style={styles.metricCard}>
                    <Text style={styles.metricValue}>
                      {analytics.engagement_rate?.toFixed(1) || '0.0'}%
                    </Text>
                    <Text style={styles.metricLabel}>Залученість</Text>
                  </View>
                  <View style={styles.metricCard}>
                    <Text style={styles.metricValue}>{analytics.total_likes || 0}</Text>
                    <Text style={styles.metricLabel}>Лайків</Text>
                  </View>
                  <View style={styles.metricCard}>
                    <Text style={styles.metricValue}>{analytics.total_comments || 0}</Text>
                    <Text style={styles.metricLabel}>Коментарів</Text>
                  </View>
                </View>

                {/* Best Posts */}
                {analytics.best_posts && analytics.best_posts.length > 0 && (
                  <View style={styles.section}>
                    <Text style={styles.sectionTitle}>🏆 Найкращі пости</Text>
                    {analytics.best_posts.slice(0, 3).map((post, index) => (
                      <View key={index} style={styles.postCard}>
                        <View style={styles.postHeader}>
                          <Text style={styles.postRank}>#{index + 1}</Text>
                          <Text style={styles.postEngagement}>
                            {post.engagement} взаємодій
                          </Text>
                        </View>
                        <Text style={styles.postCaption} numberOfLines={2}>
                          {post.caption || 'Без опису'}
                        </Text>
                        <View style={styles.postStats}>
                          <Text style={styles.postStat}>❤️ {post.likes}</Text>
                          <Text style={styles.postStat}>💬 {post.comments}</Text>
                        </View>
                      </View>
                    ))}
                  </View>
                )}

                {/* Top Hashtags */}
                {analytics.top_hashtags && analytics.top_hashtags.length > 0 && (
                  <View style={styles.section}>
                    <Text style={styles.sectionTitle}>#️⃣ Популярні хештеги</Text>
                    <View style={styles.hashtagsContainer}>
                      {analytics.top_hashtags.slice(0, 10).map((hashtag, index) => (
                        <View key={index} style={styles.hashtagBadge}>
                          <Text style={styles.hashtagText}>#{hashtag.tag}</Text>
                          <Text style={styles.hashtagCount}>{hashtag.count}</Text>
                        </View>
                      ))}
                    </View>
                  </View>
                )}

                {/* Posting Pattern */}
                {analytics.posting_pattern && (
                  <View style={styles.section}>
                    <Text style={styles.sectionTitle}>📊 Активність</Text>
                    <View style={styles.patternCard}>
                      <Text style={styles.patternText}>
                        Найкращий час для публікації: <Text style={styles.patternBold}>
                          {analytics.posting_pattern.best_time || 'Немає даних'}
                        </Text>
                      </Text>
                      <Text style={styles.patternText}>
                        Середня залученість: <Text style={styles.patternBold}>
                          {analytics.posting_pattern.avg_engagement || 0} взаємодій
                        </Text>
                      </Text>
                    </View>
                  </View>
                )}
              </>
            ) : (
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyText}>Немає даних для відображення</Text>
              </View>
            )}
          </>
        ) : (
          <>
            {/* Recommendations Tab */}
            {recommendations ? (
              <>
                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>💡 Рекомендації контенту</Text>
                  {recommendations.recommendations?.map((rec, index) => (
                    <View key={index} style={styles.recommendationCard}>
                      <View style={styles.recommendationHeader}>
                        <Text style={styles.recommendationTitle}>{rec.topic}</Text>
                        <View style={[
                          styles.priorityBadge,
                          { backgroundColor: rec.priority === 'high' ? '#fee2e2' : rec.priority === 'medium' ? '#fef3c7' : '#dbeafe' }
                        ]}>
                          <Text style={[
                            styles.priorityText,
                            { color: rec.priority === 'high' ? '#dc2626' : rec.priority === 'medium' ? '#d97706' : '#2563eb' }
                          ]}>
                            {rec.priority === 'high' ? 'Високий' : rec.priority === 'medium' ? 'Середній' : 'Низький'}
                          </Text>
                        </View>
                      </View>
                      <Text style={styles.recommendationReason}>{rec.reason}</Text>
                      {rec.example_questions && rec.example_questions.length > 0 && (
                        <View style={styles.questionsContainer}>
                          <Text style={styles.questionsTitle}>Питання клієнтів:</Text>
                          {rec.example_questions.slice(0, 2).map((q, i) => (
                            <Text key={i} style={styles.questionText}>• {q}</Text>
                          ))}
                        </View>
                      )}
                    </View>
                  ))}
                </View>

                {recommendations.summary && (
                  <View style={styles.summaryCard}>
                    <Text style={styles.summaryTitle}>📋 Підсумок</Text>
                    <Text style={styles.summaryText}>{recommendations.summary}</Text>
                  </View>
                )}
              </>
            ) : (
              <View style={styles.emptyContainer}>
                <Text style={styles.emptyText}>Немає рекомендацій</Text>
              </View>
            )}
          </>
        )}
      </ScrollView>

      {/* Actions */}
      <View style={styles.actions}>
        <TouchableOpacity style={styles.embeddingsButton} onPress={createEmbeddings}>
          <Text style={styles.embeddingsButtonText}>🔄 Оновити AI аналіз</Text>
        </TouchableOpacity>
        {onClose && (
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Text style={styles.closeButtonText}>Закрити</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6b7280',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  headerIcon: {
    fontSize: 32,
    marginRight: 12,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  tabs: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
  },
  activeTab: {
    borderBottomWidth: 2,
    borderBottomColor: '#E4405F',
  },
  tabText: {
    fontSize: 16,
    color: '#6b7280',
  },
  activeTabText: {
    color: '#E4405F',
    fontWeight: '600',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  periodSelector: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 20,
    gap: 8,
  },
  periodButton: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    backgroundColor: '#f3f4f6',
    alignItems: 'center',
  },
  activePeriodButton: {
    backgroundColor: '#E4405F',
  },
  periodButtonText: {
    fontSize: 14,
    color: '#6b7280',
  },
  activePeriodButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 20,
  },
  metricCard: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: '#f9fafb',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#E4405F',
    marginBottom: 4,
  },
  metricLabel: {
    fontSize: 12,
    color: '#6b7280',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 12,
  },
  postCard: {
    backgroundColor: '#f9fafb',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  postHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  postRank: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#E4405F',
  },
  postEngagement: {
    fontSize: 12,
    color: '#6b7280',
  },
  postCaption: {
    fontSize: 14,
    color: '#4b5563',
    marginBottom: 8,
  },
  postStats: {
    flexDirection: 'row',
    gap: 16,
  },
  postStat: {
    fontSize: 12,
    color: '#6b7280',
  },
  hashtagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  hashtagBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E4405F',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    gap: 6,
  },
  hashtagText: {
    fontSize: 12,
    color: '#fff',
    fontWeight: '600',
  },
  hashtagCount: {
    fontSize: 12,
    color: '#fff',
    opacity: 0.8,
  },
  patternCard: {
    backgroundColor: '#f9fafb',
    padding: 16,
    borderRadius: 12,
  },
  patternText: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 8,
  },
  patternBold: {
    fontWeight: '600',
    color: '#1f2937',
  },
  recommendationCard: {
    backgroundColor: '#f9fafb',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  recommendationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  recommendationTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    flex: 1,
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  priorityText: {
    fontSize: 12,
    fontWeight: '600',
  },
  recommendationReason: {
    fontSize: 14,
    color: '#4b5563',
    marginBottom: 12,
  },
  questionsContainer: {
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
  },
  questionsTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6b7280',
    marginBottom: 6,
  },
  questionText: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 4,
  },
  summaryCard: {
    backgroundColor: '#fef3c7',
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#92400e',
    marginBottom: 8,
  },
  summaryText: {
    fontSize: 14,
    color: '#92400e',
    lineHeight: 20,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
  },
  emptyText: {
    fontSize: 16,
    color: '#6b7280',
  },
  actions: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  embeddingsButton: {
    backgroundColor: '#E4405F',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 8,
  },
  embeddingsButtonText: {
    color: '#fff',
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

export default InstagramAnalytics;
