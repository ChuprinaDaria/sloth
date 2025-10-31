import { Check } from 'lucide-react';

const PricingCard = ({ name, price, period, description, features, popular }) => {
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
            Most Popular
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

      <button
        className={`w-full py-3 rounded-lg font-medium transition-colors ${
          popular
            ? 'bg-primary-500 hover:bg-primary-600 text-white'
            : 'bg-gray-100 hover:bg-gray-200 text-gray-800'
        }`}
      >
        Choose {name}
      </button>
    </div>
  );
};

export default PricingCard;
