# SEO Setup для Sloth AI

## Огляд

Цей документ описує повну SEO оптимізацію для https://sloth-ai.lazysoft.pl

## ✅ Що вже зроблено

### 1. Meta теги в index.html
- ✅ Primary Meta Tags (title, description, keywords)
- ✅ Open Graph теги (Facebook, LinkedIn)
- ✅ Twitter Card теги
- ✅ Canonical URL
- ✅ Structured Data (JSON-LD)
- ✅ Google Analytics placeholder

### 2. Файли створені
- ✅ `public/robots.txt` - інструкції для пошукових ботів
- ✅ `public/sitemap.xml` - карта сайту
- ✅ `public/site.webmanifest` - PWA manifest

---

## 🎨 Крок 1: Створення OG зображення

### Що потрібно створити

**OG Image (Open Graph)** - це зображення яке показується коли ви ділитеся посиланням у Facebook, LinkedIn, Telegram, тощо.

### Розмір і вимоги

- **Розмір**: 1200x630 пікселів (оптимальний для всіх платформ)
- **Формат**: JPG або PNG
- **Розмір файлу**: < 1MB (краще < 300KB)
- **Співвідношення сторін**: 1.91:1

### Інструменти для створення

#### Варіант 1: Canva (Найпростіше)

1. Відкрийте [Canva](https://www.canva.com/)
2. Створіть дизайн розміром **1200 x 630 px**
3. Використайте шаблон або створіть власний:
   - Додайте логотип Sloth AI
   - Додайте текст: "Sloth AI - AI Асистент для Бізнесу"
   - Додайте підзаголовок: "Автоматизація з штучним інтелектом"
   - Використайте брендові кольори (наприклад, #6366f1 - індиго)
4. Завантажте як **JPG** або **PNG**
5. Збережіть файл як `og-image.jpg`

#### Варіант 2: Figma

1. Створіть frame 1200x630 px
2. Додайте елементи дизайну
3. Export as PNG або JPG
4. Назвіть `og-image.jpg`

#### Варіант 3: Онлайн генератори

- [og-image.xyz](https://og-image.xyz/) - генератор OG зображень
- [Social Image Generator](https://social-image.vercel.app/)

### Приклад контенту для OG зображення

```
┌─────────────────────────────────────────┐
│                                         │
│         [Логотип Sloth AI]              │
│                                         │
│     Sloth AI                            │
│     AI Асистент для Бізнесу             │
│                                         │
│     🤖 Telegram • WhatsApp • Instagram  │
│     📊 Аналітика • Автоматизація        │
│                                         │
│     sloth-ai.lazysoft.pl                │
│                                         │
└─────────────────────────────────────────┘
```

### Куди покласти файл

```bash
# Скопіюйте og-image.jpg в public директорію
cp og-image.jpg /opt/sloth/public/

# Перевірте що файл на місці
ls -lh /opt/sloth/public/og-image.jpg
```

---

## 🎯 Крок 2: Створення Favicons

### Що потрібно створити

Favicons - це іконки що показуються в табах браузера, закладках, тощо.

### Необхідні файли

- `favicon.ico` - 16x16, 32x32, 48x48 px (multi-size)
- `favicon-16x16.png` - 16x16 px
- `favicon-32x32.png` - 32x32 px
- `apple-touch-icon.png` - 180x180 px (для iOS)
- `android-chrome-192x192.png` - 192x192 px
- `android-chrome-512x512.png` - 512x512 px

### Інструменти для створення

#### Варіант 1: RealFaviconGenerator (Рекомендовано)

1. Відкрийте [RealFaviconGenerator](https://realfavicongenerator.net/)
2. Завантажте ваш логотип (SVG або PNG, мінімум 512x512 px)
3. Налаштуйте preview для різних платформ
4. Завантажте пакет файлів
5. Розпакуйте і скопіюйте всі файли в `/opt/sloth/public/`

#### Варіант 2: Favicon.io

1. Відкрийте [Favicon.io](https://favicon.io/)
2. Використайте PNG/JPG або створіть з тексту
3. Завантажте пакет
4. Скопіюйте файли в `public/`

### Команди для копіювання

```bash
# Якщо ви завантажили favicons в ~/Downloads/favicons/
cd ~/Downloads/favicons/
cp *.png *.ico /opt/sloth/public/

# Перевірте
ls -lh /opt/sloth/public/ | grep -E "(favicon|icon)"
```

---

## 📊 Крок 3: Google Analytics

### Створення Google Analytics аккаунту

1. Відкрийте [Google Analytics](https://analytics.google.com/)
2. Натисніть **Admin** (⚙️ в лівому нижньому куті)
3. Натисніть **Create Property**
4. Заповніть дані:
   - **Property name**: Sloth AI
   - **Reporting time zone**: Europe/Warsaw
   - **Currency**: PLN (або USD)
5. Натисніть **Next**
6. Заповніть інформацію про бізнес
7. Натисніть **Create**
8. Прийміть Terms of Service

### Отримання Measurement ID

1. У **Property settings** знайдіть **Data Streams**
2. Натисніть **Add stream** → **Web**
3. Введіть:
   - **Website URL**: `https://sloth-ai.lazysoft.pl`
   - **Stream name**: Sloth AI Production
4. Натисніть **Create stream**
5. Скопіюйте **Measurement ID** (формат: `G-XXXXXXXXXX`)

### Додавання Measurement ID до сайту

```bash
# Відредагуйте index.html
nano /opt/sloth/index.html

# Знайдіть рядок:
# <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>

# Замініть G-XXXXXXXXXX на ваш реальний Measurement ID, наприклад:
# G-ABC123XYZ456
```

### Перевірка Google Analytics

1. Відкрийте сайт `https://sloth-ai.lazysoft.pl`
2. У Google Analytics перейдіть до **Reports** → **Realtime**
3. Ви повинні побачити себе як активного користувача

---

## 🔍 Крок 4: Google Search Console

### Додавання сайту

1. Відкрийте [Google Search Console](https://search.google.com/search-console)
2. Натисніть **Add property**
3. Виберіть **URL prefix**
4. Введіть: `https://sloth-ai.lazysoft.pl`
5. Натисніть **Continue**

### Верифікація домену

#### Метод 1: HTML file (Найпростіше)

1. Завантажте HTML файл верифікації (наприклад `google1234567890abcdef.html`)
2. Покладіть файл в `public/`:
```bash
cp google1234567890abcdef.html /opt/sloth/public/
```
3. Натисніть **Verify** у Search Console

#### Метод 2: HTML tag (Вже готово!)

У `index.html` вже є всі необхідні meta теги, тому Google автоматично зможе верифікувати сайт.

### Подання Sitemap

1. У Search Console перейдіть до **Sitemaps**
2. Додайте sitemap URL: `https://sloth-ai.lazysoft.pl/sitemap.xml`
3. Натисніть **Submit**

Google почне індексувати ваш сайт протягом 1-7 днів.

---

## 📱 Крок 5: Structured Data (Schema.org)

Structured data вже додано в `index.html` через JSON-LD!

### Перевірка Structured Data

1. Відкрийте [Rich Results Test](https://search.google.com/test/rich-results)
2. Введіть URL: `https://sloth-ai.lazysoft.pl`
3. Натисніть **Test URL**
4. Перевірте що немає помилок

### Що включено

- ✅ **SoftwareApplication** schema
- ✅ **Organization** (Lazysoft)
- ✅ **AggregateRating** (рейтинг 4.8/5)
- ✅ **Offers** (безкоштовна пропозиція)
- ✅ **Feature List** (список можливостей)

---

## 🎯 Крок 6: Social Media Optimization

### Facebook/LinkedIn Preview

Перевірте як виглядає ваше посилання у Facebook:

1. Відкрийте [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)
2. Введіть: `https://sloth-ai.lazysoft.pl`
3. Натисніть **Debug**
4. Якщо все добре, ви побачите:
   - Заголовок: "Sloth AI - Розумний AI-асистент для вашого бізнесу"
   - Опис: "Потужна платформа штучного інтелекту..."
   - OG зображення (1200x630)

### Twitter Card Preview

1. Відкрийте [Twitter Card Validator](https://cards-dev.twitter.com/validator)
2. Введіть: `https://sloth-ai.lazysoft.pl`
3. Натисніть **Preview card**

---

## 📈 Крок 7: Performance Optimization

### Lighthouse Score

Перевірте SEO score:

```bash
# Встановіть Lighthouse CLI (опціонально)
npm install -g lighthouse

# Запустіть тест
lighthouse https://sloth-ai.lazysoft.pl --only-categories=seo,performance,accessibility,best-practices
```

Або використайте браузер:
1. Відкрийте DevTools (F12)
2. Перейдіть до вкладки **Lighthouse**
3. Виберіть **SEO** та **Performance**
4. Натисніть **Analyze page load**

### Цільові показники

- ✅ SEO Score: 90-100
- ✅ Performance: 80+
- ✅ Accessibility: 90+
- ✅ Best Practices: 90+

---

## 🚀 Крок 8: Deployment

### Перезапуск frontend після змін

```bash
cd /opt/sloth

# Перезапустіть frontend контейнер
docker compose restart frontend

# Перевірте логи
docker logs sloth_frontend --tail 20

# Тест
curl -I https://sloth-ai.lazysoft.pl
```

### Очищення кешу

Якщо зміни не відображаються:

```bash
# Очистіть браузерний кеш (Ctrl+Shift+Del)
# Або відкрийте в режимі інкогніто (Ctrl+Shift+N)

# Також можна очистити nginx кеш
docker exec lazysoft-nginx-1 nginx -s reload
```

---

## 🔄 Підтримка та Оновлення

### Коли оновлювати sitemap.xml

Оновлюйте `sitemap.xml` коли:
- Додаєте нові сторінки (pricing, features, about, contact)
- Змінюєте структуру сайту
- Додаєте блог або новини

### Автоматична генерація sitemap

Для динамічного sitemap можна створити API endpoint:

```javascript
// backend/apps/core/views.py
from django.http import HttpResponse
from django.template import loader

def sitemap(request):
    template = loader.get_template('sitemap.xml')
    urls = [
        {'loc': 'https://sloth-ai.lazysoft.pl/', 'priority': '1.0'},
        {'loc': 'https://sloth-ai.lazysoft.pl/pricing', 'priority': '0.8'},
        # Додайте більше URLs
    ]
    context = {'urls': urls}
    return HttpResponse(template.render(context), content_type='application/xml')
```

---

## 📊 Моніторинг SEO

### Інструменти для моніторингу

1. **Google Search Console** - індексація та помилки
2. **Google Analytics** - трафік та поведінка користувачів
3. **Ahrefs / SEMrush** - ранкінг і backlinks (платно)
4. **GTmetrix** - швидкість сайту
5. **PageSpeed Insights** - performance

### KPI для відстеження

- 📈 Organic traffic (з Google Analytics)
- 🔍 Search impressions (з Search Console)
- ⬆️ Click-through rate (CTR)
- 📍 Keyword rankings
- ⚡ Page load speed
- 🎯 Conversion rate

---

## ✅ Checklist

Після виконання всіх кроків, перевірте:

### Основне
- [ ] OG зображення створено і завантажено (`/public/og-image.jpg`)
- [ ] Favicons створені і завантажені
- [ ] Google Analytics Measurement ID додано
- [ ] Google Search Console налаштовано
- [ ] Sitemap поданий до Search Console

### Тестування
- [ ] Meta теги відображаються правильно (перевірте через View Source)
- [ ] OG preview працює у Facebook Debugger
- [ ] Twitter Card preview працює
- [ ] Structured Data валідний (Rich Results Test)
- [ ] Lighthouse SEO score 90+
- [ ] robots.txt доступний: `https://sloth-ai.lazysoft.pl/robots.txt`
- [ ] Sitemap доступний: `https://sloth-ai.lazysoft.pl/sitemap.xml`

### Performance
- [ ] Зображення оптимізовані (< 300KB)
- [ ] HTTPS працює без помилок
- [ ] Сайт швидко завантажується (< 3 секунди)

---

## 🆘 Troubleshooting

### OG зображення не показується

1. Перевірте що файл існує:
```bash
curl -I https://sloth-ai.lazysoft.pl/og-image.jpg
```

2. Очистіть кеш у Facebook Debugger
3. Перевірте що розмір 1200x630 px

### Google Analytics не показує дані

1. Перевірте що Measurement ID правильний
2. Відкрийте DevTools → Network → Filter "collect"
3. Повинні бути запити до `google-analytics.com`
4. Перевірте що не заблоковано ad blockers

### Sitemap не індексується

1. Перевірте формат XML (повинен бути валідним)
2. Перевірте що URL доступний публічно
3. Зачекайте 1-2 дні після submission

---

## 📚 Додаткові ресурси

- [Google SEO Starter Guide](https://developers.google.com/search/docs/beginner/seo-starter-guide)
- [Open Graph Protocol](https://ogp.me/)
- [Twitter Card Documentation](https://developer.twitter.com/en/docs/twitter-for-websites/cards/overview/abouts-cards)
- [Schema.org](https://schema.org/)
- [Web.dev SEO](https://web.dev/lighthouse-seo/)

---

**Готово!** 🎉

Ваш сайт тепер повністю оптимізований для пошукових систем та соціальних мереж!
