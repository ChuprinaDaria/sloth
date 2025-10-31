import StatsCard from '../components/dashboard/StatsCard';
import ActivityFeed from '../components/dashboard/ActivityFeed';
import { MessageSquare, Users, TrendingUp, Percent } from 'lucide-react';

const DashboardPage = () => {
  const stats = [
    { label: 'Total Chats', value: '340', icon: MessageSquare, change: '+12%', color: 'primary' },
    { label: 'Active Users', value: '127', icon: Users, change: '+8%', color: 'accent' },
    { label: 'Bookings', value: '89', icon: TrendingUp, change: '+23%', color: 'green' },
    { label: 'Conversion', value: '32%', icon: Percent, change: '+5%', color: 'blue' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-gray-600">Overview of your AI assistant performance</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <StatsCard key={index} {...stat} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
          <ActivityFeed />
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Top Services</h3>
          <div className="space-y-3">
            {['Balayage', 'Haircut', 'Coloring', 'Styling'].map((service, index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-gray-700">{service}</span>
                <span className="font-semibold text-primary-600">{45 - index * 7} bookings</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
