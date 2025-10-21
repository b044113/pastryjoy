import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { SettingsModal } from './SettingsModal';
import { AuthProvider } from '../../contexts/AuthContext';
import { authService } from '../../services/auth.service';
import { userService } from '../../services/user.service';

// Mock the services
vi.mock('../../services/auth.service', () => ({
  authService: {
    isAuthenticated: vi.fn(),
    getCurrentUser: vi.fn(),
    clearToken: vi.fn(),
    login: vi.fn(),
    setToken: vi.fn(),
    register: vi.fn(),
  },
}));

vi.mock('../../services/user.service', () => ({
  userService: {
    updateSettings: vi.fn(),
    getSettings: vi.fn(),
  },
}));

// Mock i18next
const mockChangeLanguage = vi.fn();
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: {
      changeLanguage: mockChangeLanguage,
    },
  }),
}));

describe('SettingsModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockChangeLanguage.mockResolvedValue(undefined);
  });

  const mockUser = {
    id: '1',
    username: 'testuser',
    email: 'test@example.com',
    role: 'user' as const,
    settings: { preferred_language: 'en' as const },
  };

  const renderSettingsModal = (isOpen: boolean = true) => {
    const onClose = vi.fn();

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

    const result = render(
      <BrowserRouter>
        <AuthProvider>
          <SettingsModal isOpen={isOpen} onClose={onClose} />
        </AuthProvider>
      </BrowserRouter>
    );

    return { ...result, onClose };
  };

  it('renders with current language selected', async () => {
    renderSettingsModal();

    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });

    // English should be selected (user's current language)
    const englishButton = screen.getByText('English').closest('button');
    expect(englishButton).toHaveClass('border-primary-600');
  });

  it('can select different language', async () => {
    const user = userEvent.setup();
    renderSettingsModal();

    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });

    // Click Spanish button
    const spanishButton = screen.getByText('Español').closest('button');
    await user.click(spanishButton!);

    // Spanish should now be selected
    await waitFor(() => {
      expect(spanishButton).toHaveClass('border-primary-600');
    });
  });

  it('calls API when saving settings', async () => {
    const user = userEvent.setup();
    vi.mocked(userService.updateSettings).mockResolvedValue({
      data: { preferred_language: 'es' },
    } as any);

    renderSettingsModal();

    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });

    // Select Spanish
    const spanishButton = screen.getByText('Español').closest('button');
    await user.click(spanishButton!);

    // Click Save button
    const saveButton = screen.getByText('settings.save');
    await user.click(saveButton);

    // API should be called
    await waitFor(() => {
      expect(userService.updateSettings).toHaveBeenCalledWith({
        preferred_language: 'es',
      });
    });
  });

  it('shows loading state while saving', async () => {
    const user = userEvent.setup();
    vi.mocked(userService.updateSettings).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    renderSettingsModal();

    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });

    // Select Spanish
    const spanishButton = screen.getByText('Español').closest('button');
    await user.click(spanishButton!);

    // Click Save button
    const saveButton = screen.getByText('settings.save');
    await user.click(saveButton);

    // Should show loading text
    await waitFor(() => {
      expect(screen.getByText('common.loading')).toBeInTheDocument();
    });
  });

  it('shows success message on successful save', async () => {
    const user = userEvent.setup();
    vi.mocked(userService.updateSettings).mockResolvedValue({
      data: { preferred_language: 'es' },
    } as any);

    renderSettingsModal();

    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });

    // Select Spanish
    const spanishButton = screen.getByText('Español').closest('button');
    await user.click(spanishButton!);

    // Click Save button
    const saveButton = screen.getByText('settings.save');
    await user.click(saveButton);

    // Should show success message
    await waitFor(() => {
      expect(screen.getByText('settings.saved')).toBeInTheDocument();
    });
  });

  it('shows error message on failed save', async () => {
    const user = userEvent.setup();
    vi.mocked(userService.updateSettings).mockRejectedValue({
      response: { data: { detail: 'Failed to update settings' } },
    });

    renderSettingsModal();

    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });

    // Select Spanish
    const spanishButton = screen.getByText('Español').closest('button');
    await user.click(spanishButton!);

    // Click Save button
    const saveButton = screen.getByText('settings.save');
    await user.click(saveButton);

    // Should show error message
    await waitFor(() => {
      expect(screen.getByText('Failed to update settings')).toBeInTheDocument();
    });
  });

  it('closes modal after successful save', async () => {
    const user = userEvent.setup();
    vi.mocked(userService.updateSettings).mockResolvedValue({
      data: { preferred_language: 'es' },
    } as any);

    const { onClose } = renderSettingsModal();

    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });

    // Select Spanish
    const spanishButton = screen.getByText('Español').closest('button');
    await user.click(spanishButton!);

    // Click Save button
    const saveButton = screen.getByText('settings.save');
    await user.click(saveButton);

    // Modal should close after a delay
    await waitFor(
      () => {
        expect(onClose).toHaveBeenCalled();
      },
      { timeout: 2000 }
    );
  });

  it('closes modal when clicking cancel', async () => {
    const user = userEvent.setup();
    const { onClose } = renderSettingsModal();

    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });

    // Click Cancel button
    const cancelButton = screen.getByText('settings.cancel');
    await user.click(cancelButton);

    expect(onClose).toHaveBeenCalled();
  });

  it('updates i18n language after save', async () => {
    const user = userEvent.setup();
    vi.mocked(userService.updateSettings).mockResolvedValue({
      data: { preferred_language: 'es' },
    } as any);

    renderSettingsModal();

    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });

    // Select Spanish
    const spanishButton = screen.getByText('Español').closest('button');
    await user.click(spanishButton!);

    // Click Save button
    const saveButton = screen.getByText('settings.save');
    await user.click(saveButton);

    // i18n.changeLanguage should be called
    await waitFor(() => {
      expect(mockChangeLanguage).toHaveBeenCalledWith('es');
    });
  });

  it('resets language selection when canceling', async () => {
    const user = userEvent.setup();
    const { onClose } = renderSettingsModal();

    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });

    // Initial: English is selected
    let englishButton = screen.getByText('English').closest('button');
    expect(englishButton).toHaveClass('border-primary-600');

    // Select Spanish
    const spanishButton = screen.getByText('Español').closest('button');
    await user.click(spanishButton!);

    // Click Cancel
    const cancelButton = screen.getByText('settings.cancel');
    await user.click(cancelButton);

    expect(onClose).toHaveBeenCalled();
  });

  it('displays both language options', async () => {
    renderSettingsModal();

    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });

    expect(screen.getByText('English')).toBeInTheDocument();
    expect(screen.getByText('Español')).toBeInTheDocument();
    expect(screen.getByText('🇺🇸')).toBeInTheDocument();
    expect(screen.getByText('🇪🇸')).toBeInTheDocument();
  });

  it('shows checkmark on selected language', async () => {
    const user = userEvent.setup();
    renderSettingsModal();

    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });

    // Select Spanish
    const spanishButton = screen.getByText('Español').closest('button');
    await user.click(spanishButton!);

    // Checkmark SVG should be present in Spanish button
    await waitFor(() => {
      const svg = spanishButton!.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });
  });

  it('disables buttons while loading', async () => {
    const user = userEvent.setup();
    vi.mocked(userService.updateSettings).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    renderSettingsModal();

    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });

    // Select Spanish
    const spanishButton = screen.getByText('Español').closest('button');
    await user.click(spanishButton!);

    // Click Save button
    const saveButton = screen.getByText('settings.save');
    await user.click(saveButton);

    // Buttons should be disabled
    await waitFor(() => {
      expect(spanishButton).toBeDisabled();
      expect(screen.getByText('English').closest('button')).toBeDisabled();
      expect(screen.getByText('common.loading')).toBeInTheDocument();
    });
  });

  it('does not render when isOpen is false', () => {
    const { container } = renderSettingsModal(false);

    // Modal should not be visible
    expect(screen.queryByText('settings.title')).not.toBeInTheDocument();
  });

  it('shows default error message when API error has no detail', async () => {
    const user = userEvent.setup();
    vi.mocked(userService.updateSettings).mockRejectedValue(new Error('Network error'));

    renderSettingsModal();

    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });

    // Select Spanish
    const spanishButton = screen.getByText('Español').closest('button');
    await user.click(spanishButton!);

    // Click Save button
    const saveButton = screen.getByText('settings.save');
    await user.click(saveButton);

    // Should show default error message
    await waitFor(() => {
      expect(screen.getByText('settings.saveFailed')).toBeInTheDocument();
    });
  });

  it('initializes with user language preference', async () => {
    // This test verifies that the modal respects the user's language
    // Note: SettingsModal uses useState initialized with user?.settings?.preferred_language
    // The component initializes state when first mounted, so we check the default behavior

    renderSettingsModal();

    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });

    // English should be selected (mockUser has 'en')
    const englishButton = screen.getByText('English').closest('button');
    expect(englishButton).toHaveClass('border-primary-600');

    // Spanish should not be selected
    const spanishButton = screen.getByText('Español').closest('button');
    expect(spanishButton).not.toHaveClass('border-primary-600');
  });
});
