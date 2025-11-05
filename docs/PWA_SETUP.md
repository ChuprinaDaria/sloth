# PWA (Progressive Web App) Setup для Sloth AI

## Огляд

Sloth AI тепер підтримує PWA! Користувачі можуть встановити веб-додаток на свої мобільні пристрої та користуватися ним як нативним додатком.

## ✅ Що вже налаштовано

### 1. Service Worker (`public/sw.js`)
- ✅ Кешування статичних ресурсів
- ✅ Offline підтримка
- ✅ Автоматичне оновлення
- ✅ Background sync готовий
- ✅ Push notifications готовий

### 2. Web App Manifest (`public/site.webmanifest`)
- ✅ Назва додатку: "Sloth AI - AI Асистент для Бізнесу"
- ✅ Іконки (треба додати PNG файли)
- ✅ Theme color: #6366f1 (індиго)
- ✅ Display mode: standalone
- ✅ Screenshots готові

### 3. Install Prompt Component (`src/components/InstallPWA.jsx`)
- ✅ Автоматичний промпт для встановлення
- ✅ Підтримка iOS та Android
- ✅ Інструкції для iOS (Share → Add to Home Screen)
- ✅ Нативний промпт для Android/Chrome
- ✅ Запам'ятовування відмови на 7 днів

### 4. Meta теги в `index.html`
- ✅ `apple-mobile-web-app-capable`
- ✅ `apple-mobile-web-app-status-bar-style`
- ✅ `apple-mobile-web-app-title`
- ✅ `theme-color`
- ✅ Apple touch icons

---

## 🎨 Створення іконок для PWA

### Необхідні розміри

Для повної підтримки PWA потрібні іконки у форматі PNG:

| Розмір | Призначення | Назва файлу |
|--------|-------------|-------------|
| 192x192 | Android (стандартний) | `android-chrome-192x192.png` |
| 512x512 | Android (великий) | `android-chrome-512x512.png` |
| 180x180 | iOS (Apple Touch Icon) | `apple-touch-icon.png` |
| 32x32 | Desktop favicon | `favicon-32x32.png` |
| 16x16 | Desktop favicon | `favicon-16x16.png` |
| 144x144 | Windows tiles (опційно) | `ms-icon-144x144.png` |

### Інструменти для створення

#### Варіант 1: PWA Icon Generator (Рекомендовано)

