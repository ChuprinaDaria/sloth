import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useTranslation } from 'react-i18next';

const LoginForm = () => {
  const { register, handleSubmit, formState: { errors } } = useForm();
  const { login } = useAuth();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const onSubmit = async (data) => {
    setLoading(true);
    setError('');
    try {
      await login(data.email, data.password);
      navigate('/dashboard');
    } catch (err) {
      // Бекенд повертає помилки у форматі { non_field_errors: [...] } або { field: [...] }
      const errorData = err.response?.data;
      let errorMessage = t('auth.loginFailed');
      
      if (errorData) {
        if (errorData.non_field_errors && errorData.non_field_errors.length > 0) {
          const backendError = errorData.non_field_errors[0];
          // Перекладаємо стандартні помилки бекенду
          if (backendError === 'Invalid email or password' || backendError.includes('Invalid email or password')) {
            errorMessage = t('auth.invalidEmailOrPassword');
          } else if (backendError === 'User account is disabled' || backendError.includes('disabled')) {
            errorMessage = t('auth.accountDisabled', 'Обліковий запис деактивовано');
          } else {
            errorMessage = backendError;
          }
        } else if (errorData.message) {
          errorMessage = errorData.message;
        } else if (errorData.email && errorData.email.length > 0) {
          errorMessage = errorData.email[0];
        } else if (errorData.password && errorData.password.length > 0) {
          errorMessage = errorData.password[0];
        }
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md">
      <div className="card">
        <h2 className="text-2xl font-bold text-center mb-6">{t('auth.welcomeBack')}</h2>

        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">{t('auth.email')}</label>
            <input
              type="email"
              className="input"
              {...register('email', { required: t('auth.emailRequired') })}
            />
            {errors.email && (
              <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">{t('auth.password')}</label>
            <input
              type="password"
              className="input"
              {...register('password', { required: t('auth.passwordRequired') })}
            />
            {errors.password && (
              <p className="text-red-500 text-sm mt-1">{errors.password.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary"
          >
            {loading ? t('auth.loggingIn') : t('auth.loginButton')}
          </button>
        </form>

        <div className="mt-6 text-center text-sm">
          <Link to="/forgot-password" className="text-primary-500 hover:underline">
            {t('auth.forgotPassword')}
          </Link>
          <span className="mx-2">|</span>
          <Link to="/register" className="text-primary-500 hover:underline">
            {t('auth.noAccount')}
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
