import { useTranslation } from 'react-i18next';
import PricingCard from './PricingCard';
import { Check } from 'lucide-react';

const PricingPlans = () => {
  const { t } = useTranslation();
  
  const plans = [
    {
      id: 'starter',
      name: t('pricing.starter'),
      price: '14.99',
      period: t('pricing.month'),
      description: t('pricing.starterDesc'),
      features: [
        t('pricing.features.conversations', { count: 100 }),
        t('pricing.features.integration'),
        t('pricing.features.basicTraining'),
        t('pricing.features.emailSupport'),
        t('pricing.features.chatHistory'),
      ],
      popular: false,
    },
    {
      id: 'professional',
      name: t('pricing.professional'),
      price: '59',
      period: t('pricing.month'),
      description: t('pricing.professionalDesc'),
      features: [
        t('pricing.features.unlimitedConversations'),
        t('pricing.features.allIntegrations'),
        t('pricing.features.advancedTraining'),
        t('pricing.features.prioritySupport'),
        t('pricing.features.unlimitedHistory'),
        t('pricing.features.calendarIntegration'),
        t('pricing.features.customBranding'),
      ],
      popular: true,
    },
    {
      id: 'enterprise',
      name: t('pricing.enterprise'),
      price: '99',
      period: t('pricing.month'),
      description: t('pricing.enterpriseDesc'),
      features: [
        t('pricing.features.everythingProfessional'),
        t('pricing.features.multipleLocations'),
        t('pricing.features.accountManager'),
        t('pricing.features.phoneSupport'),
        t('pricing.features.customIntegrations'),
        t('pricing.features.advancedAnalytics'),
        t('pricing.features.apiAccess'),
      ],
      popular: false,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {plans.map((plan, index) => (
        <PricingCard key={plan.id} {...plan} />
      ))}
    </div>
  );
};

export default PricingPlans;
