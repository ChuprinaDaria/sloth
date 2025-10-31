import { X } from 'lucide-react';

const CalendarSetup = ({ onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 max-w-lg w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold">Setup Calendar Integration</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        <div className="space-y-4">
          <p className="text-gray-600">
            Connect your Google Calendar to enable automatic booking management.
          </p>

          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <p className="text-sm text-purple-800 mb-2">
              <strong>What will be synced:</strong>
            </p>
            <ul className="text-sm text-purple-700 space-y-1 list-disc list-inside">
              <li>New appointments booked by AI</li>
              <li>Available time slots</li>
              <li>Booking confirmations</li>
              <li>Cancellations and rescheduling</li>
            </ul>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Calendar Email</label>
            <input
              type="email"
              placeholder="your-calendar@gmail.com"
              className="input"
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button className="btn-primary flex-1">
              Connect with Google
            </button>
            <button onClick={onClose} className="btn-secondary flex-1">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CalendarSetup;
