import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import {
  Bot, Zap, BarChart3, Users, Calendar,
  MessageSquare, CheckCircle, Star, ArrowRight,
  Globe, Menu, X
} from 'lucide-react';
import { useState } from 'react';

const LandingPage = () => {
  const { t, i18n } = useTranslation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  const features = [
    {
      icon: Zap,
      title: t('landing.features.automation.title'),
      description: t('landing.features.automation.description'),
      color: 'text-yellow-500'
    },
    {
      icon: BarChart3,
      title: t('landing.features.analytics.title'),
      description: t('landing.features.analytics.description'),
      color: 'text-blue-500'
    },
    {
      icon: MessageSquare,
      title: t('landing.features.messaging.title'),
      description: t('landing.features.messaging.description'),
      color: 'text-green-500'
    },
    {
      icon: Users,
      title: t('landing.features.clients.title'),
      description: t('landing.features.clients.description'),
      color: 'text-purple-500'
    },
  ];

  const plans = [
    {
      id: 'starter',
      name: t('pricing.starter'),
      price: '29',
      description: t('pricing.starterDesc'),
      features: [
        t('landing.plans.starter.feature1'),
        t('landing.plans.starter.feature2'),
        t('landing.plans.starter.feature3'),
        t('landing.plans.starter.feature4'),
        t('landing.plans.starter.feature5'),
      ],
      popular: false,
    },
    {
      id: 'professional',
      name: t('pricing.professional'),
      price: '79',
      description: t('pricing.professionalDesc'),
      features: [
        t('landing.plans.professional.feature1'),
        t('landing.plans.professional.feature2'),
        t('landing.plans.professional.feature3'),
        t('landing.plans.professional.feature4'),
        t('landing.plans.professional.feature5'),
        t('landing.plans.professional.feature6'),
      ],
      popular: true,
    },
    {
      id: 'enterprise',
      name: t('pricing.enterprise'),
      price: '199',
      description: t('pricing.enterpriseDesc'),
      features: [
        t('landing.plans.enterprise.feature1'),
        t('landing.plans.enterprise.feature2'),
        t('landing.plans.enterprise.feature3'),
        t('landing.plans.enterprise.feature4'),
        t('landing.plans.enterprise.feature5'),
        t('landing.plans.enterprise.feature6'),
      ],
      popular: false,
    },
  ];

  const testimonials = [
    {
      name: t('landing.testimonials.testimonial1.name'),
      role: t('landing.testimonials.testimonial1.role'),
      text: t('landing.testimonials.testimonial1.text'),
      rating: 5,
    },
    {
      name: t('landing.testimonials.testimonial2.name'),
      role: t('landing.testimonials.testimonial2.role'),
      text: t('landing.testimonials.testimonial2.text'),
      rating: 5,
    },
    {
      name: t('landing.testimonials.testimonial3.name'),
      role: t('landing.testimonials.testimonial3.role'),
      text: t('landing.testimonials.testimonial3.text'),
      rating: 5,
    },
  ];

  const languages = [
    { code: 'uk', label: 'Українська', flag: '🇺🇦' },
    { code: 'en', label: 'English', flag: '🇬🇧' },
    { code: 'pl', label: 'Polski', flag: '🇵🇱' },
    { code: 'de', label: 'Deutsch', flag: '🇩🇪' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-pink-400 rounded-full flex items-center justify-center">
                <Bot className="text-white" size={24} />
              </div>
              <div>
                <div className="font-bold text-xl text-gray-900">Sloth AI</div>
                <div className="text-xs text-gray-500">by Lazysoft</div>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-gray-700 hover:text-primary-500 transition-colors">
                {t('landing.nav.features')}
              </a>
              <a href="#pricing" className="text-gray-700 hover:text-primary-500 transition-colors">
                {t('landing.nav.pricing')}
              </a>
              <a href="#testimonials" className="text-gray-700 hover:text-primary-500 transition-colors">
                {t('landing.nav.testimonials')}
              </a>

              {/* Language Selector */}
              <div className="relative group">
                <button className="flex items-center gap-2 text-gray-700 hover:text-primary-500 transition-colors">
                  <Globe size={18} />
                  <span className="text-sm">
                    {languages.find(l => l.code === i18n.language)?.flag || '🌐'}
                  </span>
                </button>
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                  {languages.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => changeLanguage(lang.code)}
                      className={`w-full text-left px-4 py-2 hover:bg-gray-50 first:rounded-t-lg last:rounded-b-lg flex items-center gap-2 ${
                        i18n.language === lang.code ? 'bg-green-50 text-primary-500' : 'text-gray-700'
                      }`}
                    >
                      <span>{lang.flag}</span>
                      <span>{lang.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              <Link to="/login" className="text-gray-700 hover:text-primary-500 transition-colors">
                {t('landing.nav.login')}
              </Link>
              <Link to="/register" className="btn-primary">
                {t('landing.nav.signUp')}
              </Link>
            </div>

            {/* Mobile menu button */}
            <button
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>

          {/* Mobile Navigation */}
          {mobileMenuOpen && (
            <div className="md:hidden py-4 space-y-4">
              <a href="#features" className="block text-gray-700 hover:text-primary-500">
                {t('landing.nav.features')}
              </a>
              <a href="#pricing" className="block text-gray-700 hover:text-primary-500">
                {t('landing.nav.pricing')}
              </a>
              <a href="#testimonials" className="block text-gray-700 hover:text-primary-500">
                {t('landing.nav.testimonials')}
              </a>
              <div className="border-t pt-4">
                {languages.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => changeLanguage(lang.code)}
                    className="block w-full text-left py-2 text-gray-700"
                  >
                    {lang.flag} {lang.label}
                  </button>
                ))}
              </div>
              <Link to="/login" className="block text-gray-700">
                {t('landing.nav.login')}
              </Link>
              <Link to="/register" className="block btn-primary text-center">
                {t('landing.nav.signUp')}
              </Link>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="space-y-8">
              <div className="space-y-4">
                <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 leading-tight">
                  {t('landing.hero.title')}
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-500 to-pink-500">
                    {' '}{t('landing.hero.titleHighlight')}
                  </span>
                </h1>
                <p className="text-xl text-gray-600 leading-relaxed">
                  {t('landing.hero.subtitle')}
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/register" className="btn-primary text-lg px-8 py-4 inline-flex items-center justify-center gap-2">
                  {t('landing.hero.cta.trial')}
                  <ArrowRight size={20} />
                </Link>
                <a href="#features" className="btn-secondary text-lg px-8 py-4 inline-flex items-center justify-center">
                  {t('landing.hero.cta.learnMore')}
                </a>
              </div>

              <p className="text-sm text-gray-500">
                {t('landing.hero.trialNotice')}
              </p>
            </div>

            {/* Right Image/Animation */}
            <div className="relative">
              <div className="relative z-10">
                <div className="bg-gradient-to-br from-green-100 to-pink-100 rounded-3xl p-8 shadow-2xl">
                  <div className="bg-white rounded-2xl p-6 shadow-lg">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-pink-400 rounded-full flex items-center justify-center animate-pulse">
                        <Bot className="text-white" size={28} />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900">Sloth AI</div>
                        <div className="text-sm text-green-500">{t('landing.hero.status')}</div>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div className="bg-gray-50 rounded-lg p-4">
                        <div className="text-sm text-gray-600 mb-2">{t('landing.hero.chatExample.user')}</div>
                        <div className="bg-white rounded p-3 text-sm">{t('landing.hero.chatExample.userMessage')}</div>
                      </div>
                      <div className="bg-green-50 rounded-lg p-4">
                        <div className="text-sm text-gray-600 mb-2">{t('landing.hero.chatExample.ai')}</div>
                        <div className="bg-white rounded p-3 text-sm">{t('landing.hero.chatExample.aiMessage')}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              {/* Decorative elements */}
              <div className="absolute -top-4 -right-4 w-72 h-72 bg-green-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
              <div className="absolute -bottom-8 -left-4 w-72 h-72 bg-pink-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-5xl font-bold text-gray-900 mb-4">
              {t('landing.features.title')}
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              {t('landing.features.subtitle')}
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="group hover:scale-105 transition-transform duration-300">
                <div className="bg-gradient-to-br from-gray-50 to-white rounded-2xl p-6 h-full border border-gray-100 shadow-lg hover:shadow-xl transition-shadow">
                  <div className={`${feature.color} mb-4`}>
                    <feature.icon size={40} strokeWidth={1.5} />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">
                    {feature.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-gradient-to-b from-white to-green-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-5xl font-bold text-gray-900 mb-4">
              {t('landing.pricing.title')}
            </h2>
            <p className="text-xl text-gray-600">
              {t('landing.pricing.subtitle')}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {plans.map((plan) => (
              <div
                key={plan.id}
                className={`relative rounded-2xl p-8 ${
                  plan.popular
                    ? 'bg-gradient-to-br from-green-500 to-pink-500 text-white shadow-2xl scale-105'
                    : 'bg-white border-2 border-gray-200'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-yellow-400 text-gray-900 px-4 py-1 rounded-full text-sm font-bold">
                      {t('pricing.mostPopular')}
                    </span>
                  </div>
                )}

                <div className="text-center mb-8">
                  <h3 className={`text-2xl font-bold mb-2 ${plan.popular ? 'text-white' : 'text-gray-900'}`}>
                    {plan.name}
                  </h3>
                  <p className={`text-sm mb-4 ${plan.popular ? 'text-green-100' : 'text-gray-600'}`}>
                    {plan.description}
                  </p>
                  <div className="flex items-baseline justify-center gap-2">
                    <span className={`text-5xl font-bold ${plan.popular ? 'text-white' : 'text-gray-900'}`}>
                      ${plan.price}
                    </span>
                    <span className={plan.popular ? 'text-green-100' : 'text-gray-500'}>
                      /{t('pricing.month')}
                    </span>
                  </div>
                </div>

                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <CheckCircle
                        className={`flex-shrink-0 ${plan.popular ? 'text-white' : 'text-green-500'}`}
                        size={20}
                      />
                      <span className={plan.popular ? 'text-white' : 'text-gray-700'}>
                        {feature}
                      </span>
                    </li>
                  ))}
                </ul>

                <Link
                  to="/register"
                  className={`block w-full py-4 rounded-lg font-semibold text-center transition-colors ${
                    plan.popular
                      ? 'bg-white text-green-600 hover:bg-green-50'
                      : 'bg-gradient-to-r from-green-500 to-pink-500 text-white hover:from-green-600 hover:to-pink-600'
                  }`}
                >
                  {t('landing.pricing.cta')}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-5xl font-bold text-gray-900 mb-4">
              {t('landing.testimonials.title')}
            </h2>
            <p className="text-xl text-gray-600">
              {t('landing.testimonials.subtitle')}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-gradient-to-br from-gray-50 to-white rounded-2xl p-8 border border-gray-100 shadow-lg">
                <div className="flex gap-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="text-yellow-400 fill-current" size={20} />
                  ))}
                </div>
                <p className="text-gray-700 mb-6 italic">
                  "{testimonial.text}"
                </p>
                <div>
                  <div className="font-semibold text-gray-900">{testimonial.name}</div>
                  <div className="text-sm text-gray-600">{testimonial.role}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-green-500 to-pink-500">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl lg:text-5xl font-bold text-white mb-6">
            {t('landing.cta.title')}
          </h2>
          <p className="text-xl text-green-100 mb-8">
            {t('landing.cta.subtitle')}
          </p>
          <Link to="/register" className="inline-flex items-center gap-2 bg-white text-green-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-green-50 transition-colors">
            {t('landing.cta.button')}
            <ArrowRight size={20} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            {/* Logo & Description */}
            <div className="md:col-span-2">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-pink-400 rounded-full flex items-center justify-center">
                  <Bot className="text-white" size={24} />
                </div>
                <div>
                  <div className="font-bold text-xl text-white">Sloth AI</div>
                  <div className="text-xs text-gray-400">by Lazysoft</div>
                </div>
              </div>
              <p className="text-gray-400 max-w-md">
                {t('landing.footer.description')}
              </p>
            </div>

            {/* Links */}
            <div>
              <h4 className="font-semibold text-white mb-4">{t('landing.footer.product')}</h4>
              <ul className="space-y-2">
                <li><a href="#features" className="hover:text-white transition-colors">{t('landing.nav.features')}</a></li>
                <li><a href="#pricing" className="hover:text-white transition-colors">{t('landing.nav.pricing')}</a></li>
                <li><Link to="/register" className="hover:text-white transition-colors">{t('landing.nav.signUp')}</Link></li>
                <li><Link to="/login" className="hover:text-white transition-colors">{t('landing.nav.login')}</Link></li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h4 className="font-semibold text-white mb-4">{t('landing.footer.company')}</h4>
              <ul className="space-y-2">
                <li><a href="https://lazysoft.pl" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Lazysoft.pl</a></li>
                <li><a href="#" className="hover:text-white transition-colors">{t('landing.footer.privacy')}</a></li>
                <li><a href="#" className="hover:text-white transition-colors">{t('landing.footer.terms')}</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Sloth AI by Lazysoft. {t('landing.footer.rights')}</p>
          </div>
        </div>
      </footer>

      <style jsx>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
      `}</style>
    </div>
  );
};

export default LandingPage;
