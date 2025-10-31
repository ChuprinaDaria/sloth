# Salon AI - Frontend

SaaS платформа для салонів краси з AI-агентом для автоматизації спілкування з клієнтами.

## Технології

- **React 18** - UI фреймворк
- **Vite** - Build tool
- **React Router** - Маршрутизація
- **Tailwind CSS** - Стилізація
- **Axios** - HTTP клієнт
- **React Hook Form** - Управління формами
- **Lucide React** - Іконки
- **Stripe** - Платежі

## Структура проєкту

```
src/
├── components/
│   ├── auth/          # Компоненти автентифікації
│   ├── dashboard/     # Компоненти дашборду
│   ├── history/       # Історія чатів
│   ├── integrations/  # Інтеграції (Telegram, WhatsApp, Calendar)
│   ├── layout/        # Layout компоненти (Sidebar, Header)
│   ├── sandbox/       # Тестова пісочниця
│   ├── subscription/  # Підписки та pricing
│   └── training/      # Тренування AI
├── pages/             # Сторінки додатку
├── context/           # React Context (Auth, Subscription)
├── api/               # API клієнти
└── utils/             # Допоміжні функції
```

## Встановлення

1. Клонуйте репозиторій
```bash
git clone <repository-url>
cd sloth
```

2. Встановіть залежності
```bash
npm install
```

3. Створіть `.env` файл на основі `.env.example`
```bash
cp .env.example .env
```

4. Налаштуйте змінні середовища в `.env`:
```env
VITE_API_URL=http://localhost:8000/api
VITE_STRIPE_PUBLIC_KEY=your_stripe_key
```

## Запуск

### Режим розробки
```bash
npm run dev
```

Відкрийте [http://localhost:5173](http://localhost:5173) у браузері.

### Production build
```bash
npm run build
```

### Preview production build
```bash
npm run preview
```

## Основні функції

### 1. Автентифікація
- Реєстрація нових користувачів
- Логін/Логаут
- Захищені роути
- 14-денний trial період

### 2. Тренування AI
- Завантаження файлів (PDF, DOC, TXT, XLS)
- Налаштування prompt для AI
- Моніторинг статусу тренування

### 3. Тестова пісочниця
- Тестування чат-бота
- Тестування розпізнавання фото
- Перегляд відповідей AI в реальному часі

### 4. Інтеграції
- **Telegram Bot** - підключення бота
- **WhatsApp Business** - інтеграція з WhatsApp
- **Google Calendar** - синхронізація календаря

### 5. Історія чатів
- Перегляд всіх розмов
- Детальний перегляд чату
- Фільтрація та пошук

### 6. Налаштування
- Профіль салону
- Мова та часовий пояс
- Інформація про підписку

## API Endpoints

Всі API endpoints налаштовані в `src/api/`:
- `auth.js` - Автентифікація
- `agent.js` - Операції з AI агентом
- `axios.js` - Базова конфігурація axios

## Стилізація

Проєкт використовує Tailwind CSS з кастомною темою:
- **Primary** (Purple): #d946ef
- **Accent** (Orange): #f97316

Кастомні класи доступні в `src/index.css`:
- `.btn-primary` - Основна кнопка
- `.btn-secondary` - Вторинна кнопка
- `.card` - Картка
- `.input` - Поле вводу

## Deployment

1. Build проєкт:
```bash
npm run build
```

2. Deploy папку `dist/` на ваш хостинг (Vercel, Netlify, тощо)

## Розробка

Проєкт налаштований з ESLint для якості коду.

```bash
npm run lint
```

## Ліцензія

MIT

## Підтримка

Для питань звертайтесь до команди розробки.
