import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { authService } from '../services/auth.service';
import type { User, LoginRequest, RegisterRequest, UserSettings } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => void;
  isAdmin: () => boolean;
  updateUserSettings: (settings: UserSettings) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const { i18n } = useTranslation();

  useEffect(() => {
    const initAuth = async () => {
      if (authService.isAuthenticated()) {
        try {
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);

          // Set language from user settings
          const preferredLanguage = currentUser.settings?.preferred_language;
          if (preferredLanguage) {
            await i18n.changeLanguage(preferredLanguage);
          } else {
            // Fallback: localStorage > browser language > 'en'
            const savedLanguage = localStorage.getItem('language');
            const browserLanguage = navigator.language.split('-')[0];
            const fallbackLanguage = savedLanguage || (browserLanguage === 'es' ? 'es' : 'en');
            await i18n.changeLanguage(fallbackLanguage);
          }
        } catch (error) {
          authService.clearToken();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, [i18n]);

  const login = async (credentials: LoginRequest) => {
    const tokenResponse = await authService.login(credentials);
    authService.setToken(tokenResponse.access_token);
    const currentUser = await authService.getCurrentUser();
    setUser(currentUser);

    // Set language from user settings
    const preferredLanguage = currentUser.settings?.preferred_language;
    if (preferredLanguage) {
      await i18n.changeLanguage(preferredLanguage);
    }
  };

  const register = async (data: RegisterRequest) => {
    await authService.register(data);
    // Auto-login after registration
    await login({ username: data.username, password: data.password });
  };

  const logout = () => {
    authService.clearToken();
    setUser(null);
  };

  const isAdmin = (): boolean => {
    return user?.role === 'admin';
  };

  const updateUserSettings = (settings: UserSettings) => {
    if (user) {
      const updatedUser = { ...user, settings };
      setUser(updatedUser);
      // Update localStorage
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    register,
    logout,
    isAdmin,
    updateUserSettings,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
