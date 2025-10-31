import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import TrialBanner from '../subscription/TrialBanner';
import { useAuth } from '../../context/AuthContext';

const Layout = () => {
  const { user } = useAuth();

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        {user?.subscription_status === 'trial' && <TrialBanner />}
        <Header />
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
