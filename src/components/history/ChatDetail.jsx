import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { User, Bot, Send, MessageCircle, Instagram, MessageSquare } from 'lucide-react';
import { agentAPI } from '../../api/agent';

const ChatDetail = ({ chat }) => {
  const { t } = useTranslation();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (chat?.id) {
      loadMessages();
    }
  }, [chat?.id]);

  const loadMessages = async () => {
    try {
      setLoading(true);
      const response = await agentAPI.getChatDetail(chat.id);
      const conversation = response?.data;
      
      if (conversation?.messages) {
        const formattedMessages = conversation.messages.map(msg => ({
          id: msg.id,
          text: msg.content || '',
          sender: msg.role === 'user' ? 'customer' : 'ai',
          timestamp: formatTime(msg.created_at),
          role: msg.role,
        }));
        setMessages(formattedMessages);
      }
    } catch (error) {
      console.error('Error loading messages:', error);
      setMessages([]);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' });
  };

  const getSourceIcon = (source) => {
    switch (source) {
      case 'telegram':
        return <Send size={16} className="text-blue-500" />;
      case 'whatsapp':
        return <MessageCircle size={16} className="text-green-500" />;
      case 'instagram':
        return <Instagram size={16} className="text-pink-500" />;
      default:
        return <MessageSquare size={16} className="text-gray-500" />;
    }
  };

  const getSourceBadge = (source) => {
    const badges = {
      'telegram': { text: 'Telegram', color: 'bg-blue-100 text-blue-700' },
      'whatsapp': { text: 'WhatsApp', color: 'bg-green-100 text-green-700' },
      'instagram': { text: 'Instagram', color: 'bg-pink-100 text-pink-700' },
      'web': { text: t('history.web'), color: 'bg-gray-100 text-gray-700' },
      'api': { text: 'API', color: 'bg-purple-100 text-purple-700' },
    };
    
    const badge = badges[source] || badges['web'];
    return (
      <span className={`text-xs px-2 py-1 rounded-full font-medium ${badge.color}`}>
        {badge.text}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="card h-[600px] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="card h-[600px] flex flex-col">
      <div className="pb-4 border-b border-gray-200 mb-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold">{chat.title || t('history.chat')}</h3>
          {chat.source && getSourceBadge(chat.source)}
        </div>
        <div className="flex items-center gap-2">
          {chat.source && getSourceIcon(chat.source)}
          <p className="text-sm text-gray-500">
            {t('history.lastActive')} {chat.timestamp || formatTime(chat.updatedAt)}
          </p>
        </div>
      </div>

      {messages.length === 0 ? (
        <div className="flex-1 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <MessageSquare size={48} className="mx-auto mb-2 opacity-50" />
            <p>{t('history.noMessages')}</p>
          </div>
        </div>
      ) : (
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
      )}
    </div>
  );
};

export default ChatDetail;
