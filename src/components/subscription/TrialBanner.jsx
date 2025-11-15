import { AlertCircle, X, Sparkles } from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Link } from 'react-router-dom';

const TrialBanner = () => {
  const [visible, setVisible] = useState(true);
  const { user } = useAuth();

  if (!visible) return null;

  return (
    <div className="bg-gradient-to-r from-orange-500 to-amber-500 text-white px-6 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Sparkles size={20} />
          <span className="font-medium">
            Trial Active - {user?.trial_days_left} days remaining
          </span>
        </div>
        <div className="flex items-center gap-4">
          <Link to="/billing" className="text-sm underline hover:text-orange-100">
            Upgrade Now
          </Link>
          <button onClick={() => setVisible(false)}>
            <X size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default TrialBanner;
