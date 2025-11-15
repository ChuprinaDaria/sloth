import { useTranslation } from 'react-i18next';
import { Clock, Eye, Video, FileText } from 'lucide-react';
import { Link } from 'react-router-dom';

const ManualCard = ({ manual }) => {
  const { t } = useTranslation();

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

  // Calculate estimated read time (assuming 200 words per minute)
  const estimateReadTime = (content) => {
    const words = content.split(/\s+/).length;
    const minutes = Math.ceil(words / 200);
    return minutes;
  };

  const readTime = estimateReadTime(manual.content || '');

  return (
    <Link
      to={`/manuals/${manual.id}`}
      className="block bg-white rounded-xl border border-gray-200 hover:shadow-lg transition-shadow duration-300 overflow-hidden group"
    >
      {/* Video Thumbnail or Placeholder */}
      <div className="relative h-48 bg-gradient-to-br from-primary-100 to-accent-100 overflow-hidden">
        {manual.video_thumbnail ? (
          <img
            src={manual.video_thumbnail}
            alt={manual.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="flex items-center justify-center h-full">
            <FileText size={64} className="text-primary-300" />
          </div>
        )}
        {manual.video_url && (
          <div className="absolute top-3 right-3 bg-black bg-opacity-70 text-white px-3 py-1 rounded-full flex items-center gap-1 text-sm">
            <Video size={16} />
            {t('manuals.videoTutorial')}
          </div>
        )}
      </div>

      {/* Card Content */}
      <div className="p-5">
        {/* Category Badge */}
        <div className="mb-3">
          <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getCategoryColor(manual.integration_type)}`}>
            {t(`manuals.category.${manual.integration_type}`)}
          </span>
        </div>

        {/* Title */}
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-primary-600 transition-colors">
          {manual.title}
        </h3>

        {/* Description */}
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">
          {manual.description}
        </p>

        {/* Meta Info */}
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <Clock size={16} />
              <span>{t('manuals.readTime', { minutes: readTime })}</span>
            </div>
            <div className="flex items-center gap-1">
              <Eye size={16} />
              <span>{manual.views_count || 0}</span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default ManualCard;
