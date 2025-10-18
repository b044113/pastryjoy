import React, { useState, useEffect } from 'react';
import { Layout } from '../../components/layout/Layout';
import { Button } from '../../components/common/Button';
import { Card } from '../../components/common/Card';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Loading } from '../../components/common/Loading';
import { ingredientService } from '../../services/ingredient.service';
import type { Ingredient } from '../../types';

export const IngredientsPage: React.FC = () => {
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingIngredient, setEditingIngredient] = useState<Ingredient | null>(null);
  const [formData, setFormData] = useState({ name: '', unit: 'kg' });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadIngredients();
  }, []);

  const loadIngredients = async () => {
    try {
      const data = await ingredientService.getAll();
      setIngredients(data);
    } catch (err: any) {
      console.error('Failed to load ingredients:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (ingredient?: Ingredient) => {
    if (ingredient) {
      setEditingIngredient(ingredient);
      setFormData({ name: ingredient.name, unit: ingredient.unit });
    } else {
      setEditingIngredient(null);
      setFormData({ name: '', unit: 'kg' });
    }
    setError('');
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingIngredient(null);
    setFormData({ name: '', unit: 'kg' });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      if (editingIngredient) {
        await ingredientService.update(editingIngredient.id, formData);
      } else {
        await ingredientService.create(formData);
      }
      await loadIngredients();
      handleCloseModal();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save ingredient');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this ingredient?')) return;

    try {
      await ingredientService.delete(id);
      await loadIngredients();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete ingredient');
    }
  };

  if (loading) return <Loading fullScreen />;

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Ingredients</h1>
            <p className="text-gray-600 mt-2">Manage your bakery ingredients</p>
          </div>
          <Button onClick={() => handleOpenModal()}>
            + Add Ingredient
          </Button>
        </div>

        {ingredients.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🥚</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No ingredients yet</h3>
              <p className="text-gray-600 mb-6">Get started by adding your first ingredient</p>
              <Button onClick={() => handleOpenModal()}>Add First Ingredient</Button>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {ingredients.map((ingredient) => (
              <Card key={ingredient.id} className="hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{ingredient.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">Unit: {ingredient.unit}</p>
                  </div>
                </div>
                <div className="flex gap-2 mt-4">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => handleOpenModal(ingredient)}
                    className="flex-1"
                  >
                    Edit
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDelete(ingredient.id)}
                    className="flex-1"
                  >
                    Delete
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Create/Edit Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          title={editingIngredient ? 'Edit Ingredient' : 'Add Ingredient'}
          footer={
            <>
              <Button variant="secondary" onClick={handleCloseModal}>
                Cancel
              </Button>
              <Button onClick={handleSubmit} disabled={submitting}>
                {submitting ? 'Saving...' : 'Save'}
              </Button>
            </>
          }
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              disabled={submitting}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Unit <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.unit}
                onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
                disabled={submitting}
              >
                <option value="kg">Kilogram (kg)</option>
                <option value="g">Gram (g)</option>
                <option value="l">Liter (l)</option>
                <option value="ml">Milliliter (ml)</option>
                <option value="unit">Unit</option>
                <option value="tbsp">Tablespoon (tbsp)</option>
                <option value="tsp">Teaspoon (tsp)</option>
                <option value="cup">Cup</option>
              </select>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}
          </form>
        </Modal>
      </div>
    </Layout>
  );
};
