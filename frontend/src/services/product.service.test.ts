import { describe, it, expect, vi, beforeEach } from 'vitest';
import { productService } from './product.service';
import { apiClient } from './api';

vi.mock('./api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('productService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getAll', () => {
    it('fetches all products', async () => {
      const mockProducts = [
        { id: '1', name: 'Baguette' },
        { id: '2', name: 'Croissant' },
      ];

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockProducts });

      const result = await productService.getAll();

      expect(apiClient.get).toHaveBeenCalledWith('/api/products/');
      expect(result).toEqual(mockProducts);
    });
  });

  describe('getById', () => {
    it('fetches product by id', async () => {
      const mockProduct = { id: '1', name: 'Baguette' };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockProduct });

      const result = await productService.getById('1');

      expect(apiClient.get).toHaveBeenCalledWith('/api/products/1');
      expect(result).toEqual(mockProduct);
    });
  });

  describe('create', () => {
    it('creates new product', async () => {
      const newProduct = { name: 'Pain au Chocolat' };
      const createdProduct = { id: '3', ...newProduct };

      vi.mocked(apiClient.post).mockResolvedValue({ data: createdProduct });

      const result = await productService.create(newProduct);

      expect(apiClient.post).toHaveBeenCalledWith('/api/products/', newProduct);
      expect(result).toEqual(createdProduct);
    });
  });

  describe('update', () => {
    it('updates existing product', async () => {
      const updateData = { name: 'Sourdough Baguette' };
      const updatedProduct = { id: '1', ...updateData };

      vi.mocked(apiClient.put).mockResolvedValue({ data: updatedProduct });

      const result = await productService.update('1', updateData);

      expect(apiClient.put).toHaveBeenCalledWith('/api/products/1', updateData);
      expect(result).toEqual(updatedProduct);
    });
  });

  describe('delete', () => {
    it('deletes product', async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({ data: undefined });

      await productService.delete('1');

      expect(apiClient.delete).toHaveBeenCalledWith('/api/products/1');
    });
  });
});
