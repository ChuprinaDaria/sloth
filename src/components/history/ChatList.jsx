import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { MessageSquare, Send, MessageCircle, Instagram } from 'lucide-react';
import { agentAPI } from '../../api/agent';

const ChatList = ({ onSelectChat, selectedChatId }) => {
  const { t } = useTranslation();
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      setLoading(true);
      const response = await agentAPI.getChatHistory();
      const conversations = response?.data?.results || response?.data || [];
      
      // Format conversations with source badges
      const formattedChats = conversations.map(conv => {
        const lastMessage = conv.last_message;
        const lastMessageText = lastMessage?.content || t('history.noMessages');
        const timestamp = formatTimestamp(conv.updated_at || conv.created_at);
        
        return {
          id: conv.id,
          title: conv.title || getDefaultTitle(conv.source, conv.external_id),
          source: conv.source || 'web',
          lastMessage: lastMessageText,
          timestamp: timestamp,
          messageCount: conv.message_count || 0,
          updatedAt: conv.updated_at || conv.created_at,
        };
      });
      
      setChats(formattedChats);
    } catch (error) {
      console.error('Error loading conversations:', error);
      setChats([]);
    } finally {
      setLoading(false);
    }
  };

  const formatTimestamp = (dateString) => {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return t('history.justNow');
    if (diffMins < 60) return `${diffMins} ${t('history.minutesAgo')}`;
    if (diffHours < 24) return `${diffHours} ${t('history.hoursAgo')}`;
    if (diffDays < 7) return `${diffDays} ${t('history.daysAgo')}`;
    
    return date.toLocaleDateString();
  };

  const getDefaultTitle = (source, externalId) => {
    const sourceNames = {
      'web': t('history.webChat'),
      'telegram': t('history.telegramChat'),
      'whatsapp': t('history.whatsappChat'),
      'instagram': t('history.instagramChat'),
      'api': t('history.apiChat'),
    };
    return sourceNames[source] || t('history.chat');
  };

  const getSourceIcon = (source) => {
    switch (source) {
      case 'telegram':
        return <Send size={14} className="text-blue-500" />;
      case 'whatsapp':
        return <MessageCircle size={14} className="text-green-500" />;
      case 'instagram':
        return <Instagram size={14} className="text-pink-500" />;
      default:
        return <MessageSquare size={14} className="text-gray-500" />;
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
      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${badge.color}`}>
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
    <div className="card h-[600px] overflow-y-auto">
      <h3 className="text-lg font-semibold mb-4">{t('history.allConversations')}</h3>

      {chats.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <MessageSquare size={48} className="mx-auto mb-2 opacity-50" />
          <p>{t('history.noConversations')}</p>
        </div>
      ) : (
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
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  {getSourceIcon(chat.source)}
                  <span className="font-medium text-sm truncate">{chat.title}</span>
                </div>
                {getSourceBadge(chat.source)}
              </div>
              <p className="text-sm text-gray-600 truncate mt-1">{chat.lastMessage}</p>
              <div className="flex items-center justify-between mt-1">
                <p className="text-xs text-gray-400">{chat.timestamp}</p>
                {chat.messageCount > 0 && (
                  <span className="text-xs text-gray-400">
                    {chat.messageCount} {t('history.messages')}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ChatList;
