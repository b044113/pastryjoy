import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import en from './locales/en.json';
import es from './locales/es.json';

const resources = {
  en: {
    translation: en
  },
  es: {
    translation: es
  }
};

// Determine initial language
// Priority: 1) User settings (loaded by AuthContext after auth), 2) localStorage, 3) 'en'
const getInitialLanguage = (): string => {
  const savedLanguage = localStorage.getItem('language');
  if (savedLanguage && (savedLanguage === 'en' || savedLanguage === 'es')) {
    return savedLanguage;
  }
  return 'en';
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: getInitialLanguage(),
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
