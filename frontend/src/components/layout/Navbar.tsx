import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import { UserMenu } from './UserMenu';

export const Navbar: React.FC = () => {
  const { user, isAdmin } = useAuth();
  const { t } = useTranslation();

  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <span className="text-2xl">🥐</span>
            <span className="text-xl font-bold text-primary-600">PastryJoy</span>
          </Link>

          {/* Navigation Links */}
          {user && (
            <div className="flex items-center gap-6">
              <Link
                to="/dashboard"
                className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
              >
                {t('nav.dashboard')}
              </Link>

              {isAdmin() && (
                <>
                  <Link
                    to="/ingredients"
                    className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
                  >
                    {t('nav.ingredients')}
                  </Link>
                  <Link
                    to="/recipes"
                    className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
                  >
                    {t('nav.recipes')}
                  </Link>
                  <Link
                    to="/products"
                    className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
                  >
                    {t('nav.products')}
                  </Link>
                </>
              )}

              <Link
                to="/orders"
                className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
              >
                {t('nav.orders')}
              </Link>

              {/* User Menu */}
              <UserMenu />
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};
