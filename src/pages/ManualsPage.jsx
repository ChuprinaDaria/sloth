import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams, useNavigate } from 'react-router-dom';
import { Search, Filter, BookOpen } from 'lucide-react';
import ManualCard from '../components/manuals/ManualCard';
import ManualDetail from '../components/manuals/ManualDetail';
import { manualsAPI } from '../api/manuals';

const ManualsPage = () => {
  const { t, i18n } = useTranslation();
  const { manualId } = useParams();
  const navigate = useNavigate();

  const [manuals, setManuals] = useState([]);
  const [featuredManuals, setFeaturedManuals] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedManual, setSelectedManual] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedIntegration, setSelectedIntegration] = useState('all');

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [manualsRes, categoriesRes, featuredRes] = await Promise.all([
          manualsAPI.getManuals({ language: i18n.language }),
          manualsAPI.getCategories(),
          manualsAPI.getFeaturedManuals(i18n.language),
        ]);

        setManuals(manualsRes.data.results || manualsRes.data || []);
        setCategories(categoriesRes.data.results || categoriesRes.data || []);
        setFeaturedManuals(featuredRes.data || []);
      } catch (error) {
        console.error('Failed to fetch manuals:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [i18n.language]);

  // Fetch specific manual if manualId is provided
  useEffect(() => {
    if (manualId) {
      const fetchManual = async () => {
        try {
          const response = await manualsAPI.getManual(manualId);
          setSelectedManual(response.data);
        } catch (error) {
          console.error('Failed to fetch manual:', error);
          navigate('/manuals');
        }
      };
      fetchManual();
    } else {
      setSelectedManual(null);
    }
  }, [manualId, navigate]);

  // Filter manuals
  const filteredManuals = manuals.filter((manual) => {
    const matchesSearch =
      searchQuery === '' ||
      manual.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      manual.description.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesCategory =
      selectedCategory === 'all' || manual.category?.slug === selectedCategory;

    const matchesIntegration =
      selectedIntegration === 'all' || manual.integration_type === selectedIntegration;

    return matchesSearch && matchesCategory && matchesIntegration;
  });

  // Integration types for filter
  const integrationTypes = [
    { value: 'all', label: t('manuals.allCategories') },
    { value: 'general', label: t('manuals.category.general') },
    { value: 'telegram', label: t('manuals.category.telegram') },
    { value: 'whatsapp', label: t('manuals.category.whatsapp') },
    { value: 'instagram', label: t('manuals.category.instagram') },
    { value: 'calendar', label: t('manuals.category.calendar') },
    { value: 'sheets', label: t('manuals.category.sheets') },
  ];

  // If viewing a specific manual
  if (selectedManual) {
    return (
      <div className="space-y-6">
        <ManualDetail manual={selectedManual} />
      </div>
    );
  }

  // List view
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-3">
          <BookOpen className="text-primary-500" size={32} />
          {t('manuals.title')}
        </h1>
        <p className="text-gray-600 mt-1">{t('manuals.subtitle')}</p>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div className="relative md:col-span-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder={t('manuals.searchPlaceholder')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input pl-10"
            />
          </div>

          {/* Integration Filter */}
          <div>
            <select
              value={selectedIntegration}
              onChange={(e) => setSelectedIntegration(e.target.value)}
              className="input"
            >
              {integrationTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          {/* Category Filter */}
          {categories.length > 0 && (
            <div>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="input"
              >
                <option value="all">{t('manuals.allCategories')}</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.slug}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Featured Manuals */}
      {featuredManuals.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-4">{t('manuals.featured')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredManuals.map((manual) => (
              <ManualCard key={manual.id} manual={manual} />
            ))}
          </div>
        </div>
      )}

      {/* All Manuals */}
      <div>
        <h2 className="text-xl font-semibold mb-4">
          {searchQuery || selectedCategory !== 'all' || selectedIntegration !== 'all'
            ? t('common.search') + ' ' + t('common.results')
            : t('manuals.allCategories')}
        </h2>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
          </div>
        ) : filteredManuals.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
            <BookOpen className="mx-auto text-gray-400 mb-4" size={48} />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {t('manuals.noResults')}
            </h3>
            <p className="text-gray-600">{t('manuals.tryDifferentSearch')}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredManuals.map((manual) => (
              <ManualCard key={manual.id} manual={manual} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ManualsPage;
