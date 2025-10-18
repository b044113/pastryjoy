import { apiClient } from './api';
import type { Product, ProductCreate, ProductUpdate } from '../types';

export const productService = {
  async getAll(): Promise<Product[]> {
    const response = await apiClient.get<Product[]>('/api/products/');
    return response.data;
  },

  async getById(id: string): Promise<Product> {
    const response = await apiClient.get<Product>(`/api/products/${id}`);
    return response.data;
  },

  async create(data: ProductCreate): Promise<Product> {
    const response = await apiClient.post<Product>('/api/products/', data);
    return response.data;
  },

  async update(id: string, data: ProductUpdate): Promise<Product> {
    const response = await apiClient.put<Product>(`/api/products/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/products/${id}`);
  },
};
