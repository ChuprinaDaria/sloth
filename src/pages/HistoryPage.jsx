import { useState } from 'react';
import ChatList from '../components/history/ChatList';
import ChatDetail from '../components/history/ChatDetail';

const HistoryPage = () => {
  const [selectedChat, setSelectedChat] = useState(null);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Chat History</h1>
        <p className="text-gray-600">View all conversations with your AI</p>
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
                <p className="text-lg">Select a chat to view details</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HistoryPage;
