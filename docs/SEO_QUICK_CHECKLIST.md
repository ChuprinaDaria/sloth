# SEO Quick Checklist для Sloth AI

## ✅ Що вже готово (автоматично)

- ✅ Meta теги (title, description, keywords)
- ✅ Open Graph теги (Facebook, LinkedIn)
- ✅ Twitter Card теги
- ✅ Structured Data (JSON-LD)
- ✅ robots.txt
- ✅ sitemap.xml
- ✅ site.webmanifest (PWA)
- ✅ Canonical URLs
- ✅ Google Analytics placeholder

---

## 🎯 Що треба зробити вручну

### 1. Створити OG зображення (5-10 хвилин)

**Інструмент**: [Canva](https://www.canva.com/)

**Розмір**: 1200 x 630 px

**Що додати**:
- Логотип Sloth AI
- Текст: "Sloth AI - AI Асистент для Бізнесу"
- Підзаголовок: "Автоматизація з штучним інтелектом"
- Іконки: 🤖 Telegram • WhatsApp • Instagram

**Куди зберегти**:
```bash
# Завантажте файл як og-image.jpg
# Скопіюйте в:
/opt/sloth/public/og-image.jpg
```

---

### 2. Створити Favicons (5 хвилин)

**Інструмент**: [RealFaviconGenerator](https://realfavicongenerator.net/)

**Кроки**:
1. Завантажте логотип (SVG або PNG, мінімум 512x512)
2. Завантажте пакет файлів
3. Розпакуйте і скопіюйте в `/opt/sloth/public/`

**Файли що будуть створені**:
- favicon.ico
- favicon-16x16.png
- favicon-32x32.png
- apple-touch-icon.png
- android-chrome-192x192.png
- android-chrome-512x512.png

---

### 3. Google Analytics (10 хвилин)

**Інструмент**: [Google Analytics](https://analytics.google.com/)

**Кроки**:
1. Створіть property "Sloth AI"
2. Додайте Web Data Stream
3. URL: `https://sloth-ai.lazysoft.pl`
4. Скопіюйте **Measurement ID** (формат: `G-XXXXXXXXXX`)

**Додайте ID до index.html**:
```bash
nano /opt/sloth/index.html

# Знайдіть і замініть:
G-XXXXXXXXXX → G-ВАШ_РЕАЛЬНИЙ_ID
```

---

### 4. Google Search Console (10 хвилин)

**Інструмент**: [Google Search Console](https://search.google.com/search-console)

**Кроки**:
1. Add property: `https://sloth-ai.lazysoft.pl`
2. Верифікація через HTML file або meta tag
3. Подайте sitemap: `https://sloth-ai.lazysoft.pl/sitemap.xml`

---

### 5. Перезапуск Frontend (1 хвилина)

```bash
cd /opt/sloth
docker compose restart frontend
```

---

## 🔍 Перевірка

### Тести що треба виконати:

```bash
# 1. Перевірте що сайт доступний
curl -I https://sloth-ai.lazysoft.pl

# 2. Перевірте robots.txt
curl https://sloth-ai.lazysoft.pl/robots.txt

# 3. Перевірте sitemap.xml
curl https://sloth-ai.lazysoft.pl/sitemap.xml

# 4. Перевірте OG зображення (після створення)
curl -I https://sloth-ai.lazysoft.pl/og-image.jpg
```

### Онлайн тести:

1. **Facebook Debugger**: https://developers.facebook.com/tools/debug/
   - Введіть: `https://sloth-ai.lazysoft.pl`

2. **Twitter Card Validator**: https://cards-dev.twitter.com/validator
   - Введіть: `https://sloth-ai.lazysoft.pl`

3. **Rich Results Test**: https://search.google.com/test/rich-results
   - Введіть: `https://sloth-ai.lazysoft.pl`

4. **PageSpeed Insights**: https://pagespeed.web.dev/
   - Введіть: `https://sloth-ai.lazysoft.pl`

---

## 📊 Очікувані результати

### SEO Metrics (після індексації, 1-2 тижні):
- ✅ Google Search Console: Indexed pages
- ✅ Lighthouse SEO Score: 90-100
- ✅ Open Graph preview працює
- ✅ Twitter Card preview працює
- ✅ Structured Data валідний

### Performance:
- ✅ Page Load Time: < 3 секунди
- ✅ First Contentful Paint: < 1.8 секунди
- ✅ Largest Contentful Paint: < 2.5 секунди

---

## ⏱️ Загальний час: 30-40 хвилин

1. OG зображення: 10 хв
2. Favicons: 5 хв
3. Google Analytics: 10 хв
4. Google Search Console: 10 хв
5. Тестування: 5 хв

---

## 📞 Потрібна допомога?

Див. детальну документацію: [SEO_SETUP.md](./SEO_SETUP.md)
