import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import { ProductsPage } from './ProductsPage';
import { AuthProvider } from '../../contexts/AuthContext';
import { authService } from '../../services/auth.service';
import { productService } from '../../services/product.service';
import { recipeService } from '../../services/recipe.service';
import type { Product, Recipe } from '../../types';

// Mock services
vi.mock('../../services/auth.service', () => ({
  authService: {
    login: vi.fn(),
    register: vi.fn(),
    getCurrentUser: vi.fn(),
    setToken: vi.fn(),
    getToken: vi.fn(),
    clearToken: vi.fn(),
    isAuthenticated: vi.fn(),
  },
}));

vi.mock('../../services/product.service', () => ({
  productService: {
    getAll: vi.fn(),
    getById: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}));

vi.mock('../../services/recipe.service', () => ({
  recipeService: {
    getAll: vi.fn(),
    getById: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}));

global.confirm = vi.fn(() => true);
global.alert = vi.fn();

describe('ProductsPage', () => {
  const mockAdmin = {
    id: '1',
    username: 'adminuser',
    email: 'admin@test.com',
    role: 'admin' as const,
    is_active: true,
    full_name: 'Admin User',
    created_at: '2025-01-01T10:00:00Z',
  };

  const mockRecipes: Recipe[] = [
    {
      id: '1',
      name: 'Bread Dough',
      instructions: 'Mix',
      ingredients: [],
      created_at: '2025-01-01T10:00:00Z',
      updated_at: '2025-01-01T10:00:00Z',
    },
  ];

  const mockProducts: Product[] = [
    {
      id: '1',
      name: 'Sourdough Bread',
      image_url: 'bread.jpg',
      fixed_costs: 2.5,
      variable_costs_percentage: 20,
      profit_margin_percentage: 30,
      recipes: [{ recipe_id: '1', recipe_name: 'Bread Dough', quantity: 1 }],
      created_at: '2025-01-01T10:00:00Z',
      updated_at: '2025-01-01T10:00:00Z',
    },
    {
      id: '2',
      name: 'Chocolate Cake',
      image_url: 'cake.jpg',
      fixed_costs: 5.0,
      variable_costs_percentage: 25,
      profit_margin_percentage: 35,
      recipes: [],
      created_at: '2025-01-01T10:00:00Z',
      updated_at: '2025-01-01T10:00:00Z',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockAdmin);
  });

  const renderProductsPage = () => {
    return render(
      <BrowserRouter>
        <AuthProvider>
          <ProductsPage />
        </AuthProvider>
      </BrowserRouter>
    );
  };

  describe('Loading State', () => {
    it('shows loading spinner while fetching data', () => {
      vi.mocked(productService.getAll).mockImplementation(
        () => new Promise(() => {})
      );
      vi.mocked(recipeService.getAll).mockImplementation(
        () => new Promise(() => {})
      );

      renderProductsPage();

      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('shows empty state when no products exist', async () => {
      vi.mocked(productService.getAll).mockResolvedValue([]);
      vi.mocked(recipeService.getAll).mockResolvedValue(mockRecipes);

      renderProductsPage();

      expect(await screen.findByText(/products.noProducts/i)).toBeInTheDocument();
    });
  });

  describe('Products List', () => {
    it('renders page heading and description', async () => {
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);
      vi.mocked(recipeService.getAll).mockResolvedValue(mockRecipes);

      renderProductsPage();

      expect(await screen.findByText('products.title')).toBeInTheDocument();
      expect(screen.getByText('products.subtitle')).toBeInTheDocument();
    });

    it('renders all products', async () => {
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);
      vi.mocked(recipeService.getAll).mockResolvedValue(mockRecipes);

      renderProductsPage();

      expect(await screen.findByText('Sourdough Bread')).toBeInTheDocument();
      expect(screen.getByText('Chocolate Cake')).toBeInTheDocument();
    });

    it('renders add product button', async () => {
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);
      vi.mocked(recipeService.getAll).mockResolvedValue(mockRecipes);

      renderProductsPage();

      expect(await screen.findByText(/products.addProduct/i)).toBeInTheDocument();
    });
  });

  describe('Create Product', () => {
    it('opens modal when add product button is clicked', async () => {
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);
      vi.mocked(recipeService.getAll).mockResolvedValue(mockRecipes);
      const user = userEvent.setup();

      renderProductsPage();

      const addButton = await screen.findByText(/products.addProduct/i);
      await user.click(addButton);

      // The modal title is products.addProduct (not createProduct)
      expect(screen.getByText('common.cancel')).toBeInTheDocument();
    });
  });

  describe('Edit Product', () => {
    it('opens modal with product data when edit is clicked', async () => {
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);
      vi.mocked(recipeService.getAll).mockResolvedValue(mockRecipes);
      const user = userEvent.setup();

      renderProductsPage();

      const editButtons = await screen.findAllByText('common.edit');
      await user.click(editButtons[0]);

      expect(screen.getByText('products.editProduct')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Sourdough Bread')).toBeInTheDocument();
    });
  });

  describe('Delete Product', () => {
    it('deletes product when delete button is clicked and confirmed', async () => {
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);
      vi.mocked(recipeService.getAll).mockResolvedValue(mockRecipes);
      vi.mocked(productService.delete).mockResolvedValue(undefined);
      const user = userEvent.setup();

      renderProductsPage();

      const deleteButtons = await screen.findAllByText('common.delete');
      await user.click(deleteButtons[0]);

      await waitFor(() => {
        expect(confirm).toHaveBeenCalledWith('products.deleteConfirm');
        expect(productService.delete).toHaveBeenCalledWith('1');
      });
    });

    it('does not delete product when confirmation is cancelled', async () => {
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);
      vi.mocked(recipeService.getAll).mockResolvedValue(mockRecipes);
      vi.mocked(confirm).mockReturnValueOnce(false);
      const user = userEvent.setup();

      renderProductsPage();

      const deleteButtons = await screen.findAllByText('common.delete');
      await user.click(deleteButtons[0]);

      await waitFor(() => {
        expect(confirm).toHaveBeenCalled();
      });

      expect(productService.delete).not.toHaveBeenCalled();
    });
  });

  describe('Modal Controls', () => {
    it('closes modal when cancel button is clicked', async () => {
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);
      vi.mocked(recipeService.getAll).mockResolvedValue(mockRecipes);
      const user = userEvent.setup();

      renderProductsPage();

      const addButton = await screen.findByText(/products.addProduct/i);
      await user.click(addButton);

      // Modal should be open
      expect(screen.getByText('common.cancel')).toBeInTheDocument();

      const cancelButton = screen.getByText('common.cancel');
      await user.click(cancelButton);

      await waitFor(() => {
        expect(screen.queryByText('common.cancel')).not.toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('shows alert when delete fails', async () => {
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);
      vi.mocked(recipeService.getAll).mockResolvedValue(mockRecipes);
      vi.mocked(productService.delete).mockRejectedValue({
        response: { data: { detail: 'Cannot delete product in use' } },
      });
      const user = userEvent.setup();

      renderProductsPage();

      const deleteButtons = await screen.findAllByText('common.delete');
      await user.click(deleteButtons[0]);

      await waitFor(() => {
        expect(alert).toHaveBeenCalledWith('Cannot delete product in use');
      });
    });
  });
});
