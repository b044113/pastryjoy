import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Navbar } from './Navbar';
import { AuthProvider } from '../../contexts/AuthContext';
import { authService } from '../../services/auth.service';
import userEvent from '@testing-library/user-event';

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

describe('Navbar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  const renderNavbar = () => {
    return render(
      <BrowserRouter>
        <AuthProvider>
          <Navbar />
        </AuthProvider>
      </BrowserRouter>
    );
  };

  it('renders logo and title', () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(false);
    renderNavbar();

    expect(screen.getByText('🥐')).toBeInTheDocument();
    expect(screen.getByText('PastryJoy')).toBeInTheDocument();
  });

  it('does not show navigation links when user is not logged in', () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(false);
    renderNavbar();

    expect(screen.queryByText('nav.dashboard')).not.toBeInTheDocument();
    expect(screen.queryByText('nav.orders')).not.toBeInTheDocument();
    expect(screen.queryByText('nav.logout')).not.toBeInTheDocument();
  });

  it('shows navigation links for regular user', async () => {
    const mockUser = {
      id: '1',
      username: 'testuser',
      email: 'test@example.com',
      role: 'user' as const,
      settings: { preferred_language: 'en' },
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

    renderNavbar();

    // Wait for user to load
    await screen.findByText('testuser');

    expect(screen.getByText('nav.dashboard')).toBeInTheDocument();
    expect(screen.getByText('nav.orders')).toBeInTheDocument();
    // UserMenu is rendered (verified by username presence)
    expect(screen.getByText('testuser')).toBeInTheDocument();
  });

  it('does not show admin links for regular user', async () => {
    const mockUser = {
      id: '1',
      username: 'testuser',
      email: 'test@example.com',
      role: 'user' as const,
      settings: { preferred_language: 'en' },
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

    renderNavbar();

    await screen.findByText('testuser');

    expect(screen.queryByText('nav.ingredients')).not.toBeInTheDocument();
    expect(screen.queryByText('nav.recipes')).not.toBeInTheDocument();
    expect(screen.queryByText('nav.products')).not.toBeInTheDocument();
  });

  it('shows admin links for admin user', async () => {
    const mockAdmin = {
      id: '1',
      username: 'adminuser',
      email: 'admin@example.com',
      role: 'admin' as const,
      settings: { preferred_language: 'en' },
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockAdmin);

    renderNavbar();

    await screen.findByText('adminuser');

    expect(screen.getByText('nav.dashboard')).toBeInTheDocument();
    expect(screen.getByText('nav.ingredients')).toBeInTheDocument();
    expect(screen.getByText('nav.recipes')).toBeInTheDocument();
    expect(screen.getByText('nav.products')).toBeInTheDocument();
    expect(screen.getByText('nav.orders')).toBeInTheDocument();
  });

  it('displays user info correctly', async () => {
    const mockUser = {
      id: '1',
      username: 'johndoe',
      email: 'john@example.com',
      role: 'user' as const,
      settings: { preferred_language: 'en' },
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

    renderNavbar();

    await screen.findByText('johndoe');

    expect(screen.getByText('johndoe')).toBeInTheDocument();
    expect(screen.getByText('user')).toBeInTheDocument();
  });

  it('handles logout correctly', async () => {
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

    renderNavbar();

    await screen.findByText('testuser');

    // Open UserMenu dropdown
    const userButton = screen.getByRole('button', { expanded: false });
    await user.click(userButton);

    // Click logout in dropdown
    const logoutButton = screen.getByText('nav.logout');
    await user.click(logoutButton);

    expect(authService.clearToken).toHaveBeenCalled();
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  it('has correct links to routes', async () => {
    const mockAdmin = {
      id: '1',
      username: 'adminuser',
      email: 'admin@example.com',
      role: 'admin' as const,
      settings: { preferred_language: 'en' },
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockAdmin);

    renderNavbar();

    await screen.findByText('adminuser');

    const dashboardLink = screen.getByText('nav.dashboard').closest('a');
    const ingredientsLink = screen.getByText('nav.ingredients').closest('a');
    const recipesLink = screen.getByText('nav.recipes').closest('a');
    const productsLink = screen.getByText('nav.products').closest('a');
    const ordersLink = screen.getByText('nav.orders').closest('a');
    const logoLink = screen.getByText('PastryJoy').closest('a');

    expect(dashboardLink).toHaveAttribute('href', '/dashboard');
    expect(ingredientsLink).toHaveAttribute('href', '/ingredients');
    expect(recipesLink).toHaveAttribute('href', '/recipes');
    expect(productsLink).toHaveAttribute('href', '/products');
    expect(ordersLink).toHaveAttribute('href', '/orders');
    expect(logoLink).toHaveAttribute('href', '/');
  });
});
