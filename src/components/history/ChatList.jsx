import { MessageSquare } from 'lucide-react';

const ChatList = ({ onSelectChat, selectedChatId }) => {
  // Mock data
  const chats = [
    {
      id: 1,
      customerName: 'Maria Kovalenko',
      lastMessage: 'Thank you for the booking!',
      timestamp: '2 hours ago',
      unread: 0,
    },
    {
      id: 2,
      customerName: 'Olena Shevchenko',
      lastMessage: 'What time slots are available?',
      timestamp: '5 hours ago',
      unread: 2,
    },
    {
      id: 3,
      customerName: 'Ivan Petrenko',
      lastMessage: 'How much is a haircut?',
      timestamp: 'Yesterday',
      unread: 0,
    },
    {
      id: 4,
      customerName: 'Anna Bondarenko',
      lastMessage: 'Can I reschedule my appointment?',
      timestamp: '2 days ago',
      unread: 0,
    },
  ];

  return (
    <div className="card h-[600px] overflow-y-auto">
      <h3 className="text-lg font-semibold mb-4">All Conversations</h3>

      <div className="space-y-2">
        {chats.map((chat) => (
          <div
            key={chat.id}
            onClick={() => onSelectChat(chat)}
            className={`p-3 rounded-lg cursor-pointer transition-colors ${
              selectedChatId === chat.id
                ? 'bg-primary-50 border-2 border-primary-200'
                : 'hover:bg-gray-50 border-2 border-transparent'
            }`}
          >
            <div className="flex items-start justify-between mb-1">
              <div className="flex items-center gap-2">
                <MessageSquare size={16} className="text-gray-500" />
                <span className="font-medium text-sm">{chat.customerName}</span>
              </div>
              {chat.unread > 0 && (
                <span className="bg-primary-500 text-white text-xs px-2 py-0.5 rounded-full">
                  {chat.unread}
                </span>
              )}
            </div>
            <p className="text-sm text-gray-600 truncate">{chat.lastMessage}</p>
            <p className="text-xs text-gray-400 mt-1">{chat.timestamp}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChatList;
