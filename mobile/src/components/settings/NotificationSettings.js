import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Switch,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { notificationsAPI } from '../../services/api';

const NotificationSettings = ({ onClose }) => {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await notificationsAPI.getSettings();
      setSettings(data);
    } catch (error) {
      console.error('Error loading settings:', error);
      Alert.alert('Помилка', 'Не вдалося завантажити налаштування');
    } finally {
      setLoading(false);
    }
  };

  const updateSetting = async (key, value) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);

    try {
      setSaving(true);
      await notificationsAPI.updateSettings({ [key]: value });
    } catch (error) {
      console.error('Error updating settings:', error);
      // Revert on error
      setSettings(settings);
      Alert.alert('Помилка', 'Не вдалося зберегти налаштування');
    } finally {
      setSaving(false);
    }
  };

  const sendTestNotification = async () => {
    try {
      setSaving(true);
      await notificationsAPI.sendTest();
      Alert.alert('Успіх', 'Тестове повідомлення відправлено!');
    } catch (error) {
      console.error('Error sending test:', error);
      Alert.alert('Помилка', 'Не вдалося відправити тестове повідомлення');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#6366f1" />
        <Text style={styles.loadingText}>Завантаження...</Text>
      </View>
    );
  }

  if (!settings) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.errorText}>Не вдалося завантажити налаштування</Text>
        <TouchableOpacity style={styles.retryButton} onPress={loadSettings}>
          <Text style={styles.retryButtonText}>Спробувати знову</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerIcon}>🔔</Text>
        <Text style={styles.headerTitle}>Налаштування сповіщень</Text>
        <Text style={styles.headerSubtitle}>
          Керуйте push-повідомленнями для вашого бізнесу
        </Text>
      </View>

      {/* Main Toggle */}
      <View style={styles.section}>
        <View style={styles.settingRow}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingTitle}>Push-повідомлення</Text>
            <Text style={styles.settingDescription}>
              Увімкнути/вимкнути всі повідомлення
            </Text>
          </View>
          <Switch
            value={settings.enabled}
            onValueChange={(value) => updateSetting('enabled', value)}
            trackColor={{ false: '#d1d5db', true: '#6366f1' }}
            thumbColor="#fff"
          />
        </View>
      </View>

      {settings.enabled && (
        <>
          {/* Frequency */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Частота повідомлень</Text>

            <TouchableOpacity
              style={[
                styles.frequencyOption,
                settings.frequency === 'all' && styles.frequencyOptionActive,
              ]}
              onPress={() => updateSetting('frequency', 'all')}
            >
              <View style={styles.radioCircle}>
                {settings.frequency === 'all' && <View style={styles.radioDot} />}
              </View>
              <View style={styles.frequencyInfo}>
                <Text style={styles.frequencyTitle}>Всі повідомлення</Text>
                <Text style={styles.frequencyDescription}>
                  Критичні, важливі та корисні (макс 3/день)
                </Text>
              </View>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.frequencyOption,
                settings.frequency === 'important' && styles.frequencyOptionActive,
              ]}
              onPress={() => updateSetting('frequency', 'important')}
            >
              <View style={styles.radioCircle}>
                {settings.frequency === 'important' && <View style={styles.radioDot} />}
              </View>
              <View style={styles.frequencyInfo}>
                <Text style={styles.frequencyTitle}>Тільки важливі</Text>
                <Text style={styles.frequencyDescription}>
                  Критичні та важливі події
                </Text>
              </View>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.frequencyOption,
                settings.frequency === 'critical' && styles.frequencyOptionActive,
              ]}
              onPress={() => updateSetting('frequency', 'critical')}
            >
              <View style={styles.radioCircle}>
                {settings.frequency === 'critical' && <View style={styles.radioDot} />}
              </View>
              <View style={styles.frequencyInfo}>
                <Text style={styles.frequencyTitle}>Тільки критичні</Text>
                <Text style={styles.frequencyDescription}>
                  VIP клієнти, відгуки, проблеми з інтеграціями
                </Text>
              </View>
            </TouchableOpacity>
          </View>

          {/* Quiet Hours */}
          <View style={styles.section}>
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Text style={styles.settingTitle}>Тиха година</Text>
                <Text style={styles.settingDescription}>
                  {settings.quiet_hours_start} - {settings.quiet_hours_end}
                </Text>
              </View>
              <Switch
                value={settings.quiet_hours_enabled}
                onValueChange={(value) => updateSetting('quiet_hours_enabled', value)}
                trackColor={{ false: '#d1d5db', true: '#6366f1' }}
                thumbColor="#fff"
              />
            </View>
            <Text style={styles.sectionNote}>
              💤 Корисні та важливі повідомлення не надсилатимуться в цей час. Критичні завжди надсилаються.
            </Text>
          </View>

          {/* Critical Notifications */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🔴 Критичні повідомлення</Text>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>💎 VIP клієнти</Text>
              <Switch
                value={settings.vip_messages}
                onValueChange={(value) => updateSetting('vip_messages', value)}
                trackColor={{ false: '#d1d5db', true: '#6366f1' }}
                thumbColor="#fff"
              />
            </View>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>⚠️ Проблеми з інтеграціями</Text>
              <Switch
                value={settings.integration_issues}
                onValueChange={(value) => updateSetting('integration_issues', value)}
                trackColor={{ false: '#d1d5db', true: '#6366f1' }}
                thumbColor="#fff"
              />
            </View>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>⭐ Негативні відгуки</Text>
              <Switch
                value={settings.negative_reviews}
                onValueChange={(value) => updateSetting('negative_reviews', value)}
                trackColor={{ false: '#d1d5db', true: '#6366f1' }}
                thumbColor="#fff"
              />
            </View>
          </View>

          {/* Important Notifications */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🟡 Важливі повідомлення</Text>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>📊 Розумна аналітика</Text>
              <Switch
                value={settings.smart_analytics}
                onValueChange={(value) => updateSetting('smart_analytics', value)}
                trackColor={{ false: '#d1d5db', true: '#6366f1' }}
                thumbColor="#fff"
              />
            </View>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>📅 Нагадування про свята</Text>
              <Switch
                value={settings.holidays_reminders}
                onValueChange={(value) => updateSetting('holidays_reminders', value)}
                trackColor={{ false: '#d1d5db', true: '#6366f1' }}
                thumbColor="#fff"
              />
            </View>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>🎉 Досягнення</Text>
              <Switch
                value={settings.achievements}
                onValueChange={(value) => updateSetting('achievements', value)}
                trackColor={{ false: '#d1d5db', true: '#6366f1' }}
                thumbColor="#fff"
              />
            </View>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>🔔 Клієнти очікують</Text>
              <Switch
                value={settings.pending_conversations}
                onValueChange={(value) => updateSetting('pending_conversations', value)}
                trackColor={{ false: '#d1d5db', true: '#6366f1' }}
                thumbColor="#fff"
              />
            </View>
          </View>

          {/* Useful Notifications */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🟢 Корисні повідомлення</Text>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>📈 Тижневі звіти</Text>
              <Switch
                value={settings.weekly_reports}
                onValueChange={(value) => updateSetting('weekly_reports', value)}
                trackColor={{ false: '#d1d5db', true: '#6366f1' }}
                thumbColor="#fff"
              />
            </View>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>💰 Рекомендації по цінам</Text>
              <Switch
                value={settings.pricing_recommendations}
                onValueChange={(value) => updateSetting('pricing_recommendations', value)}
                trackColor={{ false: '#d1d5db', true: '#6366f1' }}
                thumbColor="#fff"
              />
            </View>

            <View style={styles.settingRow}>
              <Text style={styles.settingLabel}>📸 Ідеї для контенту</Text>
              <Switch
                value={settings.content_recommendations}
                onValueChange={(value) => updateSetting('content_recommendations', value)}
                trackColor={{ false: '#d1d5db', true: '#6366f1' }}
                thumbColor="#fff"
              />
            </View>
          </View>

          {/* Test Notification */}
          <View style={styles.section}>
            <TouchableOpacity
              style={styles.testButton}
              onPress={sendTestNotification}
              disabled={saving}
            >
              {saving ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.testButtonText}>🧪 Відправити тестове повідомлення</Text>
              )}
            </TouchableOpacity>
          </View>
        </>
      )}

      {onClose && (
        <TouchableOpacity style={styles.closeButton} onPress={onClose}>
          <Text style={styles.closeButtonText}>Закрити</Text>
        </TouchableOpacity>
      )}

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          💡 Критичні повідомлення завжди надсилаються незалежно від налаштувань
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6b7280',
  },
  errorText: {
    fontSize: 16,
    color: '#6b7280',
    marginBottom: 16,
    textAlign: 'center',
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
  header: {
    padding: 20,
    backgroundColor: '#fff',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  headerIcon: {
    fontSize: 48,
    marginBottom: 12,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
  },
  section: {
    backgroundColor: '#fff',
    marginTop: 16,
    padding: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 16,
  },
  sectionNote: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 8,
    lineHeight: 18,
  },
  settingRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  settingInfo: {
    flex: 1,
    marginRight: 16,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
  },
  settingDescription: {
    fontSize: 14,
    color: '#6b7280',
  },
  settingLabel: {
    fontSize: 16,
    color: '#1f2937',
    flex: 1,
  },
  frequencyOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#f9fafb',
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  frequencyOptionActive: {
    backgroundColor: '#eef2ff',
    borderColor: '#6366f1',
  },
  radioCircle: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#6b7280',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  radioDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#6366f1',
  },
  frequencyInfo: {
    flex: 1,
  },
  frequencyTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
  },
  frequencyDescription: {
    fontSize: 14,
    color: '#6b7280',
  },
  testButton: {
    backgroundColor: '#6366f1',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  testButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  closeButton: {
    padding: 16,
    alignItems: 'center',
    marginTop: 16,
  },
  closeButtonText: {
    color: '#6b7280',
    fontSize: 16,
  },
  footer: {
    padding: 20,
    paddingBottom: 40,
  },
  footerText: {
    fontSize: 12,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 18,
  },
});

export default NotificationSettings;
