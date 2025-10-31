import { useState } from 'react';
import { Sparkles } from 'lucide-react';

const PromptEditor = () => {
  const [prompt, setPrompt] = useState(
    `You are a friendly AI assistant for a beauty salon. Your role is to:
- Answer questions about services and pricing
- Help clients book appointments
- Provide information about available time slots
- Be polite and professional

Always use a warm and welcoming tone.`
  );

  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="text-primary-500" size={20} />
        <h3 className="text-lg font-semibold">AI Behavior Prompt</h3>
      </div>

      <p className="text-sm text-gray-600 mb-4">
        Customize how your AI assistant behaves and responds to customers
      </p>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        className="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none font-mono text-sm"
        placeholder="Enter your AI instructions..."
      />

      <div className="mt-4 flex gap-3">
        <button className="btn-primary">Save Prompt</button>
        <button className="btn-secondary">Reset to Default</button>
      </div>
    </div>
  );
};

export default PromptEditor;
