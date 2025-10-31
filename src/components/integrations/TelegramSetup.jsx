import { X, Copy } from 'lucide-react';
import { useState } from 'react';

const TelegramSetup = ({ onClose }) => {
  const [botToken, setBotToken] = useState('');
  const webhookUrl = 'https://api.yourapp.com/webhook/telegram';

  const handleCopy = () => {
    navigator.clipboard.writeText(webhookUrl);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 max-w-lg w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold">Setup Telegram Bot</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-600 mb-2">
              1. Open Telegram and search for @BotFather
            </p>
            <p className="text-sm text-gray-600 mb-2">
              2. Send /newbot and follow the instructions
            </p>
            <p className="text-sm text-gray-600 mb-4">
              3. Copy the bot token and paste it below
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Bot Token</label>
            <input
              type="text"
              value={botToken}
              onChange={(e) => setBotToken(e.target.value)}
              placeholder="123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"
              className="input"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Webhook URL</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={webhookUrl}
                readOnly
                className="input flex-1 bg-gray-50"
              />
              <button onClick={handleCopy} className="btn-secondary">
                <Copy size={18} />
              </button>
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <button className="btn-primary flex-1">Connect</button>
            <button onClick={onClose} className="btn-secondary flex-1">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TelegramSetup;
