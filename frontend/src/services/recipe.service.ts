import { apiClient } from './api';
import type { Recipe, RecipeCreate, RecipeUpdate } from '../types';

export const recipeService = {
  async getAll(): Promise<Recipe[]> {
    const response = await apiClient.get<Recipe[]>('/api/recipes/');
    return response.data;
  },

  async getById(id: string): Promise<Recipe> {
    const response = await apiClient.get<Recipe>(`/api/recipes/${id}`);
    return response.data;
  },

  async create(data: RecipeCreate): Promise<Recipe> {
    const response = await apiClient.post<Recipe>('/api/recipes/', data);
    return response.data;
  },

  async update(id: string, data: RecipeUpdate): Promise<Recipe> {
    const response = await apiClient.put<Recipe>(`/api/recipes/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/recipes/${id}`);
  },
};
