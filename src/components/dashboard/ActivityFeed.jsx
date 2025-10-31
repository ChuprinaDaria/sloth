import { MessageSquare, Calendar, CheckCircle } from 'lucide-react';

const ActivityFeed = () => {
  const activities = [
    {
      icon: MessageSquare,
      text: 'New chat from Maria K.',
      time: '5 min ago',
      color: 'bg-blue-50 text-blue-600',
    },
    {
      icon: Calendar,
      text: 'Booking confirmed for tomorrow',
      time: '1 hour ago',
      color: 'bg-green-50 text-green-600',
    },
    {
      icon: CheckCircle,
      text: 'AI training completed',
      time: '2 hours ago',
      color: 'bg-primary-50 text-primary-600',
    },
    {
      icon: MessageSquare,
      text: 'New chat from John D.',
      time: '3 hours ago',
      color: 'bg-blue-50 text-blue-600',
    },
  ];

  return (
    <div className="space-y-4">
      {activities.map((activity, index) => (
        <div key={index} className="flex items-start gap-3">
          <div className={`p-2 rounded-lg ${activity.color}`}>
            <activity.icon size={16} />
          </div>
          <div className="flex-1">
            <p className="text-sm text-gray-800">{activity.text}</p>
            <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ActivityFeed;
