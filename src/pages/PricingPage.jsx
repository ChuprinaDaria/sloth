import PricingPlans from '../components/subscription/PricingPlans';

const PricingPage = () => {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Choose Your Plan</h1>
        <p className="text-gray-600">Select the perfect plan for your salon</p>
      </div>

      <PricingPlans />
    </div>
  );
};

export default PricingPage;
