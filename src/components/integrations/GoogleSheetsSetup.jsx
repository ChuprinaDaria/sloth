import { X, Sheet, Download, ExternalLink } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';
import { agentAPI } from '../../api/agent';

const GoogleSheetsSetup = ({ onClose }) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [spreadsheetUrl, setSpreadsheetUrl] = useState(null);
  const [error, setError] = useState('');
  const [exportSuccess, setExportSuccess] = useState(false);

  const handleCreateSpreadsheet = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await agentAPI.connectGoogleSheets();
      const spreadsheetUrl = response.data.spreadsheet_url || response.data.integration?.config?.spreadsheet_url;

      if (!spreadsheetUrl) {
        throw new Error('No spreadsheet URL received from server');
      }

      setSpreadsheetUrl(spreadsheetUrl);
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || t('common.error');
      console.error('Google Sheets connection error:', err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleExportNow = async () => {
    setLoading(true);
    setError('');
    setExportSuccess(false);

    try {
      await agentAPI.exportToSheets('all');
      setExportSuccess(true);
      setTimeout(() => setExportSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.error || err.message || t('common.error'));
    } finally {
      setLoading(false);
    }
  };

  const sheetsItems = t('integrations.sheetsItems', { returnObjects: true });
  const items = Array.isArray(sheetsItems) ? sheetsItems : [];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 max-w-lg w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold">{t('integrations.setupSheets')}</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        <div className="space-y-4">
          {/* Error message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {/* Export success message */}
          {exportSuccess && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm text-green-800">
                ✓ {t('integrations.exportSuccess')}
              </p>
            </div>
          )}

          <p className="text-gray-600">
            {t('integrations.sheetsNotice')}
          </p>

          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
            <p className="text-sm text-emerald-800 mb-2">
              <strong>{t('integrations.sheetsInfo')}</strong>
            </p>
            <ul className="text-sm text-emerald-700 space-y-1 list-disc list-inside">
              {items.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          </div>

          {!spreadsheetUrl ? (
            <div className="space-y-3">
              <div className="text-center py-6">
                <Sheet className="mx-auto text-emerald-500 mb-3" size={48} />
                <p className="text-gray-600 text-sm mb-4">
                  {t('integrations.createSpreadsheet')}
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleCreateSpreadsheet}
                  disabled={loading}
                  className="btn-primary flex-1 flex items-center justify-center gap-2"
                >
                  <Sheet size={18} />
                  {loading ? t('common.loading') : t('integrations.createSpreadsheet')}
                </button>
                <button onClick={onClose} className="btn-secondary flex-1">
                  {t('common.cancel')}
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm text-green-800 font-medium mb-2">
                  ✓ {t('integrations.connected')}
                </p>
                <a
                  href={spreadsheetUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-green-700 hover:text-green-900 flex items-center gap-1"
                >
                  {t('integrations.viewSpreadsheet')}
                  <ExternalLink size={14} />
                </a>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleExportNow}
                  disabled={loading}
                  className="btn-primary flex-1 flex items-center justify-center gap-2"
                >
                  <Download size={18} />
                  {loading ? t('common.loading') : t('integrations.exportNow')}
                </button>
                <button onClick={onClose} className="btn-secondary flex-1">
                  {t('common.close')}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GoogleSheetsSetup;
