import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Layout } from '../../components/layout/Layout';
import { Button } from '../../components/common/Button';
import { Card } from '../../components/common/Card';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Loading } from '../../components/common/Loading';
import { recipeService } from '../../services/recipe.service';
import { ingredientService } from '../../services/ingredient.service';
import type { Recipe, Ingredient } from '../../types';

export const RecipesPage: React.FC = () => {
  const { t } = useTranslation();
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRecipe, setEditingRecipe] = useState<Recipe | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    instructions: '',
    ingredients: [] as { ingredient_id: string; quantity: number }[],
  });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // For adding ingredients to recipe
  const [selectedIngredientId, setSelectedIngredientId] = useState('');
  const [ingredientQuantity, setIngredientQuantity] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [recipesData, ingredientsData] = await Promise.all([
        recipeService.getAll(),
        ingredientService.getAll(),
      ]);
      setRecipes(recipesData);
      setIngredients(ingredientsData);
    } catch (err: any) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (recipe?: Recipe) => {
    if (recipe) {
      setEditingRecipe(recipe);
      setFormData({
        name: recipe.name,
        instructions: recipe.instructions || '',
        ingredients: recipe.ingredients.map((ing) => ({
          ingredient_id: ing.ingredient_id,
          quantity: Number(ing.quantity),
        })),
      });
    } else {
      setEditingRecipe(null);
      setFormData({ name: '', instructions: '', ingredients: [] });
    }
    setSelectedIngredientId('');
    setIngredientQuantity('');
    setError('');
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingRecipe(null);
    setFormData({ name: '', instructions: '', ingredients: [] });
    setSelectedIngredientId('');
    setIngredientQuantity('');
    setError('');
  };

  const handleAddIngredient = () => {
    if (!selectedIngredientId || !ingredientQuantity) {
      setError(`${t('recipes.ingredientRequired')} ${t('common.and')} ${t('recipes.quantityRequired')}`);
      return;
    }

    const quantity = parseFloat(ingredientQuantity);
    if (quantity <= 0) {
      setError(t('recipes.quantityPositive'));
      return;
    }

    // Check if ingredient already added
    if (formData.ingredients.some((ing) => ing.ingredient_id === selectedIngredientId)) {
      setError(t('errors.validationError'));
      return;
    }

    setFormData({
      ...formData,
      ingredients: [
        ...formData.ingredients,
        { ingredient_id: selectedIngredientId, quantity },
      ],
    });
    setSelectedIngredientId('');
    setIngredientQuantity('');
    setError('');
  };

  const handleRemoveIngredient = (ingredientId: string) => {
    setFormData({
      ...formData,
      ingredients: formData.ingredients.filter(
        (ing) => ing.ingredient_id !== ingredientId
      ),
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.ingredients.length === 0) {
      setError(t('recipes.ingredientsRequired'));
      return;
    }

    setSubmitting(true);

    try {
      if (editingRecipe) {
        await recipeService.update(editingRecipe.id, {
          name: formData.name,
          instructions: formData.instructions || undefined,
        });
      } else {
        await recipeService.create({
          name: formData.name,
          instructions: formData.instructions || undefined,
          ingredients: formData.ingredients,
        });
      }
      await loadData();
      handleCloseModal();
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errors.generic'));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm(t('recipes.deleteConfirm'))) return;

    try {
      await recipeService.delete(id);
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || t('errors.generic'));
    }
  };

  const getIngredientName = (ingredientId: string): string => {
    const ingredient = ingredients.find((ing) => ing.id === ingredientId);
    return ingredient?.name || t('common.unknown');
  };

  const getIngredientUnit = (ingredientId: string): string => {
    const ingredient = ingredients.find((ing) => ing.id === ingredientId);
    return ingredient?.unit || '';
  };

  if (loading) return <Loading fullScreen />;

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{t('recipes.title')}</h1>
            <p className="text-gray-600 mt-2">{t('dashboard.manageRecipes')}</p>
          </div>
          <Button onClick={() => handleOpenModal()}>+ {t('recipes.createRecipe')}</Button>
        </div>

        {recipes.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">📖</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {t('recipes.noIngredients')}
              </h3>
              <p className="text-gray-600 mb-6">
                {t('recipes.createRecipe')}
              </p>
              <Button onClick={() => handleOpenModal()}>{t('recipes.createRecipe')}</Button>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recipes.map((recipe) => (
              <Card key={recipe.id} className="hover:shadow-lg transition-shadow">
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {recipe.name}
                  </h3>
                  {recipe.instructions && (
                    <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                      {recipe.instructions}
                    </p>
                  )}
                </div>

                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    {t('recipes.ingredients')}: {recipe.ingredients.length}
                  </p>
                  {recipe.ingredients.length > 0 && (
                    <ul className="text-sm text-gray-600 space-y-1">
                      {recipe.ingredients.slice(0, 3).map((ing) => (
                        <li key={ing.id}>
                          • {ing.ingredient_name || t('common.unknown')} ({ing.quantity})
                        </li>
                      ))}
                      {recipe.ingredients.length > 3 && (
                        <li className="text-gray-500 italic">
                          +{recipe.ingredients.length - 3} {t('common.more')}
                        </li>
                      )}
                    </ul>
                  )}
                </div>

                <div className="flex gap-2 mt-4">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => handleOpenModal(recipe)}
                    className="flex-1"
                  >
                    {t('common.edit')}
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDelete(recipe.id)}
                    className="flex-1"
                  >
                    {t('common.delete')}
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
          title={editingRecipe ? t('recipes.editRecipe') : t('recipes.createRecipe')}
          size="lg"
          footer={
            <>
              <Button variant="secondary" onClick={handleCloseModal}>
                {t('common.cancel')}
              </Button>
              <Button onClick={handleSubmit} disabled={submitting}>
                {submitting ? t('common.loading') : t('common.save')}
              </Button>
            </>
          }
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label={t('common.name')}
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              required
              disabled={submitting}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('recipes.instructions')}
              </label>
              <textarea
                value={formData.instructions}
                onChange={(e) =>
                  setFormData({ ...formData, instructions: e.target.value })
                }
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                rows={4}
                disabled={submitting}
              />
            </div>

            {/* Add Ingredients Section */}
            <div className="border-t pt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-3">
                {t('recipes.ingredients')}
              </h4>

              <div className="flex gap-2 mb-3">
                <select
                  value={selectedIngredientId}
                  onChange={(e) => setSelectedIngredientId(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  disabled={submitting}
                >
                  <option value="">{t('recipes.selectIngredient')}</option>
                  {ingredients.map((ing) => (
                    <option key={ing.id} value={ing.id}>
                      {ing.name} ({ing.unit})
                    </option>
                  ))}
                </select>

                <Input
                  type="number"
                  step="0.001"
                  placeholder={t('common.quantity')}
                  value={ingredientQuantity}
                  onChange={(e) => setIngredientQuantity(e.target.value)}
                  disabled={submitting}
                  className="w-32"
                />

                <Button
                  type="button"
                  variant="secondary"
                  onClick={handleAddIngredient}
                  disabled={submitting}
                >
                  {t('recipes.addIngredient')}
                </Button>
              </div>

              {/* List of added ingredients */}
              {formData.ingredients.length > 0 && (
                <div className="space-y-2">
                  {formData.ingredients.map((ing) => (
                    <div
                      key={ing.ingredient_id}
                      className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded-lg"
                    >
                      <span className="text-sm">
                        {getIngredientName(ing.ingredient_id)} - {ing.quantity}{' '}
                        {getIngredientUnit(ing.ingredient_id)}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleRemoveIngredient(ing.ingredient_id)}
                        className="text-red-600 hover:text-red-700 text-sm"
                        disabled={submitting}
                      >
                        {t('common.delete')}
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {formData.ingredients.length === 0 && (
                <p className="text-sm text-gray-500 italic">
                  {t('recipes.noIngredients')}
                </p>
              )}
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
