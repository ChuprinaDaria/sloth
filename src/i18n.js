import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import translations
import enTranslation from './locales/en/translation.json';
import ukTranslation from './locales/uk/translation.json';
import plTranslation from './locales/pl/translation.json';
import deTranslation from './locales/de/translation.json';
import itTranslation from './locales/it/translation.json';
import frTranslation from './locales/fr/translation.json';
import noTranslation from './locales/no/translation.json';
import svTranslation from './locales/sv/translation.json';
import beTranslation from './locales/be/translation.json';
import esTranslation from './locales/es/translation.json';

const resources = {
  en: { translation: enTranslation },
  uk: { translation: ukTranslation },
  pl: { translation: plTranslation },
  de: { translation: deTranslation },
  it: { translation: itTranslation },
  fr: { translation: frTranslation },
  no: { translation: noTranslation },
  sv: { translation: svTranslation },
  be: { translation: beTranslation },
  es: { translation: esTranslation },
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
