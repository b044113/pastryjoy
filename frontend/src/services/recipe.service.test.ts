import { describe, it, expect, vi, beforeEach } from 'vitest';
import { recipeService } from './recipe.service';
import { apiClient } from './api';

vi.mock('./api', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

describe('recipeService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getAll', () => {
    it('fetches all recipes', async () => {
      const mockRecipes = [
        { id: '1', name: 'Bread', instructions: 'Mix and bake' },
        { id: '2', name: 'Cake', instructions: 'Bake at 180C' },
      ];

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockRecipes });

      const result = await recipeService.getAll();

      expect(apiClient.get).toHaveBeenCalledWith('/api/recipes/');
      expect(result).toEqual(mockRecipes);
    });
  });

  describe('getById', () => {
    it('fetches recipe by id', async () => {
      const mockRecipe = { id: '1', name: 'Bread', instructions: 'Mix and bake' };

      vi.mocked(apiClient.get).mockResolvedValue({ data: mockRecipe });

      const result = await recipeService.getById('1');

      expect(apiClient.get).toHaveBeenCalledWith('/api/recipes/1');
      expect(result).toEqual(mockRecipe);
    });
  });

  describe('create', () => {
    it('creates new recipe', async () => {
      const newRecipe = { name: 'Croissant', instructions: 'Laminate dough' };
      const createdRecipe = { id: '3', ...newRecipe };

      vi.mocked(apiClient.post).mockResolvedValue({ data: createdRecipe });

      const result = await recipeService.create(newRecipe);

      expect(apiClient.post).toHaveBeenCalledWith('/api/recipes/', newRecipe);
      expect(result).toEqual(createdRecipe);
    });
  });

  describe('update', () => {
    it('updates existing recipe', async () => {
      const updateData = { name: 'Sourdough Bread', instructions: 'Use starter' };
      const updatedRecipe = { id: '1', ...updateData };

      vi.mocked(apiClient.put).mockResolvedValue({ data: updatedRecipe });

      const result = await recipeService.update('1', updateData);

      expect(apiClient.put).toHaveBeenCalledWith('/api/recipes/1', updateData);
      expect(result).toEqual(updatedRecipe);
    });
  });

  describe('delete', () => {
    it('deletes recipe', async () => {
      vi.mocked(apiClient.delete).mockResolvedValue({ data: undefined });

      await recipeService.delete('1');

      expect(apiClient.delete).toHaveBeenCalledWith('/api/recipes/1');
    });
  });
});
