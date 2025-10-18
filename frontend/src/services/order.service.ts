import { apiClient } from './api';
import type { Order, OrderCreate, OrderUpdateStatus } from '../types';

export const orderService = {
  async getAll(): Promise<Order[]> {
    const response = await apiClient.get<Order[]>('/api/orders/');
    return response.data;
  },

  async getById(id: string): Promise<Order> {
    const response = await apiClient.get<Order>(`/api/orders/${id}`);
    return response.data;
  },

  async create(data: OrderCreate): Promise<Order> {
    const response = await apiClient.post<Order>('/api/orders/', data);
    return response.data;
  },

  async updateStatus(id: string, data: OrderUpdateStatus): Promise<Order> {
    const response = await apiClient.patch<Order>(`/api/orders/${id}/status`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/orders/${id}`);
  },
};
