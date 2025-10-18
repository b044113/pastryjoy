import { apiClient } from './api';
import type { Ingredient, IngredientCreate, IngredientUpdate } from '../types';

export const ingredientService = {
  async getAll(): Promise<Ingredient[]> {
    const response = await apiClient.get<Ingredient[]>('/api/ingredients/');
    return response.data;
  },

  async getById(id: string): Promise<Ingredient> {
    const response = await apiClient.get<Ingredient>(`/api/ingredients/${id}`);
    return response.data;
  },

  async create(data: IngredientCreate): Promise<Ingredient> {
    const response = await apiClient.post<Ingredient>('/api/ingredients/', data);
    return response.data;
  },

  async update(id: string, data: IngredientUpdate): Promise<Ingredient> {
    const response = await apiClient.put<Ingredient>(`/api/ingredients/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/ingredients/${id}`);
  },
};
