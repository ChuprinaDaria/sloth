import { X, Sheet, Download, ExternalLink } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useState } from 'react';

const GoogleSheetsSetup = ({ onClose }) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [spreadsheetUrl, setSpreadsheetUrl] = useState(null);

  const handleCreateSpreadsheet = async () => {
    setLoading(true);
    try {
      // TODO: API call to create spreadsheet
      // const response = await axios.post('/api/integrations/sheets/connect/');
      // setSpreadsheetUrl(response.data.spreadsheet_url);

      // Mock for now
      setTimeout(() => {
        setSpreadsheetUrl('https://docs.google.com/spreadsheets/d/example');
        setLoading(false);
      }, 1500);
    } catch (error) {
      console.error('Error creating spreadsheet:', error);
      setLoading(false);
    }
  };

  const handleExportNow = async () => {
    setLoading(true);
    try {
      // TODO: API call to export data
      // await axios.post('/api/integrations/sheets/export/', { export_type: 'all' });

      setTimeout(() => {
        setLoading(false);
        alert(t('integrations.exportNow') + ' ✓');
      }, 1500);
    } catch (error) {
      console.error('Error exporting:', error);
      setLoading(false);
    }
  };

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
          <p className="text-gray-600">
            {t('integrations.sheetsNotice')}
          </p>

          <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
            <p className="text-sm text-emerald-800 mb-2">
              <strong>{t('integrations.sheetsInfo')}</strong>
            </p>
            <ul className="text-sm text-emerald-700 space-y-1 list-disc list-inside">
              {t('integrations.sheetsItems', { returnObjects: true }).map((item, idx) => (
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
