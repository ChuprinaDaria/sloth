import { useState } from 'react';
import IntegrationCard from '../components/integrations/IntegrationCard';
import TelegramSetup from '../components/integrations/TelegramSetup';
import WhatsAppSetup from '../components/integrations/WhatsAppSetup';
import CalendarSetup from '../components/integrations/CalendarSetup';
import { MessageCircle, Send, Calendar } from 'lucide-react';

const IntegrationsPage = () => {
  const [activeSetup, setActiveSetup] = useState(null);

  const integrations = [
    {
      id: 'telegram',
      name: 'Telegram',
      icon: Send,
      description: 'Connect to Telegram Bot',
      status: 'disconnected',
      color: 'blue',
    },
    {
      id: 'whatsapp',
      name: 'WhatsApp',
      icon: MessageCircle,
      description: 'Connect to WhatsApp Business',
      status: 'disconnected',
      color: 'green',
    },
    {
      id: 'calendar',
      name: 'Calendar',
      icon: Calendar,
      description: 'Sync with Google Calendar',
      status: 'disconnected',
      color: 'purple',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Integrations</h1>
        <p className="text-gray-600">Connect your AI to messaging platforms</p>
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
