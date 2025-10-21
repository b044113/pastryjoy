import { apiClient } from './api';
import { type UserSettings, type UpdateUserSettingsRequest } from '../types';

export const userService = {
  /**
   * Get current user's settings
   */
  getSettings: () => apiClient.get<UserSettings>('/api/users/me/settings'),

  /**
   * Update current user's settings
   */
  updateSettings: (settings: UpdateUserSettingsRequest) =>
    apiClient.patch<UserSettings>('/api/users/me/settings', settings),
};
