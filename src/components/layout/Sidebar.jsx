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

const Sidebar = () => {
  const { user } = useAuth();

  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/training', icon: GraduationCap, label: 'Train AI' },
    { to: '/sandbox', icon: FlaskConical, label: 'Test Sandbox' },
    { to: '/integrations', icon: Plug2, label: 'Integrations' },
    { to: '/history', icon: MessageSquare, label: 'Chat History' },
    { to: '/settings', icon: Settings, label: 'Settings' },
    { to: '/billing', icon: CreditCard, label: 'Billing' },
  ];

  return (
    <div className="w-64 bg-white border-r border-gray-200 min-h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-500 to-accent-500 bg-clip-text text-transparent">
          💇 Salon AI
        </h1>
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
                  🟢 Trial: {user?.trial_days_left}d left
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
