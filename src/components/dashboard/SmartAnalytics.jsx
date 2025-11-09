import { Brain, TrendingUp, AlertTriangle, Clock, Users, Lightbulb } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { agentAPI } from '../../api/agent';

const SmartAnalytics = () => {
  const { t, i18n } = useTranslation();
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadInsights();
  }, [i18n.language]);

  const loadInsights = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await agentAPI.getSmartInsights(i18n.language);
      setInsights(response.data);
    } catch (err) {
      console.error('Error loading insights:', err);
      setError(err.response?.data?.error || 'Failed to load insights');
    } finally {
      setLoading(false);
    }
  };

  const getInsightIcon = (type) => {
    const icons = {
      trend: TrendingUp,
      warning: AlertTriangle,
      time: Clock,
      clients: Users,
      recommendation: Lightbulb,
    };
    return icons[type] || Brain;
  };

  const getInsightColor = (type) => {
    const colors = {
      trend: 'bg-blue-50 border-blue-200 text-blue-700',
      warning: 'bg-orange-50 border-orange-200 text-orange-700',
      time: 'bg-purple-50 border-purple-200 text-purple-700',
      clients: 'bg-green-50 border-green-200 text-green-700',
      recommendation: 'bg-yellow-50 border-yellow-200 text-yellow-700',
    };
    return colors[type] || 'bg-gray-50 border-gray-200 text-gray-700';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <Brain className="text-primary-500" size={24} />
          <h2 className="text-xl font-semibold">{t('dashboard.smartAnalytics')}</h2>
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-full"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <Brain className="text-primary-500" size={24} />
          <h2 className="text-xl font-semibold">{t('dashboard.smartAnalytics')}</h2>
        </div>
        <div className="text-center py-8">
          <AlertTriangle className="mx-auto text-orange-500 mb-2" size={48} />
          <p className="text-gray-600">{t('dashboard.analyticsError')}</p>
          <button
            onClick={loadInsights}
            className="mt-4 btn-secondary"
          >
            {t('common.retry')}
          </button>
        </div>
      </div>
    );
  }

  if (!insights || insights.insights?.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <Brain className="text-primary-500" size={24} />
          <h2 className="text-xl font-semibold">{t('dashboard.smartAnalytics')}</h2>
        </div>
        <div className="text-center py-8">
          <Brain className="mx-auto text-gray-400 mb-2" size={48} />
          <p className="text-gray-600">{t('dashboard.noDataYet')}</p>
          <p className="text-sm text-gray-500 mt-2">
            {t('dashboard.noDataDescription')}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 md:p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Brain className="text-primary-500" size={24} />
          <h2 className="text-xl font-semibold">{t('dashboard.smartAnalytics')}</h2>
        </div>
        <button
          onClick={loadInsights}
          className="text-sm text-primary-600 hover:text-primary-700"
        >
          {t('common.refresh')}
        </button>
      </div>

      <div className="space-y-4">
        {insights.insights.map((insight, index) => {
          const Icon = getInsightIcon(insight.type);
          const colorClass = getInsightColor(insight.type);

          return (
            <div
              key={index}
              className={`border rounded-lg p-4 ${colorClass}`}
            >
              <div className="flex items-start gap-3">
                <Icon size={20} className="flex-shrink-0 mt-1" />
                <div className="flex-1">
                  <h3 className="font-semibold mb-1">{insight.title}</h3>
                  <p className="text-sm opacity-90">{insight.message}</p>
                  {insight.action && (
                    <p className="text-sm font-medium mt-2">
                      💡 {insight.action}
                    </p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {insights.summary && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h3 className="font-semibold text-gray-800 mb-2">
            {t('dashboard.summary')}
          </h3>
          <p className="text-sm text-gray-600">{insights.summary}</p>
        </div>
      )}

      <div className="mt-4 text-xs text-gray-500 text-center">
        {t('dashboard.aiGenerated')} • {t('dashboard.lastUpdated')}: {new Date(insights.generated_at).toLocaleString()}
      </div>
    </div>
  );
};

export default SmartAnalytics;
