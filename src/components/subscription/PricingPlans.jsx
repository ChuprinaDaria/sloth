import { useTranslation } from 'react-i18next';
import PricingCard from './PricingCard';

const PricingPlans = () => {
  const { t } = useTranslation();

  const plans = [
    {
      id: 'free',
      name: t('pricing.free'),
      price: '0',
      period: t('pricing.forever'),
      description: t('pricing.freeDesc'),
      features: [
        t('pricing.features.telegramBot'),
        t('pricing.features.dialogs', { count: 20 }),
        t('pricing.features.basicTraining'),
        t('pricing.features.smartAnalytics'),
        t('pricing.features.watermarkedMessages'),
      ],
      popular: false,
      badge: t('pricing.freeBadge'),
    },
    {
      id: 'starter',
      name: t('pricing.starter'),
      price: '14.99',
      period: t('pricing.month'),
      description: t('pricing.starterDesc'),
      features: [
        t('pricing.features.conversations', { count: 100 }),
        t('pricing.features.starterIntegrations'),
        t('pricing.features.basicTraining'),
        t('pricing.features.emailSupport'),
        t('pricing.features.chatHistory30'),
        t('pricing.features.smartAnalytics'),
      ],
      popular: false,
    },
    {
      id: 'professional',
      name: t('pricing.professional'),
      price: '49',
      period: t('pricing.month'),
      description: t('pricing.professionalDesc'),
      features: [
        t('pricing.features.unlimitedConversations'),
        t('pricing.features.allPlatforms'),
        t('pricing.features.instagramEmbeddings'),
        t('pricing.features.calendarAndEmail'),
        t('pricing.features.websiteWidget'),
        t('pricing.features.advancedTraining'),
        t('pricing.features.fullAiAnalytics'),
        t('pricing.features.phoneSupport'),
        t('pricing.features.accountManager'),
        t('pricing.features.apiAccess'),
        t('pricing.features.multipleLocations'),
      ],
      popular: true,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {plans.map((plan) => (
        <PricingCard key={plan.id} {...plan} />
      ))}
    </div>
  );
};

export default PricingPlans;
