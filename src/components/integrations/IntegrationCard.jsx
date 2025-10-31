import { useTranslation } from 'react-i18next';
import { CheckCircle, Circle } from 'lucide-react';

const IntegrationCard = ({ name, icon: Icon, description, status, color, onSetup }) => {
  const { t } = useTranslation();
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
  };

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${colorClasses[color]}`}>
        <Icon size={24} />
      </div>

      <h3 className="text-lg font-semibold mb-2">{name}</h3>
      <p className="text-sm text-gray-600 mb-4">{description}</p>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {status === 'connected' ? (
            <>
              <CheckCircle className="text-green-500" size={18} />
              <span className="text-sm font-medium text-green-600">{t('integrations.connected')}</span>
            </>
          ) : (
            <>
              <Circle className="text-gray-400" size={18} />
              <span className="text-sm text-gray-500">{t('integrations.notConnected')}</span>
            </>
          )}
        </div>

        <button onClick={onSetup} className="btn-primary text-sm">
          {status === 'connected' ? t('integrations.configure') : t('integrations.setup')}
        </button>
      </div>
    </div>
  );
};

export default IntegrationCard;
