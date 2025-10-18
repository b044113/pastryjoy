import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../common/Button';

export const Navbar: React.FC = () => {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

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
                Dashboard
              </Link>

              {isAdmin() && (
                <>
                  <Link
                    to="/ingredients"
                    className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
                  >
                    Ingredients
                  </Link>
                  <Link
                    to="/recipes"
                    className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
                  >
                    Recipes
                  </Link>
                  <Link
                    to="/products"
                    className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
                  >
                    Products
                  </Link>
                </>
              )}

              <Link
                to="/orders"
                className="text-gray-700 hover:text-primary-600 font-medium transition-colors"
              >
                Orders
              </Link>

              {/* User Menu */}
              <div className="flex items-center gap-3 pl-6 border-l border-gray-200">
                <div className="text-sm">
                  <p className="font-medium text-gray-900">{user.username}</p>
                  <p className="text-gray-500 text-xs capitalize">{user.role}</p>
                </div>
                <Button onClick={handleLogout} variant="secondary" size="sm">
                  Logout
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};
