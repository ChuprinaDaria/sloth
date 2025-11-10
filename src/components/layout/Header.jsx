import { Bell, LogOut, Menu } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../common/LanguageSwitcher';

const Header = ({ onMenuClick }) => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header className="bg-white border-b border-gray-200 px-4 md:px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {/* Mobile menu button */}
          <button
            onClick={onMenuClick}
            className="md:hidden p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
          >
            <Menu size={24} />
          </button>

          <div>
            <h2 className="text-lg md:text-xl font-semibold text-gray-800">{t('dashboard.welcomeBack')}</h2>
            <p className="text-xs md:text-sm text-gray-500 hidden sm:block">{t('dashboard.manageAssistant')}</p>
          </div>
        </div>

        <div className="flex items-center gap-2 md:gap-4">
          <LanguageSwitcher />

          <button className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-lg">
            <Bell size={20} />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>

          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-2 md:px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg"
          >
            <LogOut size={18} />
            <span className="hidden md:inline">{t('common.logout')}</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
