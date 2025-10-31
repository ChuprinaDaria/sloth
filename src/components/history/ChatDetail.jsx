import { useTranslation } from 'react-i18next';
import { User, Bot } from 'lucide-react';

const ChatDetail = ({ chat }) => {
  const { t } = useTranslation();
  
  // Mock messages
  const messages = [
    {
      id: 1,
      text: 'Hello! I would like to book an appointment',
      sender: 'customer',
      timestamp: '10:30 AM',
    },
    {
      id: 2,
      text: 'Hello! I would be happy to help you book an appointment. What service are you interested in?',
      sender: 'ai',
      timestamp: '10:30 AM',
    },
    {
      id: 3,
      text: 'I need a haircut and coloring',
      sender: 'customer',
      timestamp: '10:31 AM',
    },
    {
      id: 4,
      text: 'Great! We have the following available slots for haircut and coloring this week:\n- Tuesday at 2:00 PM\n- Wednesday at 11:00 AM\n- Friday at 3:00 PM\n\nWhich time works best for you?',
      sender: 'ai',
      timestamp: '10:31 AM',
    },
    {
      id: 5,
      text: 'Wednesday at 11:00 AM sounds perfect!',
      sender: 'customer',
      timestamp: '10:32 AM',
    },
    {
      id: 6,
      text: 'Excellent! I have booked your appointment for Wednesday at 11:00 AM. You will receive a confirmation message shortly. Is there anything else I can help you with?',
      sender: 'ai',
      timestamp: '10:32 AM',
    },
  ];

  return (
    <div className="card h-[600px] flex flex-col">
      <div className="pb-4 border-b border-gray-200 mb-4">
        <h3 className="text-lg font-semibold">{chat.customerName}</h3>
        <p className="text-sm text-gray-500">{t('history.lastActive')} {chat.timestamp}</p>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.sender === 'customer' ? '' : 'flex-row-reverse'}`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                msg.sender === 'customer'
                  ? 'bg-gray-200 text-gray-600'
                  : 'bg-primary-100 text-primary-600'
              }`}
            >
              {msg.sender === 'customer' ? <User size={16} /> : <Bot size={16} />}
            </div>

            <div className="flex-1">
              <div
                className={`p-3 rounded-lg ${
                  msg.sender === 'customer' ? 'bg-gray-100' : 'bg-primary-50'
                }`}
              >
                <p className="text-sm whitespace-pre-line">{msg.text}</p>
              </div>
              <p className="text-xs text-gray-400 mt-1">{msg.timestamp}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChatDetail;
