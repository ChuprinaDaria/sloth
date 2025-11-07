import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Download, Smartphone, Apple } from 'lucide-react';

const DownloadApp = ({ className = '' }) => {
  const { t } = useTranslation();
  const [appLinks, setAppLinks] = useState(null);
  const [platform, setPlatform] = useState('unknown');

  useEffect(() => {
    // Detect platform
    const ua = navigator.userAgent.toLowerCase();
    if (ua.includes('iphone') || ua.includes('ipad')) {
      setPlatform('ios');
    } else if (ua.includes('android')) {
      setPlatform('android');
    } else {
      setPlatform('desktop');
    }

    // Fetch app download links
    fetch('/api/core/app-download-links/')
      .then(res => res.json())
      .then(data => setAppLinks(data))
      .catch(err => console.error('Failed to fetch app links:', err));
  }, []);

  const handleDownload = () => {
    if (!appLinks) return;

    if (appLinks.coming_soon) {
      alert(t('downloadApp.comingSoon'));
      return;
    }

    const ua = navigator.userAgent.toLowerCase();

    if (ua.includes('iphone') || ua.includes('ipad')) {
      if (appLinks.ios_download_url) {
        window.location.href = appLinks.ios_download_url;
      }
    } else if (ua.includes('android')) {
      if (appLinks.android_download_url) {
        window.location.href = appLinks.android_download_url;
      }
    } else {
      // Desktop - show options
      alert(t('downloadApp.scanQR'));
    }
  };

  if (!appLinks) return null;

  return (
    <button
      onClick={handleDownload}
      className={`inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-500 to-pink-500 text-white rounded-lg font-semibold hover:from-green-600 hover:to-pink-600 transition-all ${className}`}
    >
      {platform === 'ios' ? (
        <Apple size={20} />
      ) : platform === 'android' ? (
        <Smartphone size={20} />
      ) : (
        <Download size={20} />
      )}
      <span>{t('downloadApp.button')}</span>
    </button>
  );
};

export default DownloadApp;
