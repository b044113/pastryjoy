import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import { useAuth } from '../../contexts/AuthContext';
import { userService } from '../../services/user.service';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const { t, i18n } = useTranslation();
  const { user, updateUserSettings } = useAuth();
  const [selectedLanguage, setSelectedLanguage] = useState<'en' | 'es'>(
    user?.settings?.preferred_language || 'en'
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSave = async () => {
    if (!user) return;

    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      const response = await userService.updateSettings({
        preferred_language: selectedLanguage,
      });

      // Update AuthContext with new settings
      updateUserSettings(response.data);

      // Change i18n language
      await i18n.changeLanguage(selectedLanguage);

      // Show success message
      setSuccess(true);

      // Close modal after a short delay
      setTimeout(() => {
        onClose();
        setSuccess(false);
      }, 1000);
    } catch (err: any) {
      setError(err.response?.data?.detail || t('settings.saveFailed'));
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    // Reset to current user language
    setSelectedLanguage(user?.settings?.preferred_language || 'en');
    setError('');
    setSuccess(false);
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleCancel}
      title={t('settings.title')}
      size="md"
      footer={
        <>
          <Button variant="outline" onClick={handleCancel} disabled={loading}>
            {t('settings.cancel')}
          </Button>
          <Button onClick={handleSave} disabled={loading}>
            {loading ? t('common.loading') : t('settings.save')}
          </Button>
        </>
      }
    >
      <div className="space-y-6">
        {/* General Tab */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {t('settings.general')}
          </h3>

          {/* Language Setting */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              {t('settings.language')}
            </label>
            <p className="text-sm text-gray-500 mb-3">
              {t('settings.languageDescription')}
            </p>

            <div className="flex gap-3">
              <button
                onClick={() => setSelectedLanguage('en')}
                disabled={loading}
                className={`flex-1 px-4 py-3 rounded-lg border-2 text-sm font-medium transition-all ${
                  selectedLanguage === 'en'
                    ? 'border-primary-600 bg-primary-50 text-primary-700'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                } ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <div className="flex items-center justify-center gap-2">
                  <span className="text-2xl">🇺🇸</span>
                  <span>English</span>
                  {selectedLanguage === 'en' && (
                    <svg
                      className="w-5 h-5 text-primary-600"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </div>
              </button>

              <button
                onClick={() => setSelectedLanguage('es')}
                disabled={loading}
                className={`flex-1 px-4 py-3 rounded-lg border-2 text-sm font-medium transition-all ${
                  selectedLanguage === 'es'
                    ? 'border-primary-600 bg-primary-50 text-primary-700'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                } ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <div className="flex items-center justify-center gap-2">
                  <span className="text-2xl">🇪🇸</span>
                  <span>Español</span>
                  {selectedLanguage === 'es' && (
                    <svg
                      className="w-5 h-5 text-primary-600"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Success Message */}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            {t('settings.saved')}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}
      </div>
    </Modal>
  );
};
