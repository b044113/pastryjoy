import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ingredientService } from './ingredient.service';
import { apiClient } from './api';

vi.mock('./api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('ingredientService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getAll', () => {
    it('fetches all ingredients', async () => {
      const mockIngredients = [
        { id: '1', name: 'Flour', unit: 'kg' },
        { id: '2', name: 'Sugar', unit: 'kg' },
      ];

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockIngredients });

      const result = await ingredientService.getAll();

      expect(apiClient.get).toHaveBeenCalledWith('/api/ingredients/');
      expect(result).toEqual(mockIngredients);
    });

    it('handles errors when fetching ingredients', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Network error'));

      await expect(ingredientService.getAll()).rejects.toThrow('Network error');
    });
  });

  describe('getById', () => {
    it('fetches ingredient by id', async () => {
      const mockIngredient = { id: '1', name: 'Flour', unit: 'kg' };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockIngredient });

      const result = await ingredientService.getById('1');

      expect(apiClient.get).toHaveBeenCalledWith('/api/ingredients/1');
      expect(result).toEqual(mockIngredient);
    });

    it('handles errors when ingredient not found', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Not found'));

      await expect(ingredientService.getById('999')).rejects.toThrow('Not found');
    });
  });

  describe('create', () => {
    it('creates new ingredient', async () => {
      const newIngredient = { name: 'Salt', unit: 'kg' };
      const createdIngredient = { id: '3', ...newIngredient };

      vi.mocked(apiClient.post).mockResolvedValue({ data: createdIngredient });

      const result = await ingredientService.create(newIngredient);

      expect(apiClient.post).toHaveBeenCalledWith('/api/ingredients/', newIngredient);
      expect(result).toEqual(createdIngredient);
    });

    it('handles errors when creating ingredient', async () => {
      vi.mocked(apiClient.post).mockRejectedValue(new Error('Validation error'));

      await expect(ingredientService.create({ name: '', unit: '' })).rejects.toThrow('Validation error');
    });
  });

  describe('update', () => {
    it('updates existing ingredient', async () => {
      const updateData = { name: 'Bread Flour', unit: 'kg' };
      const updatedIngredient = { id: '1', ...updateData };

      vi.mocked(apiClient.put).mockResolvedValue({ data: updatedIngredient });

      const result = await ingredientService.update('1', updateData);

      expect(apiClient.put).toHaveBeenCalledWith('/api/ingredients/1', updateData);
      expect(result).toEqual(updatedIngredient);
    });

    it('handles errors when updating ingredient', async () => {
      vi.mocked(apiClient.put).mockRejectedValue(new Error('Update failed'));

      await expect(ingredientService.update('1', { name: 'Test' })).rejects.toThrow('Update failed');
    });
  });

  describe('delete', () => {
    it('deletes ingredient', async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({ data: undefined });

      await ingredientService.delete('1');

      expect(apiClient.delete).toHaveBeenCalledWith('/api/ingredients/1');
    });

    it('handles errors when deleting ingredient', async () => {
      vi.mocked(apiClient.delete).mockRejectedValue(new Error('Delete failed'));

      await expect(ingredientService.delete('1')).rejects.toThrow('Delete failed');
    });
  });
});
