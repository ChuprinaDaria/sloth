import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import IntegrationCard from '../components/integrations/IntegrationCard';
import TelegramSetup from '../components/integrations/TelegramSetup';
import WhatsAppSetup from '../components/integrations/WhatsAppSetup';
import CalendarSetup from '../components/integrations/CalendarSetup';
import { MessageCircle, Send, Calendar } from 'lucide-react';

const IntegrationsPage = () => {
  const { t } = useTranslation();
  const [activeSetup, setActiveSetup] = useState(null);

  const integrations = [
    {
      id: 'telegram',
      name: t('integrations.telegram'),
      icon: Send,
      description: t('integrations.telegramDesc'),
      status: 'disconnected',
      color: 'blue',
    },
    {
      id: 'whatsapp',
      name: t('integrations.whatsapp'),
      icon: MessageCircle,
      description: t('integrations.whatsappDesc'),
      status: 'disconnected',
      color: 'green',
    },
    {
      id: 'calendar',
      name: t('integrations.calendar'),
      icon: Calendar,
      description: t('integrations.calendarDesc'),
      status: 'disconnected',
      color: 'purple',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{t('integrations.title')}</h1>
        <p className="text-gray-600">{t('integrations.subtitle')}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {integrations.map((integration) => (
          <IntegrationCard
            key={integration.id}
            {...integration}
            onSetup={() => setActiveSetup(integration.id)}
          />
        ))}
      </div>

      {activeSetup === 'telegram' && <TelegramSetup onClose={() => setActiveSetup(null)} />}
      {activeSetup === 'whatsapp' && <WhatsAppSetup onClose={() => setActiveSetup(null)} />}
      {activeSetup === 'calendar' && <CalendarSetup onClose={() => setActiveSetup(null)} />}
    </div>
  );
};

export default IntegrationsPage;
