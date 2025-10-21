import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { UserMenu } from './UserMenu';
import { AuthProvider } from '../../contexts/AuthContext';
import { authService } from '../../services/auth.service';

// Mock the auth service
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

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: {
      changeLanguage: vi.fn(),
    },
  }),
}));

describe('UserMenu', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  const renderUserMenu = () => {
    return render(
      <BrowserRouter>
        <AuthProvider>
          <UserMenu />
        </AuthProvider>
      </BrowserRouter>
    );
  };

  it('renders user name when user is logged in', async () => {
    const mockUser = {
      id: '1',
      username: 'johndoe',
      email: 'john@example.com',
      role: 'user' as const,
      full_name: 'John Doe',
      settings: { preferred_language: 'en' },
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

    renderUserMenu();

    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
    });
  });

  it('renders username when full_name is not available', async () => {
    const mockUser = {
      id: '1',
      username: 'johndoe',
      email: 'john@example.com',
      role: 'user' as const,
      full_name: null,
      settings: { preferred_language: 'en' },
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

    renderUserMenu();

    await waitFor(() => {
      expect(screen.getByText('johndoe')).toBeInTheDocument();
    });
  });

  it('opens dropdown when user button is clicked', async () => {
    const user = userEvent.setup();
    const mockUser = {
      id: '1',
      username: 'testuser',
      email: 'test@example.com',
      role: 'user' as const,
      settings: { preferred_language: 'en' },
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

    renderUserMenu();

    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument();
    });

    // Click the user button
    const userButton = screen.getByRole('button', { expanded: false });
    await user.click(userButton);

    // Dropdown should be visible
    await waitFor(() => {
      expect(screen.getByRole('button', { expanded: true })).toBeInTheDocument();
      expect(screen.getByText('nav.settings')).toBeInTheDocument();
      expect(screen.getByText('nav.logout')).toBeInTheDocument();
    });
  });

  it('closes dropdown when clicking outside', async () => {
    const user = userEvent.setup();
    const mockUser = {
      id: '1',
      username: 'testuser',
      email: 'test@example.com',
      role: 'user' as const,
      settings: { preferred_language: 'en' },
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

    const { container } = renderUserMenu();

    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument();
    });

    // Open dropdown
    const userButton = screen.getByRole('button', { expanded: false });
    await user.click(userButton);

    await waitFor(() => {
      expect(screen.getByText('nav.settings')).toBeInTheDocument();
    });

    // Click outside
    await user.click(container);

    // Dropdown should be closed
    await waitFor(() => {
      expect(screen.queryByText('nav.settings')).not.toBeInTheDocument();
    });
  });

  it('shows Settings and Logout options in dropdown', async () => {
    const user = userEvent.setup();
    const mockUser = {
      id: '1',
      username: 'testuser',
      email: 'test@example.com',
      role: 'user' as const,
      settings: { preferred_language: 'en' },
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

    renderUserMenu();

    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument();
    });

    // Open dropdown
    const userButton = screen.getByRole('button', { expanded: false });
    await user.click(userButton);

    // Check for menu items
    await waitFor(() => {
      const settingsButton = screen.getByText('nav.settings');
      const logoutButton = screen.getByText('nav.logout');

      expect(settingsButton).toBeInTheDocument();
      expect(logoutButton).toBeInTheDocument();
    });
  });

  it('opens SettingsModal when clicking Settings', async () => {
    const user = userEvent.setup();
    const mockUser = {
      id: '1',
      username: 'testuser',
      email: 'test@example.com',
      role: 'user' as const,
      settings: { preferred_language: 'en' },
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

    renderUserMenu();

    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument();
    });

    // Open dropdown
    const userButton = screen.getByRole('button', { expanded: false });
    await user.click(userButton);

    // Click Settings
    const settingsButton = screen.getByText('nav.settings');
    await user.click(settingsButton);

    // SettingsModal should be rendered (check for modal title)
    await waitFor(() => {
      expect(screen.getByText('settings.title')).toBeInTheDocument();
    });
  });

  it('calls logout and navigates when clicking Logout', async () => {
    const user = userEvent.setup();
    const mockUser = {
      id: '1',
      username: 'testuser',
      email: 'test@example.com',
      role: 'user' as const,
      settings: { preferred_language: 'en' },
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

    renderUserMenu();

    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument();
    });

    // Open dropdown
    const userButton = screen.getByRole('button', { expanded: false });
    await user.click(userButton);

    // Click Logout
    const logoutButton = screen.getByText('nav.logout');
    await user.click(logoutButton);

    // Should clear token and navigate to login
    await waitFor(() => {
      expect(authService.clearToken).toHaveBeenCalled();
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });

  it('displays user role correctly', async () => {
    const mockAdmin = {
      id: '1',
      username: 'adminuser',
      email: 'admin@example.com',
      role: 'admin' as const,
      settings: { preferred_language: 'en' },
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockAdmin);

    renderUserMenu();

    await waitFor(() => {
      expect(screen.getByText('admin')).toBeInTheDocument();
    });
  });

  it('displays user email in dropdown header', async () => {
    const user = userEvent.setup();
    const mockUser = {
      id: '1',
      username: 'testuser',
      email: 'test@example.com',
      role: 'user' as const,
      settings: { preferred_language: 'en' },
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

    renderUserMenu();

    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument();
    });

    // Open dropdown
    const userButton = screen.getByRole('button', { expanded: false });
    await user.click(userButton);

    // Check for email in dropdown
    await waitFor(() => {
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
    });
  });

  it('renders nothing when user is not logged in', () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(false);

    const { container } = renderUserMenu();

    expect(container.firstChild).toBeNull();
  });

  it('displays user initial in avatar', async () => {
    const mockUser = {
      id: '1',
      username: 'johndoe',
      email: 'john@example.com',
      role: 'user' as const,
      full_name: 'John Doe',
      settings: { preferred_language: 'en' },
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

    renderUserMenu();

    await waitFor(() => {
      // Avatar should show first letter of display name (J from John Doe)
      expect(screen.getByText('J')).toBeInTheDocument();
    });
  });

  it('closes dropdown when opening settings modal', async () => {
    const user = userEvent.setup();
    const mockUser = {
      id: '1',
      username: 'testuser',
      email: 'test@example.com',
      role: 'user' as const,
      settings: { preferred_language: 'en' },
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

    renderUserMenu();

    await waitFor(() => {
      expect(screen.getByText('testuser')).toBeInTheDocument();
    });

    // Open dropdown
    const userButton = screen.getByRole('button', { expanded: false });
    await user.click(userButton);

    await waitFor(() => {
      expect(screen.getByText('nav.settings')).toBeInTheDocument();
    });

    // Click Settings
    const settingsButton = screen.getByText('nav.settings');
    await user.click(settingsButton);

    // Dropdown should be closed (aria-expanded should be false)
    await waitFor(() => {
      expect(screen.getByRole('button', { expanded: false })).toBeInTheDocument();
    });
  });
});
