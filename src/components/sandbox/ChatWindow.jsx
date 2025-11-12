import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Send, User, Bot } from 'lucide-react';
import { agentAPI } from '../../api/agent';

const ChatWindow = () => {
  const { t, i18n } = useTranslation();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [mode, setMode] = useState('client'); // 'client' or 'assistant'

  useEffect(() => {
    if (messages.length === 0) {
      const initialMessage = mode === 'client' 
        ? t('sandbox.helloMessage')
        : t('sandbox.assistantModeWelcome');
      setMessages([
        { id: 1, text: initialMessage, sender: 'ai', timestamp: new Date() },
      ]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [i18n.language, mode]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: input,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError('');

    try {
      const { data } = await agentAPI.testChat(userMessage.text, null, i18n.language, mode);
      const text = typeof data?.message === 'string' ? data.message : (data?.message?.content || t('sandbox.testResponse'));
      const aiMessage = {
        id: Date.now() + 1,
        text,
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (e) {
      const fallback = e.response?.data?.error || t('common.error');
      const aiMessage = {
        id: Date.now() + 1,
        text: fallback,
        sender: 'ai',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
      setError(fallback);
    } finally {
      setLoading(false);
    }
  };

  const handleModeChange = (newMode) => {
    setMode(newMode);
    setMessages([]);
  };

  return (
    <div className="card h-[600px] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">{t('sandbox.chatTest')}</h3>
        <div className="flex gap-2">
          <button
            onClick={() => handleModeChange('client')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              mode === 'client'
                ? 'bg-primary-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <User size={16} className="inline mr-2" />
            {t('sandbox.clientMode')}
          </button>
          <button
            onClick={() => handleModeChange('assistant')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              mode === 'assistant'
                ? 'bg-primary-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <Bot size={16} className="inline mr-2" />
            {t('sandbox.assistantMode')}
          </button>
        </div>
      </div>
      
      <div className="mb-3 p-2 bg-blue-50 rounded-lg text-sm text-blue-800">
        {mode === 'client' ? t('sandbox.clientModeDescription') : t('sandbox.assistantModeDescription')}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] p-3 rounded-lg ${
                msg.sender === 'user'
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.text}</p>
              <p
                className={`text-xs mt-1 ${
                  msg.sender === 'user' ? 'text-primary-100' : 'text-gray-500'
                }`}
              >
                {msg.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 p-3 rounded-lg">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}
        {error && (
          <div className="text-xs text-red-500 px-2">{error}</div>
        )}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder={t('sandbox.typeMessage')}
          className="flex-1 input"
        />
        <button onClick={handleSend} disabled={loading} className="btn-primary">
          <Send size={18} />
        </button>
      </div>
    </div>
  );
};

export default ChatWindow;
