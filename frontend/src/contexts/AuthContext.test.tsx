import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from './AuthContext';
import { authService } from '../services/auth.service';

// Mock the auth service
vi.mock('../services/auth.service', () => ({
  authService: {
    isAuthenticated: vi.fn(),
    getCurrentUser: vi.fn(),
    clearToken: vi.fn(),
    login: vi.fn(),
    setToken: vi.fn(),
    register: vi.fn(),
  },
}));

// Test component that uses the auth context
const TestComponent = () => {
  const { user, loading, login, register, logout, isAdmin } = useAuth();

  return (
    <div>
      <div data-testid="loading">{loading ? 'loading' : 'loaded'}</div>
      <div data-testid="user">{user ? user.username : 'no user'}</div>
      <div data-testid="is-admin">{isAdmin() ? 'admin' : 'not admin'}</div>
      <button onClick={() => login({ username: 'test', password: 'pass' })}>Login</button>
      <button onClick={() => register({ username: 'new', password: 'pass', email: 'test@test.com' })}>Register</button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('useAuth hook', () => {
    it('throws error when used outside AuthProvider', () => {
      // Suppress console.error for this test
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => render(<TestComponent />)).toThrow('useAuth must be used within AuthProvider');

      consoleError.mockRestore();
    });
  });

  describe('AuthProvider', () => {
    it('initializes with no user when not authenticated', async () => {
      vi.mocked(authService.isAuthenticated).mockReturnValue(false);

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
      });

      expect(screen.getByTestId('user')).toHaveTextContent('no user');
      expect(screen.getByTestId('is-admin')).toHaveTextContent('not admin');
    });

    it('loads current user when authenticated', async () => {
      const mockUser = {
        id: '1',
        username: 'testuser',
        email: 'test@example.com',
        role: 'user' as const,
      };

      vi.mocked(authService.isAuthenticated).mockReturnValue(true);
      vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('testuser');
      });

      expect(screen.getByTestId('is-admin')).toHaveTextContent('not admin');
    });

    it('loads admin user correctly', async () => {
      const mockAdmin = {
        id: '1',
        username: 'admin',
        email: 'admin@example.com',
        role: 'admin' as const,
      };

      vi.mocked(authService.isAuthenticated).mockReturnValue(true);
      vi.mocked(authService.getCurrentUser).mockResolvedValue(mockAdmin);

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('admin');
      });

      expect(screen.getByTestId('is-admin')).toHaveTextContent('admin');
    });

    it('clears token when getCurrentUser fails', async () => {
      vi.mocked(authService.isAuthenticated).mockReturnValue(true);
      vi.mocked(authService.getCurrentUser).mockRejectedValue(new Error('Unauthorized'));

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
      });

      expect(authService.clearToken).toHaveBeenCalled();
      expect(screen.getByTestId('user')).toHaveTextContent('no user');
    });

    it('handles login successfully', async () => {
      const mockTokenResponse = { access_token: 'test-token', token_type: 'bearer' };
      const mockUser = {
        id: '1',
        username: 'testuser',
        email: 'test@example.com',
        role: 'user' as const,
      };

      vi.mocked(authService.isAuthenticated).mockReturnValue(false);
      vi.mocked(authService.login).mockResolvedValue(mockTokenResponse);
      vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
      });

      const loginButton = screen.getByText('Login');
      loginButton.click();

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('testuser');
      });

      expect(authService.setToken).toHaveBeenCalledWith('test-token');
    });

    it('handles registration and auto-login', async () => {
      const mockTokenResponse = { access_token: 'test-token', token_type: 'bearer' };
      const mockUser = {
        id: '2',
        username: 'newuser',
        email: 'new@example.com',
        role: 'user' as const,
      };

      vi.mocked(authService.isAuthenticated).mockReturnValue(false);
      vi.mocked(authService.register).mockResolvedValue(mockUser);
      vi.mocked(authService.login).mockResolvedValue(mockTokenResponse);
      vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('loaded');
      });

      const registerButton = screen.getByText('Register');
      registerButton.click();

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('newuser');
      });

      expect(authService.register).toHaveBeenCalled();
      expect(authService.login).toHaveBeenCalled();
    });

    it('handles logout', async () => {
      const mockUser = {
        id: '1',
        username: 'testuser',
        email: 'test@example.com',
        role: 'user' as const,
      };

      vi.mocked(authService.isAuthenticated).mockReturnValue(true);
      vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('testuser');
      });

      const logoutButton = screen.getByText('Logout');
      logoutButton.click();

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('no user');
      });

      expect(authService.clearToken).toHaveBeenCalled();
    });
  });
});
