import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { integrationsAPI } from '../../services/api';

const EmailSetup = ({ onClose, onSuccess }) => {
  const [provider, setProvider] = useState('smtp');
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    smtp_server: '',
    smtp_port: '587',
    smtp_username: '',
    smtp_password: '',
    from_email: '',
    from_name: '',
  });

  const handleConnect = async () => {
    // Validate form
    if (provider === 'smtp') {
      if (!formData.smtp_server || !formData.smtp_username || !formData.smtp_password || !formData.from_email) {
        Alert.alert('Помилка', 'Будь ласка, заповніть всі обов\'язкові поля');
        return;
      }
    }

    try {
      setLoading(true);
      await integrationsAPI.connectEmail(provider, formData);
      Alert.alert('Успіх', 'Email інтеграцію підключено!', [
        {
          text: 'OK',
          onPress: () => {
            if (onSuccess) onSuccess();
            if (onClose) onClose();
          },
        },
      ]);
    } catch (err) {
      console.error('Error connecting email:', err);
      Alert.alert('Помилка', err.response?.data?.error || 'Не вдалося підключити email');
    } finally {
      setLoading(false);
    }
  };

  const updateFormData = (key, value) => {
    setFormData(prev => ({ ...prev, [key]: value }));
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.icon}>📧</Text>
        <Text style={styles.title}>Інтеграція Email</Text>
      </View>

      <Text style={styles.description}>
        Підключіть email для відправки підтверджень бронювань та нагадувань
      </Text>

      {/* Provider Tabs */}
      <View style={styles.providerTabs}>
        <TouchableOpacity
          style={[styles.providerTab, provider === 'gmail' && styles.activeProviderTab]}
          onPress={() => setProvider('gmail')}
        >
          <Text style={[styles.providerTabText, provider === 'gmail' && styles.activeProviderTabText]}>
            Gmail
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.providerTab, provider === 'smtp' && styles.activeProviderTab]}
          onPress={() => setProvider('smtp')}
        >
          <Text style={[styles.providerTabText, provider === 'smtp' && styles.activeProviderTabText]}>
            SMTP
          </Text>
        </TouchableOpacity>
      </View>

      {provider === 'gmail' && (
        <View style={styles.gmailInfo}>
          <Text style={styles.infoIcon}>ℹ️</Text>
          <View style={styles.infoContent}>
            <Text style={styles.infoTitle}>Gmail OAuth</Text>
            <Text style={styles.infoText}>
              Для підключення Gmail, будь ласка, використайте веб-версію додатку.
              OAuth авторизація вимагає відкриття браузера.
            </Text>
          </View>
        </View>
      )}

      {provider === 'smtp' && (
        <View style={styles.form}>
          <View style={styles.formGroup}>
            <Text style={styles.label}>SMTP Сервер *</Text>
            <TextInput
              style={styles.input}
              placeholder="smtp.gmail.com"
              value={formData.smtp_server}
              onChangeText={(value) => updateFormData('smtp_server', value)}
              autoCapitalize="none"
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.label}>SMTP Порт *</Text>
            <TextInput
              style={styles.input}
              placeholder="587"
              value={formData.smtp_port}
              onChangeText={(value) => updateFormData('smtp_port', value)}
              keyboardType="number-pad"
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.label}>Ім'я користувача (Email) *</Text>
            <TextInput
              style={styles.input}
              placeholder="your-email@gmail.com"
              value={formData.smtp_username}
              onChangeText={(value) => updateFormData('smtp_username', value)}
              autoCapitalize="none"
              keyboardType="email-address"
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.label}>Пароль додатку *</Text>
            <TextInput
              style={styles.input}
              placeholder="••••••••"
              value={formData.smtp_password}
              onChangeText={(value) => updateFormData('smtp_password', value)}
              secureTextEntry
              autoCapitalize="none"
            />
            <Text style={styles.hint}>
              Для Gmail використовуйте пароль додатку (App Password)
            </Text>
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.label}>Email відправника *</Text>
            <TextInput
              style={styles.input}
              placeholder="your-email@gmail.com"
              value={formData.from_email}
              onChangeText={(value) => updateFormData('from_email', value)}
              autoCapitalize="none"
              keyboardType="email-address"
            />
          </View>

          <View style={styles.formGroup}>
            <Text style={styles.label}>Ім'я відправника</Text>
            <TextInput
              style={styles.input}
              placeholder="Sloth AI"
              value={formData.from_name}
              onChangeText={(value) => updateFormData('from_name', value)}
            />
          </View>
        </View>
      )}

      {/* Features */}
      <View style={styles.featuresSection}>
        <Text style={styles.featuresTitle}>Можливості:</Text>
        <View style={styles.feature}>
          <Text style={styles.featureIcon}>✓</Text>
          <Text style={styles.featureText}>Автоматичні підтвердження бронювань</Text>
        </View>
        <View style={styles.feature}>
          <Text style={styles.featureIcon}>✓</Text>
          <Text style={styles.featureText}>Нагадування про візити</Text>
        </View>
        <View style={styles.feature}>
          <Text style={styles.featureIcon}>✓</Text>
          <Text style={styles.featureText}>Професійні email розсилки</Text>
        </View>
        <View style={styles.feature}>
          <Text style={styles.featureIcon}>✓</Text>
          <Text style={styles.featureText}>Аналітика відкриттів та кліків</Text>
        </View>
      </View>

      {/* Actions */}
      <View style={styles.actions}>
        {provider === 'smtp' && (
          <TouchableOpacity
            style={styles.connectButton}
            onPress={handleConnect}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.connectButtonText}>Підключити Email</Text>
            )}
          </TouchableOpacity>
        )}

        {onClose && (
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Text style={styles.closeButtonText}>Закрити</Text>
          </TouchableOpacity>
        )}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    alignItems: 'center',
    padding: 20,
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
    marginHorizontal: 20,
    marginBottom: 24,
    lineHeight: 24,
  },
  providerTabs: {
    flexDirection: 'row',
    marginHorizontal: 20,
    marginBottom: 20,
    gap: 12,
  },
  providerTab: {
    flex: 1,
    paddingVertical: 12,
    backgroundColor: '#f3f4f6',
    borderRadius: 12,
    alignItems: 'center',
  },
  activeProviderTab: {
    backgroundColor: '#6366f1',
  },
  providerTabText: {
    fontSize: 16,
    color: '#6b7280',
    fontWeight: '600',
  },
  activeProviderTabText: {
    color: '#fff',
  },
  gmailInfo: {
    flexDirection: 'row',
    backgroundColor: '#dbeafe',
    marginHorizontal: 20,
    padding: 16,
    borderRadius: 12,
    marginBottom: 20,
  },
  infoIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  infoContent: {
    flex: 1,
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e40af',
    marginBottom: 4,
  },
  infoText: {
    fontSize: 14,
    color: '#1e40af',
    lineHeight: 20,
  },
  form: {
    marginHorizontal: 20,
    marginBottom: 20,
  },
  formGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 16,
    color: '#1f2937',
    backgroundColor: '#fff',
  },
  hint: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 4,
  },
  featuresSection: {
    marginHorizontal: 20,
    marginBottom: 20,
  },
  featuresTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 12,
  },
  feature: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  featureIcon: {
    fontSize: 18,
    color: '#10b981',
    marginRight: 12,
  },
  featureText: {
    fontSize: 14,
    color: '#4b5563',
  },
  actions: {
    padding: 20,
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
  closeButton: {
    paddingVertical: 12,
    alignItems: 'center',
  },
  closeButtonText: {
    color: '#6b7280',
    fontSize: 16,
  },
});

export default EmailSetup;
