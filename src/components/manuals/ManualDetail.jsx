import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Video, ThumbsUp, ThumbsDown, Eye, Calendar, CheckCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { manualsAPI } from '../../api/manuals';

const ManualDetail = ({ manual }) => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFeedback = async (isHelpful) => {
    if (feedbackSubmitted || isSubmitting) return;

    setIsSubmitting(true);
    try {
      await manualsAPI.submitFeedback(manual.id, { is_helpful: isHelpful });
      setFeedbackSubmitted(true);
      setTimeout(() => setFeedbackSubmitted(false), 3000);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getCategoryColor = (integrationType) => {
    const colors = {
      telegram: 'bg-blue-100 text-blue-700',
      whatsapp: 'bg-green-100 text-green-700',
      instagram: 'bg-pink-100 text-pink-700',
      calendar: 'bg-purple-100 text-purple-700',
      sheets: 'bg-emerald-100 text-emerald-700',
      general: 'bg-gray-100 text-gray-700',
    };
    return colors[integrationType] || colors.general;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Back Button */}
      <button
        onClick={() => navigate('/manuals')}
        className="flex items-center gap-2 text-gray-600 hover:text-primary-600 mb-6 transition-colors"
      >
        <ArrowLeft size={20} />
        {t('manuals.backToList')}
      </button>

      {/* Header */}
      <div className="bg-white rounded-xl border border-gray-200 p-8 mb-6">
        {/* Category Badge */}
        <div className="mb-4">
          <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getCategoryColor(manual.integration_type)}`}>
            {t(`manuals.category.${manual.integration_type}`)}
          </span>
        </div>

        {/* Title */}
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          {manual.title}
        </h1>

        {/* Meta Info */}
        <div className="flex flex-wrap items-center gap-6 text-sm text-gray-600">
          <div className="flex items-center gap-2">
            <Eye size={18} />
            {t('manuals.views', { count: manual.views_count || 0 })}
          </div>
          {manual.updated_at && (
            <div className="flex items-center gap-2">
              <Calendar size={18} />
              {t('manuals.lastUpdated', { date: formatDate(manual.updated_at) })}
            </div>
          )}
        </div>
      </div>

      {/* Video Tutorial */}
      {manual.video_url && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Video className="text-primary-500" />
            {t('manuals.videoTutorial')}
          </h2>
          <div className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
            {/* Video embed - supports YouTube, Vimeo, or direct video URLs */}
            {manual.video_url.includes('youtube.com') || manual.video_url.includes('youtu.be') ? (
              <iframe
                src={manual.video_url.replace('watch?v=', 'embed/')}
                className="w-full h-full"
                allowFullScreen
                title={manual.title}
              />
            ) : manual.video_url.includes('vimeo.com') ? (
              <iframe
                src={manual.video_url.replace('vimeo.com/', 'player.vimeo.com/video/')}
                className="w-full h-full"
                allowFullScreen
                title={manual.title}
              />
            ) : (
              <video
                src={manual.video_url}
                controls
                className="w-full h-full"
              />
            )}
          </div>
        </div>
      )}

      {/* Text Instructions */}
      <div className="bg-white rounded-xl border border-gray-200 p-8 mb-6">
        <h2 className="text-xl font-semibold mb-6">
          {t('manuals.textInstructions')}
        </h2>
        <div className="prose prose-lg max-w-none">
          <ReactMarkdown>{manual.content}</ReactMarkdown>
        </div>
      </div>

      {/* Feedback */}
      <div className="bg-gradient-to-r from-primary-50 to-accent-50 rounded-xl border border-primary-100 p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4 text-center">
          {t('manuals.helpful')}
        </h3>
        {feedbackSubmitted ? (
          <div className="flex items-center justify-center gap-2 text-green-600">
            <CheckCircle size={24} />
            <span className="font-medium">{t('manuals.thankYou')}</span>
          </div>
        ) : (
          <div className="flex items-center justify-center gap-4">
            <button
              onClick={() => handleFeedback(true)}
              disabled={isSubmitting}
              className="flex items-center gap-2 px-6 py-3 bg-white border-2 border-green-500 text-green-600 rounded-lg hover:bg-green-50 transition-colors disabled:opacity-50"
            >
              <ThumbsUp size={20} />
              {t('manuals.yes')}
            </button>
            <button
              onClick={() => handleFeedback(false)}
              disabled={isSubmitting}
              className="flex items-center gap-2 px-6 py-3 bg-white border-2 border-red-500 text-red-600 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50"
            >
              <ThumbsDown size={20} />
              {t('manuals.no')}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ManualDetail;
