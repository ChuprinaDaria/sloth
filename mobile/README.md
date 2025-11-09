# Sloth AI Mobile App - React Native + Expo

## Огляд

Повноцінний мобільний додаток для iOS і Android, який повністю синхронізується з Django backend через REST API.

### Технології

- **React Native** - Framework для мобільних додатків
- **Expo** - Toolchain для швидкої розробки
- **React Navigation** - Навігація між екранами
- **Axios** - HTTP клієнт для API
- **React Query** - Кешування та синхронізація даних
- **Zustand** - State management
- **Expo Secure Store** - Безпечне зберігання токенів

---

## Структура проєкту

```
mobile/
├── App.js                          # Головний файл додатку
├── app.json                        # Expo конфігурація
├── package.json                    # Залежності
├── babel.config.js                 # Babel конфігурація
├── assets/                         # Статичні файли (іконки, зображення)
├── src/
│   ├── navigation/                 # Навігація
│   │   ├── AppNavigator.js        # Головна навігація (залогінений)
│   │   └── AuthNavigator.js       # Навігація для авторизації
│   ├── screens/                    # Екрани додатку
│   │   ├── auth/                  # Екрани авторизації
│   │   │   ├── WelcomeScreen.js  # Вітальний екран
│   │   │   ├── LoginScreen.js    # Вхід
│   │   │   └── RegisterScreen.js # Реєстрація
│   │   └── app/                   # Основні екрани
│   │       ├── HomeScreen.js     # Головна
│   │       ├── ConversationsScreen.js  # Чати
│   │       ├── IntegrationsScreen.js   # Інтеграції
│   │       └── ProfileScreen.js   # Профіль
│   ├── services/                   # API сервіси
│   │   └── api.js                 # API клієнт + методи
│   ├── stores/                     # State management (Zustand)
│   │   └── authStore.js           # Авторизація store
│   ├── components/                 # Переосичувані компоненти
│   ├── hooks/                      # Custom React hooks
│   ├── utils/                      # Утиліти
│   └── constants/                  # Константи
└── docs/                           # Документація
```

---

## Встановлення

### Передумови

