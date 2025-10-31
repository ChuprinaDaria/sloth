import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import translations
import enTranslation from './locales/en/translation.json';
import ukTranslation from './locales/uk/translation.json';
import plTranslation from './locales/pl/translation.json';
import deTranslation from './locales/de/translation.json';

const resources = {
  en: { translation: enTranslation },
  uk: { translation: ukTranslation },
  pl: { translation: plTranslation },
  de: { translation: deTranslation },
};

// Get saved language or use browser language
const savedLanguage = localStorage.getItem('language');
const browserLanguage = navigator.language.split('-')[0];
const defaultLanguage = savedLanguage || (resources[browserLanguage] ? browserLanguage : 'en');

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: defaultLanguage,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

// Save language when it changes
i18n.on('languageChanged', (lng) => {
  localStorage.setItem('language', lng);
});

export default i18n;
