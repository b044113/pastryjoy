import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { DashboardPage } from './DashboardPage';
import { AuthProvider } from '../../contexts/AuthContext';
import { authService } from '../../services/auth.service';

// Mock auth service
vi.mock('../../services/auth.service', () => ({
  authService: {
    isAuthenticated: vi.fn(),
    getCurrentUser: vi.fn(),
    clearToken: vi.fn(),
  },
}));

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const renderDashboardPage = (isAdmin = false) => {
    const mockUser = {
      id: '1',
      username: isAdmin ? 'adminuser' : 'regularuser',
      email: isAdmin ? 'admin@test.com' : 'user@test.com',
      role: isAdmin ? ('admin' as const) : ('user' as const),
      full_name: isAdmin ? 'Admin User' : 'Regular User',
    };

    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockUser);

    return render(
      <BrowserRouter>
        <AuthProvider>
          <DashboardPage />
        </AuthProvider>
      </BrowserRouter>
    );
  };

  describe('Admin User', () => {
    it('renders welcome message with user name', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText(/welcome back, Admin User!/i)).toBeInTheDocument();
    });

    it('shows admin description message', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText(/manage your bakery operations from here/i)).toBeInTheDocument();
    });

    it('renders all admin navigation cards', async () => {
      renderDashboardPage(true);

      const ingredientsElements = await screen.findAllByText('Ingredients');
      expect(ingredientsElements.length).toBeGreaterThan(0);

      const recipesElements = screen.getAllByText('Recipes');
      expect(recipesElements.length).toBeGreaterThan(0);

      const productsElements = screen.getAllByText('Products');
      expect(productsElements.length).toBeGreaterThan(0);

      const ordersElements = screen.getAllByText('Orders');
      expect(ordersElements.length).toBeGreaterThan(0);
    });

    it('renders correct icons for admin cards', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText('🥚')).toBeInTheDocument(); // Ingredients
      expect(screen.getByText('📖')).toBeInTheDocument(); // Recipes
      expect(screen.getByText('🎂')).toBeInTheDocument(); // Products
      expect(screen.getByText('📦')).toBeInTheDocument(); // Orders
    });

    it('renders ingredient card description', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText('Manage your bakery ingredients')).toBeInTheDocument();
    });

    it('renders recipes card description', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText('Create and manage recipes')).toBeInTheDocument();
    });

    it('renders products card description', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText('Manage your product catalog')).toBeInTheDocument();
    });
  });

  describe('Regular User', () => {
    it('renders welcome message with user name', async () => {
      renderDashboardPage(false);

      expect(await screen.findByText(/welcome back, Regular User!/i)).toBeInTheDocument();
    });

    it('shows user description message', async () => {
      renderDashboardPage(false);

      const descriptions = await screen.findAllByText(/view and create orders/i);
      expect(descriptions.length).toBeGreaterThan(0);
    });

    it('only renders orders card for regular users', async () => {
      renderDashboardPage(false);

      // Orders should be present
      const ordersElements = await screen.findAllByText('Orders');
      expect(ordersElements.length).toBeGreaterThan(0);

      // Admin sections should not be present (they only appear in navbar, not in cards)
      expect(screen.queryByText('Manage your bakery ingredients')).not.toBeInTheDocument();
      expect(screen.queryByText('Create and manage recipes')).not.toBeInTheDocument();
      expect(screen.queryByText('Manage your product catalog')).not.toBeInTheDocument();
    });

    it('renders orders card description', async () => {
      renderDashboardPage(false);

      const descriptions = await screen.findAllByText('View and create orders');
      expect(descriptions.length).toBeGreaterThan(0);
    });
  });

  describe('Quick Stats Section', () => {
    it('renders quick stats heading', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText('Quick Stats')).toBeInTheDocument();
    });

    it('renders total orders stat', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText(/total orders/i)).toBeInTheDocument();
    });

    it('renders active products stat', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText(/active products/i)).toBeInTheDocument();
    });

    it('renders revenue stat', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText(/revenue/i)).toBeInTheDocument();
    });

    it('shows coming soon message for stats', async () => {
      renderDashboardPage(true);

      const comingSoonMessages = await screen.findAllByText(/coming soon/i);
      expect(comingSoonMessages).toHaveLength(3);
    });
  });
});
