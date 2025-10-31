import PricingCard from './PricingCard';
import { Check } from 'lucide-react';

const PricingPlans = () => {
  const plans = [
    {
      name: 'Starter',
      price: '29',
      period: 'month',
      description: 'Perfect for small salons',
      features: [
        '100 conversations/month',
        '1 integration (Telegram or WhatsApp)',
        'Basic AI training',
        'Email support',
        'Chat history (30 days)',
      ],
      popular: false,
    },
    {
      name: 'Professional',
      price: '79',
      period: 'month',
      description: 'Best for growing businesses',
      features: [
        'Unlimited conversations',
        'All integrations (Telegram, WhatsApp, Instagram)',
        'Advanced AI training',
        'Priority support',
        'Unlimited chat history',
        'Calendar integration',
        'Custom branding',
      ],
      popular: true,
    },
    {
      name: 'Enterprise',
      price: '199',
      period: 'month',
      description: 'For salon chains',
      features: [
        'Everything in Professional',
        'Multiple locations',
        'Dedicated account manager',
        '24/7 phone support',
        'Custom integrations',
        'Advanced analytics',
        'API access',
      ],
      popular: false,
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {plans.map((plan, index) => (
        <PricingCard key={index} {...plan} />
      ))}
    </div>
  );
};

export default PricingPlans;
