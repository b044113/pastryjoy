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

      expect(await screen.findByText(/dashboard.welcomeBack/i)).toBeInTheDocument();
    });

    it('shows admin description message', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText(/dashboard.adminSubtitle/i)).toBeInTheDocument();
    });

    it('renders all admin navigation cards', async () => {
      renderDashboardPage(true);

      const ingredientsElements = await screen.findAllByText('dashboard.cards.ingredients.title');
      expect(ingredientsElements.length).toBeGreaterThan(0);

      const recipesElements = screen.getAllByText('dashboard.cards.recipes.title');
      expect(recipesElements.length).toBeGreaterThan(0);

      const productsElements = screen.getAllByText('dashboard.cards.products.title');
      expect(productsElements.length).toBeGreaterThan(0);

      const ordersElements = screen.getAllByText('dashboard.cards.orders.title');
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

      expect(await screen.findByText('dashboard.cards.ingredients.description')).toBeInTheDocument();
    });

    it('renders recipes card description', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText('dashboard.cards.recipes.description')).toBeInTheDocument();
    });

    it('renders products card description', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText('dashboard.cards.products.description')).toBeInTheDocument();
    });
  });

  describe('Regular User', () => {
    it('renders welcome message with user name', async () => {
      renderDashboardPage(false);

      expect(await screen.findByText(/dashboard.welcomeBack/i)).toBeInTheDocument();
    });

    it('shows user description message', async () => {
      renderDashboardPage(false);

      const descriptions = await screen.findAllByText(/dashboard.userSubtitle/i);
      expect(descriptions.length).toBeGreaterThan(0);
    });

    it('only renders orders card for regular users', async () => {
      renderDashboardPage(false);

      // Orders should be present
      const ordersElements = await screen.findAllByText('dashboard.cards.orders.title');
      expect(ordersElements.length).toBeGreaterThan(0);

      // Admin sections should not be present (they only appear in navbar, not in cards)
      expect(screen.queryByText('dashboard.cards.ingredients.description')).not.toBeInTheDocument();
      expect(screen.queryByText('dashboard.cards.recipes.description')).not.toBeInTheDocument();
      expect(screen.queryByText('dashboard.cards.products.description')).not.toBeInTheDocument();
    });

    it('renders orders card description', async () => {
      renderDashboardPage(false);

      const descriptions = await screen.findAllByText('dashboard.cards.orders.description');
      expect(descriptions.length).toBeGreaterThan(0);
    });
  });

  describe('Quick Stats Section', () => {
    it('renders quick stats heading', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText('dashboard.quickStats')).toBeInTheDocument();
    });

    it('renders total orders stat', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText(/dashboard.totalOrders/i)).toBeInTheDocument();
    });

    it('renders active products stat', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText(/dashboard.activeProducts/i)).toBeInTheDocument();
    });

    it('renders revenue stat', async () => {
      renderDashboardPage(true);

      expect(await screen.findByText(/dashboard.revenue/i)).toBeInTheDocument();
    });

    it('shows coming soon message for stats', async () => {
      renderDashboardPage(true);

      const comingSoonMessages = await screen.findAllByText(/dashboard.comingSoon/i);
      expect(comingSoonMessages).toHaveLength(3);
    });
  });
});
