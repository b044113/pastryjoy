import { describe, it, expect, vi, beforeEach } from 'vitest';
import { userService } from './user.service';
import { apiClient } from './api';

// Mock the API client
vi.mock('./api', () => ({
  apiClient: {
    get: vi.fn(),
    patch: vi.fn(),
  },
}));

describe('userService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getSettings', () => {
    it('calls correct endpoint', async () => {
      const mockSettings = {
        data: {
          preferred_language: 'en',
        },
      };

      vi.mocked(apiClient.get).mockResolvedValue(mockSettings);

      const result = await userService.getSettings();

      expect(apiClient.get).toHaveBeenCalledWith('/api/users/me/settings');
      expect(result).toEqual(mockSettings);
    });

    it('throws error when API call fails', async () => {
      const error = new Error('Failed to fetch settings');
      vi.mocked(apiClient.get).mockRejectedValue(error);

      await expect(userService.getSettings()).rejects.toThrow('Failed to fetch settings');
    });

    it('returns settings with preferred_language', async () => {
      const mockSettings = {
        data: {
          preferred_language: 'es',
        },
      };

      vi.mocked(apiClient.get).mockResolvedValue(mockSettings);

      const result = await userService.getSettings();

      expect(result.data.preferred_language).toBe('es');
    });
  });

  describe('updateSettings', () => {
    it('calls correct endpoint with data', async () => {
      const mockResponse = {
        data: {
          preferred_language: 'es',
        },
      };

      vi.mocked(apiClient.patch).mockResolvedValue(mockResponse);

      const settings = { preferred_language: 'es' as const };
      const result = await userService.updateSettings(settings);

      expect(apiClient.patch).toHaveBeenCalledWith('/api/users/me/settings', settings);
      expect(result).toEqual(mockResponse);
    });

    it('updates language to English', async () => {
      const mockResponse = {
        data: {
          preferred_language: 'en',
        },
      };

      vi.mocked(apiClient.patch).mockResolvedValue(mockResponse);

      const settings = { preferred_language: 'en' as const };
      const result = await userService.updateSettings(settings);

      expect(result.data.preferred_language).toBe('en');
    });

    it('updates language to Spanish', async () => {
      const mockResponse = {
        data: {
          preferred_language: 'es',
        },
      };

      vi.mocked(apiClient.patch).mockResolvedValue(mockResponse);

      const settings = { preferred_language: 'es' as const };
      const result = await userService.updateSettings(settings);

      expect(result.data.preferred_language).toBe('es');
    });

    it('throws error when API call fails', async () => {
      const error = new Error('Failed to update settings');
      vi.mocked(apiClient.patch).mockRejectedValue(error);

      const settings = { preferred_language: 'es' as const };

      await expect(userService.updateSettings(settings)).rejects.toThrow(
        'Failed to update settings'
      );
    });

    it('handles 400 validation error', async () => {
      const error = {
        response: {
          status: 400,
          data: {
            detail: 'Invalid language: only en and es are supported',
          },
        },
      };

      vi.mocked(apiClient.patch).mockRejectedValue(error);

      const settings = { preferred_language: 'fr' as any };

      await expect(userService.updateSettings(settings)).rejects.toEqual(error);
    });

    it('handles 401 authentication error', async () => {
      const error = {
        response: {
          status: 401,
          data: {
            detail: 'Not authenticated',
          },
        },
      };

      vi.mocked(apiClient.patch).mockRejectedValue(error);

      const settings = { preferred_language: 'es' as const };

      await expect(userService.updateSettings(settings)).rejects.toEqual(error);
    });

    it('handles network error', async () => {
      const error = new Error('Network Error');
      vi.mocked(apiClient.patch).mockRejectedValue(error);

      const settings = { preferred_language: 'es' as const };

      await expect(userService.updateSettings(settings)).rejects.toThrow('Network Error');
    });
  });
});
