import { useTranslation } from 'react-i18next';
import { useState, useEffect } from 'react';
import StatsCard from '../components/dashboard/StatsCard';
import ActivityFeed from '../components/dashboard/ActivityFeed';
import SmartAnalytics from '../components/dashboard/SmartAnalytics';
import { MessageSquare, Users, TrendingUp, Percent } from 'lucide-react';
import { agentAPI } from '../api/agent';

const DashboardPage = () => {
  const { t } = useTranslation();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await agentAPI.getDashboardStats();
        setDashboardData(response.data);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);
  
  const stats = dashboardData ? [
    { 
      label: t('dashboard.totalChats'), 
      value: String(dashboardData.stats.total_chats), 
      icon: MessageSquare, 
      change: dashboardData.stats.chats_change, 
      color: 'primary' 
    },
    { 
      label: t('dashboard.activeUsers'), 
      value: String(dashboardData.stats.active_users), 
      icon: Users, 
      change: dashboardData.stats.users_change, 
      color: 'accent' 
    },
    { 
      label: t('dashboard.bookings'), 
      value: String(dashboardData.stats.bookings), 
      icon: TrendingUp, 
      change: dashboardData.stats.bookings_change, 
      color: 'green' 
    },
    { 
      label: t('dashboard.conversion'), 
      value: dashboardData.stats.conversion_rate, 
      icon: Percent, 
      change: dashboardData.stats.conversion_change, 
      color: 'blue' 
    },
  ] : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{t('dashboard.title')}</h1>
        <p className="text-gray-600">{t('dashboard.subtitle')}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <StatsCard key={index} {...stat} />
        ))}
      </div>

      {/* Smart Analytics - AI-powered insights */}
      <SmartAnalytics />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">{t('dashboard.recentActivity')}</h3>
          {loading ? (
            <div className="text-center py-8 text-gray-500">Завантаження...</div>
          ) : dashboardData && dashboardData.recent_activity && dashboardData.recent_activity.length > 0 ? (
            <div className="space-y-3">
              {dashboardData.recent_activity.map((activity, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-800">{activity.title}</p>
                    <p className="text-sm text-gray-500">{activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">Немає останньої активності</p>
          )}
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-4">{t('dashboard.topServices')}</h3>
          {loading ? (
            <div className="text-center py-8 text-gray-500">Завантаження...</div>
          ) : dashboardData && dashboardData.top_services && dashboardData.top_services.length > 0 ? (
            <div className="space-y-3">
              {dashboardData.top_services.map((service, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-gray-700">{service.name}</span>
                  <span className="font-semibold text-primary-600">{service.count} {t('dashboard.bookingsCount')}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">Немає даних про послуги</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
