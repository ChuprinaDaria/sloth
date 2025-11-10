import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Modal,
} from 'react-native';
import { useAuthStore } from '../../stores/authStore';
import SmartAnalytics from '../../components/analytics/SmartAnalytics';

const HomeScreen = ({ navigation }) => {
  const user = useAuthStore((state) => state.user);
  const [analyticsVisible, setAnalyticsVisible] = useState(false);

  return (
    <>
      <ScrollView style={styles.container}>
        {/* Welcome Section */}
        <View style={styles.welcomeSection}>
          <Text style={styles.welcomeText}>
            Привіт, {user?.first_name || 'Користувач'}! 👋
          </Text>
          <Text style={styles.subtitle}>Що бажаєте зробити сьогодні?</Text>
        </View>

        {/* Quick Actions */}
        <View style={styles.quickActions}>
          <QuickActionCard
            icon="💬"
            title="Новий чат"
            description="Почати розмову з AI"
            onPress={() => navigation.navigate('Conversations')}
          />
          <QuickActionCard
            icon="🔌"
            title="Інтеграції"
            description="Підключити Telegram, WhatsApp"
            onPress={() => navigation.navigate('Integrations')}
          />
          <QuickActionCard
            icon="📄"
            title="Документи"
            description="Завантажити та аналізувати"
            onPress={() => {}}
          />
          <QuickActionCard
            icon="🧠"
            title="Розумна аналітика"
            description="AI-рекомендації та інсайти"
            onPress={() => setAnalyticsVisible(true)}
          />
        </View>

        {/* Stats Section */}
        <View style={styles.statsSection}>
          <Text style={styles.sectionTitle}>Статистика</Text>
          <View style={styles.statsGrid}>
            <StatCard title="Чатів" value="24" icon="💬" />
            <StatCard title="Повідомлень" value="156" icon="📨" />
            <StatCard title="Інтеграцій" value="3" icon="🔌" />
            <StatCard title="Документів" value="12" icon="📄" />
          </View>
        </View>

        {/* Recent Activity */}
        <View style={styles.recentSection}>
          <Text style={styles.sectionTitle}>Остання активність</Text>
          <ActivityItem
            title="Telegram бот активовано"
            time="2 години тому"
            icon="🤖"
          />
          <ActivityItem
            title="Нова розмова розпочата"
            time="5 годин тому"
            icon="💬"
          />
          <ActivityItem
            title="Документ завантажено"
            time="Вчора"
            icon="📄"
          />
        </View>
      </ScrollView>

      {/* Smart Analytics Modal */}
      <Modal
        visible={analyticsVisible}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setAnalyticsVisible(false)}
      >
        <View style={styles.modalContainer}>
          <SmartAnalytics />
          <TouchableOpacity
            style={styles.closeModalButton}
            onPress={() => setAnalyticsVisible(false)}
          >
            <Text style={styles.closeModalButtonText}>Закрити</Text>
          </TouchableOpacity>
        </View>
      </Modal>
    </>
  );
};

const QuickActionCard = ({ icon, title, description, onPress }) => (
  <TouchableOpacity style={styles.actionCard} onPress={onPress}>
    <Text style={styles.actionIcon}>{icon}</Text>
    <Text style={styles.actionTitle}>{title}</Text>
    <Text style={styles.actionDescription}>{description}</Text>
  </TouchableOpacity>
);

const StatCard = ({ title, value, icon }) => (
  <View style={styles.statCard}>
    <Text style={styles.statIcon}>{icon}</Text>
    <Text style={styles.statValue}>{value}</Text>
    <Text style={styles.statTitle}>{title}</Text>
  </View>
);

const ActivityItem = ({ title, time, icon }) => (
  <View style={styles.activityItem}>
    <Text style={styles.activityIcon}>{icon}</Text>
    <View style={styles.activityContent}>
      <Text style={styles.activityTitle}>{title}</Text>
      <Text style={styles.activityTime}>{time}</Text>
    </View>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  welcomeSection: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
  },
  quickActions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 12,
    gap: 12,
  },
  actionCard: {
    width: '47%',
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  actionIcon: {
    fontSize: 40,
    marginBottom: 8,
  },
  actionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
    textAlign: 'center',
  },
  actionDescription: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
  },
  statsSection: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  statCard: {
    width: '47%',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  statIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#6366f1',
    marginBottom: 4,
  },
  statTitle: {
    fontSize: 14,
    color: '#6b7280',
  },
  recentSection: {
    padding: 20,
    paddingBottom: 40,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  activityIcon: {
    fontSize: 32,
    marginRight: 12,
  },
  activityContent: {
    flex: 1,
  },
  activityTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1f2937',
    marginBottom: 4,
  },
  activityTime: {
    fontSize: 14,
    color: '#6b7280',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#fff',
  },
  closeModalButton: {
    padding: 16,
    backgroundColor: '#f3f4f6',
    alignItems: 'center',
  },
  closeModalButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#6b7280',
  },
});

export default HomeScreen;
