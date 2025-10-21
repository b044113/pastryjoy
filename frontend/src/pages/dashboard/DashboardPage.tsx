import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../contexts/AuthContext';
import { Layout } from '../../components/layout/Layout';
import { Card } from '../../components/common/Card';

export const DashboardPage: React.FC = () => {
  const { t } = useTranslation();
  const { user, isAdmin } = useAuth();

  const adminCards = [
    {
      title: t('dashboard.cards.ingredients.title'),
      description: t('dashboard.cards.ingredients.description'),
      icon: '🥚',
      link: '/ingredients',
      color: 'bg-blue-50 border-blue-200',
    },
    {
      title: t('dashboard.cards.recipes.title'),
      description: t('dashboard.cards.recipes.description'),
      icon: '📖',
      link: '/recipes',
      color: 'bg-green-50 border-green-200',
    },
    {
      title: t('dashboard.cards.products.title'),
      description: t('dashboard.cards.products.description'),
      icon: '🎂',
      link: '/products',
      color: 'bg-purple-50 border-purple-200',
    },
  ];

  const userCards = [
    {
      title: t('dashboard.cards.orders.title'),
      description: t('dashboard.cards.orders.description'),
      icon: '📦',
      link: '/orders',
      color: 'bg-orange-50 border-orange-200',
    },
  ];

  const cards = isAdmin() ? [...adminCards, userCards[0]] : userCards;

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            {t('dashboard.welcomeBack', { name: user?.full_name || user?.username })}
          </h1>
          <p className="text-gray-600 mt-2">
            {isAdmin()
              ? t('dashboard.adminSubtitle')
              : t('dashboard.userSubtitle')}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cards.map((card) => (
            <Link key={card.link} to={card.link} className="transform transition-transform hover:scale-105">
              <div
                className={`${card.color} border-2 rounded-lg p-6 h-full hover:shadow-lg transition-shadow`}
              >
                <div className="text-5xl mb-4">{card.icon}</div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">{card.title}</h3>
                <p className="text-gray-600">{card.description}</p>
              </div>
            </Link>
          ))}
        </div>

        {/* Quick Stats */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">{t('dashboard.quickStats')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <div className="text-center">
                <p className="text-gray-600 text-sm uppercase tracking-wide">{t('dashboard.totalOrders')}</p>
                <p className="text-4xl font-bold text-primary-600 mt-2">-</p>
                <p className="text-gray-500 text-sm mt-1">{t('dashboard.comingSoon')}</p>
              </div>
            </Card>
            <Card>
              <div className="text-center">
                <p className="text-gray-600 text-sm uppercase tracking-wide">{t('dashboard.activeProducts')}</p>
                <p className="text-4xl font-bold text-green-600 mt-2">-</p>
                <p className="text-gray-500 text-sm mt-1">{t('dashboard.comingSoon')}</p>
              </div>
            </Card>
            <Card>
              <div className="text-center">
                <p className="text-gray-600 text-sm uppercase tracking-wide">{t('dashboard.revenue')}</p>
                <p className="text-4xl font-bold text-purple-600 mt-2">-</p>
                <p className="text-gray-500 text-sm mt-1">{t('dashboard.comingSoon')}</p>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </Layout>
  );
};