1. Відкрийте [PWA Icon Generator](https://www.pwabuilder.com/imageGenerator)
2. Завантажте ваш логотип (SVG або PNG, мінімум 512x512 px)
3. Виберіть padding (рекомендовано 10-20%)
4. Завантажте ZIP з усіма іконками
5. Розпакуйте і скопіюйте в `/opt/sloth/public/`

#### Варіант 2: RealFaviconGenerator

1. Відкрийте [RealFaviconGenerator](https://realfavicongenerator.net/)
2. Завантажте логотип
3. Налаштуйте iOS, Android, Windows tiles
4. Завантажте пакет
5. Скопіюйте файли в `public/`

### Команди для встановлення іконок

```bash
# Припустимо ви завантажили іконки в ~/Downloads/pwa-icons/
cd ~/Downloads/pwa-icons/

# Скопіюйте всі PNG файли
cp *.png /opt/sloth/public/

# Перевірте
ls -lh /opt/sloth/public/*.png

# Очікується:
# android-chrome-192x192.png
# android-chrome-512x512.png
# apple-touch-icon.png
# favicon-16x16.png
# favicon-32x32.png
```

---

## 📱 Використання Install Prompt компоненту

### Додавання в App.jsx

```javascript
// src/App.jsx
import InstallPWA from './components/InstallPWA';

function App() {
  return (
    <div className="App">
      {/* Ваш існуючий код */}

      {/* Додайте в кінець */}
      <InstallPWA />
    </div>
  );
}

export default App;
```

### Налаштування промпту

Компонент `InstallPWA` автоматично:
- ✅ Показується через 5 секунд на iOS (якщо не встановлено)
- ✅ Показується одразу на Android коли браузер готовий
- ✅ Ховається якщо PWA вже встановлено
- ✅ Запам'ятовує відмову на 7 днів

Для кастомізації відредагуйте:
- Час показу: змініть `setTimeout` в `useEffect` (рядок 33)
- Період повтору: змініть `daysSinceDismissed < 7` (рядок 69)
- Стилі: відредагуйте Tailwind класи

---

## 🧪 Тестування PWA

### 1. Перевірка Service Worker

```bash
# Відкрийте сайт у браузері
https://sloth-ai.lazysoft.pl

# Відкрийте DevTools (F12)
# Перейдіть до Application → Service Workers
# Ви повинні побачити:
# - Status: activated and running
# - Source: /sw.js
```

### 2. Перевірка Manifest

```bash
# У DevTools → Application → Manifest
# Перевірте що всі поля заповнені:
# - Name: Sloth AI - AI Асистент для Бізнесу
# - Short name: Sloth AI
# - Start URL: /
# - Display: standalone
# - Theme color: #6366f1
# - Icons: (після додавання PNG файлів)
```

### 3. Lighthouse PWA Audit

```bash
# У DevTools → Lighthouse
# Виберіть "Progressive Web App"
# Натисніть "Analyze page load"

# Цільові показники:
# - PWA Score: 90-100
# - ✅ Installable
# - ✅ Offline support
# - ✅ Fast load times
```

### 4. Тестування на мобільних

#### Android/Chrome:
1. Відкрийте `https://sloth-ai.lazysoft.pl` в Chrome
2. Повинен з'явитися промпт "Додати Sloth AI на головний екран"
3. Або Menu (⋮) → "Додати на головний екран"
4. Після встановлення іконка з'явиться на головному екрані

#### iOS/Safari:
1. Відкрийте `https://sloth-ai.lazysoft.pl` в Safari
2. Натисніть Share кнопку (квадрат з стрілкою)
3. Scroll down → "На екран «Домівка»"
4. Або слідуйте інструкціям в InstallPWA промпті

---

## ⚙️ Налаштування Service Worker

### Що кешується

По замовчуванню Service Worker кешує:
- `/` - головна сторінка
- `/index.html`
- `/logo/logo.svg` - логотип
- `/og-image.jpg` - OG зображення
- `/manifest.json` - manifest файл

### Додавання файлів до кешу

Відредагуйте `public/sw.js`:

```javascript
const urlsToCache = [
  '/',
  '/index.html',
  '/logo/logo.svg',
  '/og-image.jpg',
  '/manifest.json',
  // Додайте ваші файли
  '/assets/main.css',
  '/assets/main.js',
];
```

### Оновлення Service Worker

При зміні Service Worker:

1. Збільште версію:
```javascript
const CACHE_NAME = 'sloth-ai-v2'; // було v1
```

2. Користувачі автоматично отримають оновлення через 1 годину
3. Або примусово: `registration.update()` в DevTools

---

## 🔔 Push Notifications (Майбутнє)

Service Worker вже готовий для push notifications!

### Кроки для активації:

1. **Backend**: Додати Web Push API
```python
# backend/apps/notifications/webpush.py
from pywebpush import webpush

def send_web_push(subscription_info, message_body):
    return webpush(
        subscription_info=subscription_info,
        data=message_body,
        vapid_private_key="YOUR_VAPID_PRIVATE_KEY",
        vapid_claims={
            "sub": "mailto:your-email@example.com"
        }
    )
```

2. **Frontend**: Запитати дозвіл
```javascript
// Ask for notification permission
Notification.requestPermission().then((permission) => {
  if (permission === 'granted') {
    // Subscribe to push notifications
    navigator.serviceWorker.ready.then((registration) => {
      registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: 'YOUR_PUBLIC_VAPID_KEY'
      });
    });
  }
});
```

---

## 🔄 Background Sync (Майбутнє)

Service Worker підтримує Background Sync для sync даних коли користувач офлайн.

### Приклад використання:

```javascript
// Register sync when offline
if ('sync' in registration) {
  registration.sync.register('sync-data')
    .then(() => console.log('Sync registered'))
    .catch((err) => console.log('Sync registration failed', err));
}

// Service Worker обробить sync коли з'явиться інтернет
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-data') {
    event.waitUntil(syncData());
  }
});
```

---

## 📊 Аналітика PWA

### Відстеження встановлень

Додайте в Google Analytics:

```javascript
// Track PWA installs
window.addEventListener('beforeinstallprompt', (e) => {
  // Track install prompt shown
  gtag('event', 'pwa_install_prompt_shown');
});

window.addEventListener('appinstalled', (e) => {
  // Track successful install
  gtag('event', 'pwa_installed');
});
```

### Відстеження standalone mode

```javascript
// Track if app is running as PWA
if (window.matchMedia('(display-mode: standalone)').matches) {
  gtag('event', 'pwa_running_standalone');
} else {
  gtag('event', 'pwa_running_browser');
}
```

---

## ✅ Checklist

### Основне
- [ ] Іконки створені і завантажені (192x192, 512x512, 180x180, etc.)
- [ ] InstallPWA компонент додано в App.jsx
- [ ] Service Worker працює (перевірте в DevTools)
- [ ] Manifest валідний (перевірте в DevTools)
- [ ] Lighthouse PWA score 90+

### iOS
- [ ] Apple touch icons на місці
- [ ] `apple-mobile-web-app-capable` встановлено
- [ ] Тестування в Safari на iPhone/iPad
- [ ] Install інструкції показуються

### Android
- [ ] Android Chrome icons на місці
- [ ] Install промпт показується
- [ ] Тестування в Chrome на Android
- [ ] Після встановлення працює як standalone app

### Offline
- [ ] Сайт працює без інтернету (базовий HTML)
- [ ] Service Worker кешує критичні файли
- [ ] Offline сторінка готова

---

## 🆘 Troubleshooting

### Service Worker не реєструється

**Симптоми**: Немає в DevTools → Application → Service Workers

**Рішення**:
1. Перевірте що `sw.js` доступний: `curl https://sloth-ai.lazysoft.pl/sw.js`
2. Перевірте Console на помилки
3. Service Workers працюють тільки через HTTPS (або localhost)
4. Очистіть кеш браузера (Ctrl+Shift+Del)

### Install промпт не показується

**Симптоми**: Немає кнопки "Додати на головний екран"

**Рішення**:
1. Перевірте що manifest валідний
2. Перевірте що іконки існують (192x192, 512x512)
3. На iOS: використовуйте Safari (не Chrome!)
4. На Android: використовуйте Chrome
5. Перевірте що PWA ще не встановлено

### Іконки не відображаються

**Симптоми**: Білий квадрат замість іконки

**Рішення**:
1. Перевірте що PNG файли існують
2. Перевірте розміри (точно 192x192, 512x512, тощо)
3. Перевірте шляхи в `site.webmanifest`
4. Деінсталюйте і встановіть PWA знову

---

## 📚 Додаткові ресурси

- [PWA Documentation (MDN)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web App Manifest](https://developer.mozilla.org/en-US/docs/Web/Manifest)
- [PWA Builder](https://www.pwabuilder.com/)
- [Workbox (Google PWA tools)](https://developers.google.com/web/tools/workbox)

---

**Готово!** 🎉 Ваш сайт тепер можна встановити як нативний додаток на мобільних!
