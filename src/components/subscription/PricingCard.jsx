import { useTranslation } from 'react-i18next';
import { Check } from 'lucide-react';
import { useState } from 'react';
import { subscriptionAPI } from '../../api/subscription';

const PricingCard = ({ id, name, price, period, description, features, popular, badge }) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const isFree = id === 'free';

  const handleSelectPlan = async () => {
    // Free plan - just reload (already assigned on registration)
    if (isFree) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await subscriptionAPI.createCheckout(id, 'monthly');
      // Redirect to Stripe checkout
      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || t('common.error'));
      setLoading(false);
    }
  };

  return (
    <div
      className={`card relative ${
        popular
          ? 'border-2 border-primary-500 shadow-lg scale-105'
          : 'border border-gray-200'
      }`}
    >
      {popular && (
        <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
          <span className="bg-primary-500 text-white px-4 py-1 rounded-full text-sm font-medium">
            {t('pricing.mostPopular')}
          </span>
        </div>
      )}
      {badge && !popular && (
        <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
          <span className="bg-green-500 text-white px-4 py-1 rounded-full text-sm font-medium">
            {badge}
          </span>
        </div>
      )}

      <div className="text-center mb-6">
        <h3 className="text-2xl font-bold mb-2">{name}</h3>
        <p className="text-gray-600 text-sm mb-4">{description}</p>
        <div className="flex items-baseline justify-center gap-1">
          <span className="text-4xl font-bold">${price}</span>
          <span className="text-gray-500">/{period}</span>
        </div>
      </div>

      <ul className="space-y-3 mb-6">
        {features.map((feature, index) => (
          <li key={index} className="flex items-start gap-2">
            <Check className="text-green-500 flex-shrink-0 mt-0.5" size={18} />
            <span className="text-sm text-gray-700">{feature}</span>
          </li>
        ))}
      </ul>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      <button
        onClick={handleSelectPlan}
        disabled={loading || isFree}
        className={`w-full py-3 rounded-lg font-medium transition-colors ${
          isFree
            ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
            : popular
            ? 'bg-primary-500 hover:bg-primary-600 text-white disabled:bg-primary-300'
            : 'bg-gray-100 hover:bg-gray-200 text-gray-800 disabled:bg-gray-50'
        }`}
      >
        {isFree
          ? t('pricing.currentPlan')
          : loading
          ? t('common.loading')
          : `${t('pricing.choose')} ${name}`}
      </button>
    </div>
  );
};

export default PricingCard;
