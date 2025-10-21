import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { authService } from './services/auth.service';

// Import pages
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { DashboardPage } from './pages/dashboard/DashboardPage';
import { IngredientsPage } from './pages/ingredients/IngredientsPage';
import { RecipesPage } from './pages/recipes/RecipesPage';
import { ProductsPage } from './pages/products/ProductsPage';
import { OrdersPage } from './pages/orders/OrdersPage';
import { Loading } from './components/common/Loading';
import { useAuth } from './contexts/AuthContext';
import React from 'react';

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode; adminOnly?: boolean }> = ({
  children,
  adminOnly = false,
}) => {
  const { user, loading, isAdmin } = useAuth();

  if (loading) {
    return <Loading fullScreen />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (adminOnly && !isAdmin()) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

// Public Route Component (redirect if already authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return <Loading fullScreen />;
  }

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

// Mock all services
vi.mock('./services/auth.service', () => ({
  authService: {
    isAuthenticated: vi.fn(),
    getCurrentUser: vi.fn(),
    clearToken: vi.fn(),
    login: vi.fn(),
    register: vi.fn(),
  },
}));

vi.mock('./services/ingredient.service', () => ({
  ingredientService: {
    getAll: vi.fn().mockResolvedValue([]),
  },
}));

vi.mock('./services/recipe.service', () => ({
  recipeService: {
    getAll: vi.fn().mockResolvedValue([]),
  },
}));

vi.mock('./services/product.service', () => ({
  productService: {
    getAll: vi.fn().mockResolvedValue([]),
  },
}));

vi.mock('./services/order.service', () => ({
  orderService: {
    getAll: vi.fn().mockResolvedValue([]),
  },
}));

// Test App component that uses MemoryRouter
const TestApp: React.FC<{ initialRoute: string }> = ({ initialRoute }) => {
  return (
    <MemoryRouter initialEntries={[initialRoute]}>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            }
          />
          <Route
            path="/register"
            element={
              <PublicRoute>
                <RegisterPage />
              </PublicRoute>
            }
          />

          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/ingredients"
            element={
              <ProtectedRoute adminOnly>
                <IngredientsPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/recipes"
            element={
              <ProtectedRoute adminOnly>
                <RecipesPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/products"
            element={
              <ProtectedRoute adminOnly>
                <ProductsPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/orders"
            element={
              <ProtectedRoute>
                <OrdersPage />
              </ProtectedRoute>
            }
          />

          {/* Redirect root to dashboard or login */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* 404 */}
          <Route
            path="*"
            element={
              <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                  <h1 className="text-6xl font-bold text-gray-900 mb-4">404</h1>
                  <p className="text-gray-600 mb-6">Page not found</p>
                  <a href="/dashboard" className="text-primary-600 hover:text-primary-700 font-medium">
                    Go to Dashboard
                  </a>
                </div>
              </div>
            }
          />
        </Routes>
      </AuthProvider>
    </MemoryRouter>
  );
};

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Public Routes', () => {
    beforeEach(() => {
      vi.mocked(authService.isAuthenticated).mockReturnValue(false);
      vi.mocked(authService.getCurrentUser).mockResolvedValue(null);
    });

    it('renders login page at /login', async () => {
      render(<TestApp initialRoute="/login" />);

      await waitFor(() => {
        expect(screen.getByText(/PastryJoy/i)).toBeInTheDocument();
      });
    });

    it('renders register page at /register', async () => {
      render(<TestApp initialRoute="/register" />);

      await waitFor(() => {
        expect(screen.getByText(/create.*account/i)).toBeInTheDocument();
      });
    });

    it('redirects to login when accessing protected route without auth', async () => {
      render(<TestApp initialRoute="/dashboard" />);

      await waitFor(() => {
        expect(screen.getByText(/PastryJoy/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
      });
    });

    it('redirects root to dashboard which then redirects to login', async () => {
      render(<TestApp initialRoute="/" />);

      await waitFor(() => {
        expect(screen.getByText(/PastryJoy/i)).toBeInTheDocument();
      });
    });
  });

  describe('Protected Routes - Regular User', () => {
    beforeEach(() => {
      vi.mocked(authService.isAuthenticated).mockReturnValue(true);
      vi.mocked(authService.getCurrentUser).mockResolvedValue({
        id: 1,
        email: 'user@test.com',
        username: 'testuser',
        full_name: 'Test User',
        role: 'user',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
      });
    });

    it('renders dashboard for authenticated user', async () => {
      render(<TestApp initialRoute="/dashboard" />);

      await waitFor(() => {
        expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
      });
    });

    it('redirects regular user from admin-only routes to dashboard', async () => {
      render(<TestApp initialRoute="/ingredients" />);

      await waitFor(() => {
        expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
      });
    });

    it('allows regular user to access orders page', async () => {
      render(<TestApp initialRoute="/orders" />);

      await waitFor(() => {
        expect(screen.getByText('orders.title')).toBeInTheDocument();
      });
    });

    it('redirects authenticated user from login to dashboard', async () => {
      render(<TestApp initialRoute="/login" />);

      await waitFor(() => {
        expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
      });
    });

    it('redirects authenticated user from register to dashboard', async () => {
      render(<TestApp initialRoute="/register" />);

      await waitFor(() => {
        expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
      });
    });
  });

  describe('Protected Routes - Admin User', () => {
    beforeEach(() => {
      vi.mocked(authService.isAuthenticated).mockReturnValue(true);
      vi.mocked(authService.getCurrentUser).mockResolvedValue({
        id: 1,
        email: 'admin@test.com',
        username: 'admin',
        full_name: 'Admin User',
        role: 'admin',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
      });
    });

    it('allows admin to access ingredients page', async () => {
      render(<TestApp initialRoute="/ingredients" />);

      await waitFor(() => {
        expect(screen.getByText('ingredients.title')).toBeInTheDocument();
      });
    });

    it('allows admin to access recipes page', async () => {
      render(<TestApp initialRoute="/recipes" />);

      await waitFor(() => {
        expect(screen.getByText('recipes.title')).toBeInTheDocument();
      });
    });

    it('allows admin to access products page', async () => {
      render(<TestApp initialRoute="/products" />);

      await waitFor(() => {
        expect(screen.getByText('products.title')).toBeInTheDocument();
      });
    });

    it('allows admin to access orders page', async () => {
      render(<TestApp initialRoute="/orders" />);

      await waitFor(() => {
        expect(screen.getByText('orders.title')).toBeInTheDocument();
      });
    });
  });

  describe('404 Not Found', () => {
    beforeEach(() => {
      vi.mocked(authService.isAuthenticated).mockReturnValue(false);
      vi.mocked(authService.getCurrentUser).mockResolvedValue(null);
    });

    it('renders 404 page for unknown routes', async () => {
      render(<TestApp initialRoute="/unknown-route" />);

      await waitFor(() => {
        expect(screen.getByText('404')).toBeInTheDocument();
        expect(screen.getByText(/page not found/i)).toBeInTheDocument();
      });
    });

    it('renders link to dashboard on 404 page', async () => {
      render(<TestApp initialRoute="/invalid" />);

      await waitFor(() => {
        const link = screen.getByText(/go to dashboard/i);
        expect(link).toBeInTheDocument();
        expect(link).toHaveAttribute('href', '/dashboard');
      });
    });
  });

  describe('Loading States', () => {
    it('shows loading screen while checking authentication', async () => {
      vi.mocked(authService.isAuthenticated).mockReturnValue(true);
      vi.mocked(authService.getCurrentUser).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({
          id: 1,
          email: 'user@test.com',
          username: 'testuser',
          full_name: 'Test User',
          role: 'user',
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
        }), 100))
      );

      render(<TestApp initialRoute="/dashboard" />);

      // Should show loading initially
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();

      // Wait for content to load
      await waitFor(() => {
        expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
      });
    });
  });
});
