import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  GraduationCap,
  FlaskConical,
  Plug2,
  MessageSquare,
  Settings,
  CreditCard
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useTranslation } from 'react-i18next';

const Sidebar = () => {
  const { user } = useAuth();
  const { t } = useTranslation();

  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: t('nav.dashboard') },
    { to: '/training', icon: GraduationCap, label: t('nav.training') },
    { to: '/sandbox', icon: FlaskConical, label: t('nav.sandbox') },
    { to: '/integrations', icon: Plug2, label: t('nav.integrations') },
    { to: '/history', icon: MessageSquare, label: t('nav.history') },
    { to: '/settings', icon: Settings, label: t('nav.settings') },
    { to: '/billing', icon: CreditCard, label: t('nav.billing') },
  ];

  return (
    <div className="w-64 bg-white border-r border-gray-200 min-h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-14 h-14 flex-shrink-0 flex items-center justify-center">
            <img
              src="/logo/logo.svg"
              alt="Logo"
              className="w-full h-full object-contain"
              onError={(e) => {
                e.target.style.display = 'none';
                const fallback = e.target.nextSibling;
                if (fallback) {
                  fallback.classList.remove('hidden');
                  fallback.classList.add('flex');
                }
              }}
            />
            <div
              className="w-14 h-14 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg items-center justify-center text-white font-bold text-xl hidden"
            >
              S
            </div>
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-800">Sloth</h1>
            <p className="text-xs text-gray-500">by Lazysoft</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-600'
                  : 'text-gray-700 hover:bg-gray-100'
              }`
            }
          >
            <item.icon size={20} />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      {/* User info */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
            <span className="text-primary-600 font-semibold">
              {user?.name?.[0] || 'U'}
            </span>
          </div>
          <div className="flex-1">
            <p className="font-medium text-sm">{user?.name || 'User'}</p>
            <p className="text-xs text-gray-500">
              {user?.subscription_status === 'trial' ? (
                <span className="text-orange-500">
                  🟢 {t('trial.active')}: {user?.trial_days_left}d
                </span>
              ) : (
                <span className="text-green-500">✓ Active</span>
              )}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
