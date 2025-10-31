import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import ChatList from '../components/history/ChatList';
import ChatDetail from '../components/history/ChatDetail';

const HistoryPage = () => {
  const { t } = useTranslation();
  const [selectedChat, setSelectedChat] = useState(null);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{t('history.title')}</h1>
        <p className="text-gray-600">{t('history.subtitle')}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ChatList onSelectChat={setSelectedChat} selectedChatId={selectedChat?.id} />
        </div>

        <div className="lg:col-span-2">
          {selectedChat ? (
            <ChatDetail chat={selectedChat} />
          ) : (
            <div className="card h-full flex items-center justify-center">
              <div className="text-center text-gray-500">
                <p className="text-lg">{t('history.selectChat')}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HistoryPage;
