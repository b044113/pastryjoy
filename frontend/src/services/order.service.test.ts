import { describe, it, expect, vi, beforeEach } from 'vitest';
import { orderService } from './order.service';
import { apiClient } from './api';

vi.mock('./api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('orderService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getAll', () => {
    it('fetches all orders', async () => {
      const mockOrders = [
        { id: '1', customer_name: 'John Doe', status: 'pending' },
        { id: '2', customer_name: 'Jane Smith', status: 'completed' },
      ];

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockOrders });

      const result = await orderService.getAll();

      expect(apiClient.get).toHaveBeenCalledWith('/api/orders/');
      expect(result).toEqual(mockOrders);
    });
  });

  describe('getById', () => {
    it('fetches order by id', async () => {
      const mockOrder = { id: '1', customer_name: 'John Doe', status: 'pending' };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockOrder });

      const result = await orderService.getById('1');

      expect(apiClient.get).toHaveBeenCalledWith('/api/orders/1');
      expect(result).toEqual(mockOrder);
    });
  });

  describe('create', () => {
    it('creates new order', async () => {
      const newOrder = { customer_name: 'Bob Wilson', items: [] };
      const createdOrder = { id: '3', ...newOrder, status: 'pending' };

      vi.mocked(apiClient.post).mockResolvedValue({ data: createdOrder });

      const result = await orderService.create(newOrder);

      expect(apiClient.post).toHaveBeenCalledWith('/api/orders/', newOrder);
      expect(result).toEqual(createdOrder);
    });
  });

  describe('updateStatus', () => {
    it('updates order status', async () => {
      const statusData = { status: 'completed' };
      const updatedOrder = { id: '1', customer_name: 'John Doe', status: 'completed' };

      vi.mocked(apiClient.patch).mockResolvedValue({ data: updatedOrder });

      const result = await orderService.updateStatus('1', statusData);

      expect(apiClient.patch).toHaveBeenCalledWith('/api/orders/1/status', statusData);
      expect(result).toEqual(updatedOrder);
    });
  });

  describe('delete', () => {
    it('deletes order', async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({ data: undefined });

      await orderService.delete('1');

      expect(apiClient.delete).toHaveBeenCalledWith('/api/orders/1');
    });
  });
});