- Node.js 18+ і npm/yarn
- Expo CLI: `npm install -g expo-cli`
- Expo Go app на телефоні (для тестування)
  - iOS: [App Store](https://apps.apple.com/app/expo-go/id982107779)
  - Android: [Google Play](https://play.google.com/store/apps/details?id=host.exp.exponent)

### Кроки встановлення

```bash
# 1. Перейти в директорію mobile
cd mobile

# 2. Встановити залежності
npm install
# або
yarn install

# 3. Запустити Expo dev server
npm start
# або
expo start
```

### Запуск на емуляторі/пристрої

```bash
# iOS Simulator (потрібен macOS і Xcode)
npm run ios

# Android Emulator (потрібен Android Studio)
npm run android

# Веб (для швидкого тестування)
npm run web

# Або скануйте QR код в Expo Go на телефоні
```

---

## Налаштування API

### 1. Backend URL

Відредагуйте `app.json`:

```json
{
  "expo": {
    "extra": {
      "apiUrl": "https://sloth-ai.lazysoft.pl/api"
    }
  }
}
```

### 2. API методи

Всі API методи знаходяться в `src/services/api.js`:

- `authAPI` - Авторизація (login, register, logout)
- `agentAPI` - Чати та розмови
- `integrationsAPI` - Інтеграції (Telegram, WhatsApp, тощо)
- `documentsAPI` - Документи
- `subscriptionsAPI` - Підписки

### 3. Авторизація

JWT токени зберігаються в **Expo Secure Store** (зашифровано):
- `auth_token` - Access token
- `refresh_token` - Refresh token

Автоматичне оновлення токенів відбувається через Axios interceptors.

---

## Синхронізація з Backend

### Автоматична синхронізація

Додаток використовує **React Query** для кешування і автоматичної синхронізації:

```javascript
// Приклад: Отримання розмов
import { useQuery } from '@tanstack/react-query';
import { agentAPI } from '../services/api';

function ConversationsScreen() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['conversations'],
    queryFn: () => agentAPI.getConversations(),
    staleTime: 30000, // 30 секунд
    refetchInterval: 60000, // Автоматичне оновлення кожну хвилину
  });

  // ...
}
```

### Offline підтримка

React Query автоматично:
- ✅ Кешує дані локально
- ✅ Показує кешовані дані коли offline
- ✅ Синхронізує при поверненні online
- ✅ Retry запитів при помилці

---

## Додавання нових екранів

### 1. Створіть файл екрану

```javascript
// src/screens/app/NewScreen.js
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

const NewScreen = () => {
  return (
    <View style={styles.container}>
      <Text>New Screen</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default NewScreen;
```

### 2. Додайте в навігацію

```javascript
// src/navigation/AppNavigator.js
import NewScreen from '../screens/app/NewScreen';

// В Tab.Navigator:
<Tab.Screen
  name="New"
  component={NewScreen}
  options={{ title: 'Новий екран' }}
/>
```

---

## Робота з Backend API

### Приклад: Створення нової розмови

```javascript
import { agentAPI } from '../services/api';
import { useMutation, useQueryClient } from '@tanstack/react-query';

function ChatScreen() {
  const queryClient = useQueryClient();

  const createConversation = useMutation({
    mutationFn: agentAPI.createConversation,
    onSuccess: (newConversation) => {
      // Інвалідуємо кеш розмов для оновлення списку
      queryClient.invalidateQueries(['conversations']);

      // Переходимо до нової розмови
      navigation.navigate('Chat', { id: newConversation.id });
    },
  });

  const handleNewChat = () => {
    createConversation.mutate();
  };

  return (
    <TouchableOpacity onPress={handleNewChat}>
      <Text>Новий чат</Text>
    </TouchableOpacity>
  );
}
```

---

## State Management (Zustand)

### Auth Store

```javascript
import { useAuthStore } from '../stores/authStore';

function ProfileScreen() {
  // Отримати дані
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  // Отримати методи
  const logout = useAuthStore((state) => state.logout);

  return (
    <View>
      <Text>Привіт, {user?.first_name}!</Text>
      <Button title="Вийти" onPress={logout} />
    </View>
  );
}
```

### Створення нового Store

```javascript
// src/stores/conversationsStore.js
import { create } from 'zustand';

export const useConversationsStore = create((set) => ({
  conversations: [],
  activeConversation: null,

  setConversations: (conversations) => set({ conversations }),
  setActiveConversation: (id) => set({ activeConversation: id }),

  addMessage: (conversationId, message) =>
    set((state) => ({
      conversations: state.conversations.map((conv) =>
        conv.id === conversationId
          ? { ...conv, messages: [...conv.messages, message] }
          : conv
      ),
    })),
}));
```

---

## Стилізація

Використовуємо **StyleSheet** API з React Native:

```javascript
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  button: {
    backgroundColor: '#6366f1',
    borderRadius: 12,
    padding: 16,
  },
});
```

### Кольорова схема

Використовується та сама палітра що і на веб-сайті:

```javascript
const COLORS = {
  primary: '#6366f1',    // Індиго
  secondary: '#8b5cf6',   // Фіолетовий
  success: '#10b981',     // Зелений
  danger: '#ef4444',      // Червоний
  warning: '#f59e0b',     // Помаранчевий
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    // ...
  },
};
```

---

## Іконки

Використовуємо **@expo/vector-icons** (включає Ionicons, Material Icons, FontAwesome):

```javascript
import { Ionicons } from '@expo/vector-icons';

<Ionicons name="home-outline" size={24} color="#6366f1" />
```

[Список всіх іконок](https://icons.expo.fyi/)

---

## Push Notifications

### 1. Налаштування

```bash
expo install expo-notifications
```

### 2. Запит дозволу

```javascript
import * as Notifications from 'expo-notifications';

async function registerForPushNotificationsAsync() {
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') {
    alert('Push notifications permission not granted');
    return;
  }

  const token = (await Notifications.getExpoPushTokenAsync()).data;
  console.log('Push token:', token);

  // Відправити token на backend
  await api.post('/users/push-token/', { token });
}
```

### 3. Обробка notifications

```javascript
Notifications.addNotificationReceivedListener((notification) => {
  console.log('Notification received:', notification);
});

Notifications.addNotificationResponseReceivedListener((response) => {
  console.log('Notification tapped:', response);
  // Перейти на потрібний екран
});
```

---

## Завантаження файлів

### Камера та галерея

```javascript
import * as ImagePicker from 'expo-image-picker';

async function pickImage() {
  const result = await ImagePicker.launchImageLibraryAsync({
    mediaTypes: ImagePicker.MediaTypeOptions.Images,
    allowsEditing: true,
    aspect: [4, 3],
    quality: 1,
  });

  if (!result.canceled) {
    const file = {
      uri: result.assets[0].uri,
      type: 'image/jpeg',
      name: 'photo.jpg',
    };

    await documentsAPI.uploadDocument(file, { title: 'My photo' });
  }
}
```

---

## Тестування

### Unit тести (Jest)

```bash
npm test
```

### E2E тести (Detox)

```bash
# Встановлення
npm install --save-dev detox

# Запуск
detox test
```

---

## Build для Production

### iOS (потрібен macOS і Xcode)

```bash
# 1. Збірка через Expo
eas build --platform ios

# Або Native Build:
expo prebuild
cd ios
pod install
open ios/SlothAI.xcworkspace  # Відкрити в Xcode
# Build в Xcode
```

### Android

```bash
# 1. Збірка через Expo
eas build --platform android

# Або Native Build:
expo prebuild
cd android
./gradlew assembleRelease
# APK: android/app/build/outputs/apk/release/app-release.apk
```

### Expo Application Services (EAS)

Найпростіший спосіб:

```bash
# 1. Встановити EAS CLI
npm install -g eas-cli

# 2. Login
eas login

# 3. Build для обох платформ
eas build --platform all

# 4. Submit до App Store / Google Play
eas submit --platform ios
eas submit --platform android
```

---

## Deployment

### TestFlight (iOS Beta)

1. Build через EAS
2. Submit до App Store Connect
3. Додати тестувальників
4. Розпочати тестування

### Google Play Internal Testing (Android Beta)

1. Build через EAS
2. Upload APK/AAB до Google Play Console
3. Додати тестувальників
4. Розпочати тестування

---

## Моніторинг та Аналітика

### Expo Analytics

Вбудовано в Expo, не потребує налаштування.

### Sentry (Error tracking)

```bash
expo install sentry-expo
```

```javascript
// App.js
import * as Sentry from 'sentry-expo';

Sentry.init({
  dsn: 'your-sentry-dsn',
  enableInExpoDevelopment: true,
  debug: __DEV__,
});
```

---

## Troubleshooting

### Metro bundler не запускається

```bash
# Очистити кеш
expo start --clear

# Або
rm -rf node_modules
npm install
expo start
```

### API не працює

1. Перевірте що backend запущений
2. Перевірте URL в `app.json`
3. Перевірте CORS налаштування на backend
4. Перевірте токен в Secure Store:

```javascript
import * as SecureStore from 'expo-secure-store';

const token = await SecureStore.getItemAsync('auth_token');
console.log('Token:', token);
```

### Проблеми з iOS

- Перевірте Xcode version (13+)
- Запустіть `pod install` в `ios/`
- Очистіть build: `rm -rf ios/build`

### Проблеми з Android

- Перевірте Android SDK (API 31+)
- Очистіть build: `cd android && ./gradlew clean`
- Перевірте Java version (11 або 17)

---

## Наступні кроки

### Додати функціональність

- [ ] Real-time чат (WebSockets)
- [ ] Push notifications
- [ ] Офлайн підтримка (SQLite)
- [ ] Біометрична авторизація (Face ID / Fingerprint)
- [ ] Темна тема
- [ ] Локалізація (i18n)
- [ ] Детальний екран розмови
- [ ] Редагування профілю
- [ ] Завантаження документів
- [ ] Аналітика та статистика
- [ ] Налаштування підписки

### Покращити UI/UX

- [ ] Анімації (Reanimated)
- [ ] Skeleton loaders
- [ ] Pull-to-refresh
- [ ] Infinite scroll
- [ ] Toast notifications
- [ ] Bottom sheets
- [ ] Splash screen animation

---

## Документація

- [Expo Documentation](https://docs.expo.dev/)
- [React Native Documentation](https://reactnative.dev/docs/getting-started)
- [React Navigation](https://reactnavigation.org/docs/getting-started)
- [React Query](https://tanstack.com/query/latest/docs/react/overview)
- [Zustand](https://github.com/pmndrs/zustand)

---

## Ліцензія

Цей проєкт є власністю Lazysoft. Всі права захищені.

---

**Готово!** 🎉 Повноцінний мобільний додаток готовий до розробки та розширення!
