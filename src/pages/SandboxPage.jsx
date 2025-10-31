import ChatWindow from '../components/sandbox/ChatWindow';
import PhotoUploadTest from '../components/sandbox/PhotoUploadTest';

const SandboxPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Test Sandbox</h1>
        <p className="text-gray-600">Test your AI assistant before going live</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ChatWindow />
        </div>

        <div>
          <PhotoUploadTest />
        </div>
      </div>
    </div>
  );
};

export default SandboxPage;
