import { Sparkles, X } from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Link } from 'react-router-dom';

const FreeBanner = () => {
  const [visible, setVisible] = useState(true);
  const { user } = useAuth();

  if (!visible) return null;

  // Only show for free plan users
  if (user?.subscription_status !== 'free') return null;

  const conversationsUsed = user?.subscription?.used_conversations || 0;
  const conversationsLimit = user?.subscription?.plan?.max_conversations_per_month || 50;
  const conversationsLeft = Math.max(0, conversationsLimit - conversationsUsed);
  const usagePercent = Math.round((conversationsUsed / conversationsLimit) * 100);

  // Change color based on usage
  const getBannerColor = () => {
    if (usagePercent >= 90) return 'from-red-500 to-orange-500';
    if (usagePercent >= 70) return 'from-orange-500 to-amber-500';
    return 'from-purple-500 to-pink-500';
  };

  return (
    <div className={`bg-gradient-to-r ${getBannerColor()} text-white px-4 md:px-6 py-3`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 md:gap-3 flex-1">
          <Sparkles size={20} className="flex-shrink-0" />
          <span className="font-medium text-sm md:text-base">
            🦥 FREE FOREVER • {conversationsLeft}/{conversationsLimit} conversations left this month
          </span>
        </div>
        <div className="flex items-center gap-2 md:gap-4">
          <Link
            to="/billing"
            className="text-xs md:text-sm underline hover:text-white/80 whitespace-nowrap"
          >
            Upgrade for Unlimited
          </Link>
          <button
            onClick={() => setVisible(false)}
            className="flex-shrink-0"
          >
            <X size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default FreeBanner;
