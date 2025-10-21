import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { OrdersPage } from './OrdersPage';
import { AuthProvider } from '../../contexts/AuthContext';
import { authService } from '../../services/auth.service';
import { orderService } from '../../services/order.service';
import { productService } from '../../services/product.service';
import type { Order, Product } from '../../types';

// Mock services
vi.mock('../../services/auth.service', () => ({
  authService: {
    isAuthenticated: vi.fn(),
    getCurrentUser: vi.fn(),
    clearToken: vi.fn(),
  },
}));

vi.mock('../../services/order.service', () => ({
  orderService: {
    getAll: vi.fn(),
    create: vi.fn(),
    updateStatus: vi.fn(),
    delete: vi.fn(),
  },
}));

vi.mock('../../services/product.service', () => ({
  productService: {
    getAll: vi.fn(),
  },
}));

global.confirm = vi.fn(() => true);
global.alert = vi.fn();

describe('OrdersPage', () => {
  const mockAdmin = {
    id: '1',
    username: 'adminuser',
    email: 'admin@test.com',
    role: 'admin' as const,
  };

  const mockUser = {
    id: '2',
    username: 'regularuser',
    email: 'user@test.com',
    role: 'user' as const,
  };

  const mockProducts: Product[] = [
    {
      id: '1',
      name: 'Bread',
      image_url: 'bread.jpg',
      fixed_costs: 2,
      variable_costs_percentage: 20,
      profit_margin_percentage: 30,
      recipes: [],
      created_at: '2025-01-01T10:00:00Z',
      updated_at: '2025-01-01T10:00:00Z',
    },
  ];

  const mockOrders: Order[] = [
    {
      id: '1',
      customer_name: 'John Doe',
      customer_email: 'john@example.com',
      status: 'pending',
      notes: 'Deliver at 9am',
      items: [
        { id: '1', product_id: '1', product_name: 'Bread', quantity: 2, unit_price: 5.0, total: 10.0 },
      ],
      total: 10.0,
      created_at: '2025-01-01T10:00:00Z',
      updated_at: '2025-01-01T10:00:00Z',
    },
    {
      id: '2',
      customer_name: 'Jane Smith',
      customer_email: 'jane@example.com',
      status: 'completed',
      notes: '',
      items: [],
      total: 0.0,
      created_at: '2025-01-02T10:00:00Z',
      updated_at: '2025-01-02T10:00:00Z',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  const renderOrdersPage = (isAdmin = true) => {
    const user = isAdmin ? mockAdmin : mockUser;
    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(user);

    return render(
      <BrowserRouter>
        <AuthProvider>
          <OrdersPage />
        </AuthProvider>
      </BrowserRouter>
    );
  };

  describe('Loading State', () => {
    it('shows loading spinner while fetching data', () => {
      vi.mocked(orderService.getAll).mockImplementation(
        () => new Promise(() => {})
      );
      vi.mocked(productService.getAll).mockImplementation(
        () => new Promise(() => {})
      );

      renderOrdersPage();

      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('shows empty state when no orders exist', async () => {
      vi.mocked(orderService.getAll).mockResolvedValue([]);
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);

      renderOrdersPage();

      expect(await screen.findByText('orders.noOrdersYet')).toBeInTheDocument();
    });
  });

  describe('Orders List', () => {
    it('renders page heading', async () => {
      vi.mocked(orderService.getAll).mockResolvedValue(mockOrders);
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);

      renderOrdersPage();

      expect(await screen.findByRole('heading', { name: 'orders.title' })).toBeInTheDocument();
    });

    it('renders all orders', async () => {
      vi.mocked(orderService.getAll).mockResolvedValue(mockOrders);
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);

      renderOrdersPage();

      expect(await screen.findByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });

    it('renders add order button', async () => {
      vi.mocked(orderService.getAll).mockResolvedValue(mockOrders);
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);

      renderOrdersPage();

      expect(await screen.findByText('orders.createOrder', { exact: false })).toBeInTheDocument();
    });

    it('displays order status', async () => {
      vi.mocked(orderService.getAll).mockResolvedValue(mockOrders);
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);

      renderOrdersPage();

      await waitFor(() => {
        expect(screen.getByText('orders.statuses.pending')).toBeInTheDocument();
        expect(screen.getByText('orders.statuses.completed')).toBeInTheDocument();
      });
    });
  });

  describe('Create Order', () => {
    it('opens modal when create order button is clicked', async () => {
      vi.mocked(orderService.getAll).mockResolvedValue(mockOrders);
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);
      const user = userEvent.setup();

      renderOrdersPage();

      const addButton = await screen.findByText('orders.createOrder', { exact: false });
      await user.click(addButton);

      expect(screen.getByRole('heading', { name: 'orders.createOrder' })).toBeInTheDocument();
    });
  });

  describe('Delete Order', () => {
    it('deletes order when delete button is clicked and confirmed', async () => {
      vi.mocked(orderService.getAll).mockResolvedValue(mockOrders);
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);
      vi.mocked(orderService.delete).mockResolvedValue(undefined);
      const user = userEvent.setup();

      renderOrdersPage();

      const deleteButtons = await screen.findAllByText('common.delete');
      await user.click(deleteButtons[0]);

      await waitFor(() => {
        expect(confirm).toHaveBeenCalledWith('orders.deleteConfirm');
        expect(orderService.delete).toHaveBeenCalledWith('1');
      });
    });

    it('does not delete order when confirmation is cancelled', async () => {
      vi.mocked(orderService.getAll).mockResolvedValue(mockOrders);
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);
      vi.mocked(confirm).mockReturnValueOnce(false);
      const user = userEvent.setup();

      renderOrdersPage();

      const deleteButtons = await screen.findAllByText('common.delete');
      await user.click(deleteButtons[0]);

      await waitFor(() => {
        expect(confirm).toHaveBeenCalled();
      });

      expect(orderService.delete).not.toHaveBeenCalled();
    });
  });

  describe('Admin Features', () => {
    it('shows update status button for admin users', async () => {
      vi.mocked(orderService.getAll).mockResolvedValue(mockOrders);
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);

      renderOrdersPage(true);

      expect(await screen.findAllByText('orders.updateStatus')).toHaveLength(2);
    });
  });

  describe('Modal Controls', () => {
    it('closes modal when cancel button is clicked', async () => {
      vi.mocked(orderService.getAll).mockResolvedValue(mockOrders);
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);
      const user = userEvent.setup();

      renderOrdersPage();

      const addButton = await screen.findByText('orders.createOrder', { exact: false });
      await user.click(addButton);

      expect(screen.getByRole('heading', { name: 'orders.createOrder' })).toBeInTheDocument();

      const cancelButton = screen.getByText('common.cancel');
      await user.click(cancelButton);

      await waitFor(() => {
        expect(screen.queryByRole('heading', { name: 'orders.createOrder' })).not.toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('shows alert when delete fails', async () => {
      vi.mocked(orderService.getAll).mockResolvedValue(mockOrders);
      vi.mocked(productService.getAll).mockResolvedValue(mockProducts);
      vi.mocked(orderService.delete).mockRejectedValue({
        response: { data: { detail: 'Cannot delete order' } },
      });
      const user = userEvent.setup();

      renderOrdersPage();

      const deleteButtons = await screen.findAllByText('common.delete');
      await user.click(deleteButtons[0]);

      await waitFor(() => {
        expect(alert).toHaveBeenCalledWith('Cannot delete order');
      });
    });
  });
});
