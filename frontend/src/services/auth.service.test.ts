import { describe, it, expect, vi, beforeEach } from 'vitest';
import { authService } from './auth.service';
import { apiClient } from './api';

// Mock the API client
vi.mock('./api', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

describe('authService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('login', () => {
    it('calls API with credentials and returns token response', async () => {
      const mockResponse = {
        data: {
          access_token: 'test-token',
          token_type: 'bearer',
        },
      };

      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const credentials = { username: 'testuser', password: 'password123' };
      const result = await authService.login(credentials);

      expect(apiClient.post).toHaveBeenCalledWith('/api/auth/login', credentials);
      expect(result).toEqual(mockResponse.data);
    });

    it('throws error when login fails', async () => {
      vi.mocked(apiClient.post).mockRejectedValue(new Error('Login failed'));

      const credentials = { username: 'testuser', password: 'wrong' };

      await expect(authService.login(credentials)).rejects.toThrow('Login failed');
    });
  });

  describe('register', () => {
    it('calls API with registration data and returns user', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        username: 'testuser',
        role: 'user',
      };

      const mockResponse = { data: mockUser };
      vi.mocked(apiClient.post).mockResolvedValue(mockResponse);

      const registerData = {
        email: 'test@example.com',
        username: 'testuser',
        password: 'password123',
        full_name: 'Test User',
      };

      const result = await authService.register(registerData);

      expect(apiClient.post).toHaveBeenCalledWith('/api/auth/register', registerData);
      expect(result).toEqual(mockUser);
    });

    it('throws error when registration fails', async () => {
      vi.mocked(apiClient.post).mockRejectedValue(new Error('Registration failed'));

      const registerData = {
        email: 'test@example.com',
        username: 'testuser',
        password: 'password123',
      };

      await expect(authService.register(registerData)).rejects.toThrow('Registration failed');
    });
  });

  describe('getCurrentUser', () => {
    it('calls API and returns current user', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        username: 'testuser',
        role: 'user',
      };

      const mockResponse = { data: mockUser };
      vi.mocked(apiClient.get).mockResolvedValue(mockResponse);

      const result = await authService.getCurrentUser();

      expect(apiClient.get).toHaveBeenCalledWith('/api/auth/me');
      expect(result).toEqual(mockUser);
    });

    it('throws error when getting user fails', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Unauthorized'));

      await expect(authService.getCurrentUser()).rejects.toThrow('Unauthorized');
    });
  });

  describe('setToken', () => {
    it('stores token in localStorage', () => {
      authService.setToken('my-token');
      expect(localStorage.getItem('token')).toBe('my-token');
    });

    it('overwrites existing token', () => {
      localStorage.setItem('token', 'old-token');
      authService.setToken('new-token');
      expect(localStorage.getItem('token')).toBe('new-token');
    });
  });

  describe('getToken', () => {
    it('retrieves token from localStorage', () => {
      localStorage.setItem('token', 'stored-token');
      expect(authService.getToken()).toBe('stored-token');
    });

    it('returns null when no token exists', () => {
      expect(authService.getToken()).toBeNull();
    });
  });

  describe('clearToken', () => {
    it('removes token from localStorage', () => {
      localStorage.setItem('token', 'token-to-remove');
      authService.clearToken();
      expect(localStorage.getItem('token')).toBeNull();
    });

    it('does nothing when no token exists', () => {
      authService.clearToken();
      expect(localStorage.getItem('token')).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('returns true when token exists', () => {
      localStorage.setItem('token', 'valid-token');
      expect(authService.isAuthenticated()).toBe(true);
    });

    it('returns false when token does not exist', () => {
      expect(authService.isAuthenticated()).toBe(false);
    });

    it('returns false when token is empty string', () => {
      localStorage.setItem('token', '');
      expect(authService.isAuthenticated()).toBe(false);
    });
  });
});
