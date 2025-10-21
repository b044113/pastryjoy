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

  // For editing ingredient quantities
  const [editingIngredientId, setEditingIngredientId] = useState<string | null>(null);
  const [editingQuantity, setEditingQuantity] = useState('');

  // For creating new ingredients
  const [isIngredientModalOpen, setIsIngredientModalOpen] = useState(false);
  const [ingredientFormData, setIngredientFormData] = useState({ name: '', unit: 'kg' });
  const [ingredientError, setIngredientError] = useState('');
  const [ingredientSubmitting, setIngredientSubmitting] = useState(false);

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
    // Cancel editing if we're removing the ingredient being edited
    if (editingIngredientId === ingredientId) {
      setEditingIngredientId(null);
      setEditingQuantity('');
    }
  };

  const handleStartEditIngredient = (ingredientId: string, quantity: number) => {
    setEditingIngredientId(ingredientId);
    setEditingQuantity(quantity.toString());
  };

  const handleSaveEditIngredient = (ingredientId: string) => {
    const quantity = parseFloat(editingQuantity);
    if (quantity <= 0 || isNaN(quantity)) {
      setError(t('recipes.quantityPositive'));
      return;
    }

    setFormData({
      ...formData,
      ingredients: formData.ingredients.map((ing) =>
        ing.ingredient_id === ingredientId
          ? { ...ing, quantity }
          : ing
      ),
    });
    setEditingIngredientId(null);
    setEditingQuantity('');
    setError('');
  };

  const handleCancelEditIngredient = () => {
    setEditingIngredientId(null);
    setEditingQuantity('');
  };

  const handleOpenIngredientModal = () => {
    setIngredientFormData({ name: '', unit: 'kg' });
    setIngredientError('');
    setIsIngredientModalOpen(true);
  };

  const handleCloseIngredientModal = () => {
    setIsIngredientModalOpen(false);
    setIngredientFormData({ name: '', unit: 'kg' });
    setIngredientError('');
  };

  const handleIngredientSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIngredientError('');
    setIngredientSubmitting(true);

    try {
      const newIngredient = await ingredientService.create(ingredientFormData);
      // Refresh ingredients list
      const ingredientsData = await ingredientService.getAll();
      setIngredients(ingredientsData);
      // Auto-select the newly created ingredient
      setSelectedIngredientId(newIngredient.id);
      handleCloseIngredientModal();
    } catch (err: any) {
      setIngredientError(err.response?.data?.detail || t('errors.generic'));
    } finally {
      setIngredientSubmitting(false);
    }
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
          ingredients: formData.ingredients,
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

  const formatQuantity = (quantity: number): string => {
    // Convertir a número por si viene como string
    const num = Number(quantity);
    // Si es un número entero, mostrar sin decimales
    if (Number.isInteger(num)) {
      return num.toString();
    }
    // Si tiene decimales, mostrar hasta 3 decimales y eliminar ceros finales
    return parseFloat(num.toFixed(3)).toString();
  };

  const getUnitSymbol = (unit: string): string => {
    const unitMap: Record<string, string> = {
      'kg': 'kg',
      'g': 'g',
      'l': 'L',
      'ml': 'mL',
      'unit': 'u',
      'tbsp': 'cdta',
      'tsp': 'cdita',
      'cup': 'taza',
    };
    return unitMap[unit] || unit;
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 items-start">
            {recipes.map((recipe) => (
              <Card key={recipe.id} className="hover:shadow-lg transition-shadow flex flex-col">
                <div className="flex-1 min-h-0">
                  <div className="mb-4 h-20">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {recipe.name}
                    </h3>
                    {recipe.instructions && (
                      <p className="text-sm text-gray-600 mt-2 line-clamp-2">
                        {recipe.instructions}
                      </p>
                    )}
                  </div>

                  <div className="h-28">
                    <p className="text-sm font-medium text-gray-700 mb-2">
                      {t('recipes.ingredients')}: {recipe.ingredients.length}
                    </p>
                    {recipe.ingredients.length > 0 && (
                      <ul className="text-sm text-gray-600 space-y-1">
                        {recipe.ingredients.slice(0, 3).map((ing) => {
                          const unit = getIngredientUnit(ing.ingredient_id);
                          const formattedQuantity = formatQuantity(ing.quantity);
                          const unitSymbol = getUnitSymbol(unit);
                          return (
                            <li key={ing.id}>
                              • {ing.ingredient_name || t('common.unknown')} ({formattedQuantity} {unitSymbol})
                            </li>
                          );
                        })}
                        {recipe.ingredients.length > 3 && (
                          <li className="text-gray-500 italic">
                            +{recipe.ingredients.length - 3} {t('common.more')}
                          </li>
                        )}
                      </ul>
                    )}
                  </div>
                </div>

                <div className="flex gap-2 mt-4 pt-4 border-t border-gray-100">
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
          size="xl"
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
          <form onSubmit={handleSubmit} className="h-[500px] overflow-hidden">
            <div className="grid grid-cols-2 gap-6 h-full">
              {/* Left Column: Name and Instructions */}
              <div className="flex flex-col">
                <div className="mb-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('common.name')} <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                    disabled={submitting}
                  />
                </div>

                <div className="flex-1 flex flex-col">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {t('recipes.instructions')}
                  </label>
                  <textarea
                    value={formData.instructions}
                    onChange={(e) =>
                      setFormData({ ...formData, instructions: e.target.value })
                    }
                    className="flex-1 w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                    disabled={submitting}
                  />
                </div>
              </div>

              {/* Right Column: Ingredients */}
              <div className="flex flex-col h-full">
                {/* Header */}
                <div className="mb-1">
                  <h4 className="text-sm font-medium text-gray-700 mb-1">
                    {t('recipes.ingredients')}
                  </h4>
                </div>

                {/* Add ingredient controls */}
                <div className="flex gap-2 mb-3">
                  <select
                    value={selectedIngredientId}
                    onChange={(e) => setSelectedIngredientId(e.target.value)}
                    className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
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
                    className="w-24"
                  />

                  <Button
                    type="button"
                    onClick={handleAddIngredient}
                    disabled={submitting}
                  >
                    {t('common.add')}
                  </Button>
                </div>

                {/* Ingredients Table with scrollbar */}
                <div className="flex-1 overflow-y-auto border border-gray-200 rounded-lg mb-3">
                  {formData.ingredients.length > 0 ? (
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50 sticky top-0">
                        <tr>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            {t('common.name')}
                          </th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                            {t('common.quantity')}
                          </th>
                          <th className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                            {t('common.actions')}
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {formData.ingredients.map((ing) => (
                          <tr key={ing.ingredient_id} className="hover:bg-gray-50">
                            <td className="px-3 py-2 text-sm text-gray-900">
                              {getIngredientName(ing.ingredient_id)}
                            </td>
                            <td className="px-3 py-2 text-sm text-gray-600">
                              {editingIngredientId === ing.ingredient_id ? (
                                <div className="flex items-center gap-1">
                                  <input
                                    type="number"
                                    step="0.001"
                                    value={editingQuantity}
                                    onChange={(e) => setEditingQuantity(e.target.value)}
                                    className="w-20 px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500"
                                    autoFocus
                                  />
                                  <span className="text-xs text-gray-500">
                                    {getIngredientUnit(ing.ingredient_id)}
                                  </span>
                                </div>
                              ) : (
                                `${ing.quantity} ${getIngredientUnit(ing.ingredient_id)}`
                              )}
                            </td>
                            <td className="px-3 py-2 text-right">
                              <div className="flex justify-end gap-1">
                                {editingIngredientId === ing.ingredient_id ? (
                                  <>
                                    <button
                                      type="button"
                                      onClick={() => handleSaveEditIngredient(ing.ingredient_id)}
                                      className="text-green-600 hover:text-green-900 p-1 rounded hover:bg-green-50"
                                      title={t('common.save')}
                                      disabled={submitting}
                                    >
                                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                      </svg>
                                    </button>
                                    <button
                                      type="button"
                                      onClick={handleCancelEditIngredient}
                                      className="text-gray-600 hover:text-gray-900 p-1 rounded hover:bg-gray-50"
                                      title={t('common.cancel')}
                                      disabled={submitting}
                                    >
                                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                      </svg>
                                    </button>
                                  </>
                                ) : (
                                  <>
                                    <button
                                      type="button"
                                      onClick={() => handleStartEditIngredient(ing.ingredient_id, ing.quantity)}
                                      className="text-blue-600 hover:text-blue-900 p-1 rounded hover:bg-blue-50"
                                      title={t('common.edit')}
                                      disabled={submitting}
                                    >
                                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                                      </svg>
                                    </button>
                                    <button
                                      type="button"
                                      onClick={() => handleRemoveIngredient(ing.ingredient_id)}
                                      className="text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-50"
                                      title={t('common.delete')}
                                      disabled={submitting}
                                    >
                                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                                      </svg>
                                    </button>
                                  </>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <p className="text-sm text-gray-500 italic">
                        {t('recipes.noIngredients')}
                      </p>
                    </div>
                  )}
                </div>

                {/* New ingredient button */}
                <Button
                  type="button"
                  variant="secondary"
                  onClick={handleOpenIngredientModal}
                  disabled={submitting}
                  className="w-full"
                >
                  {t('common.new')} {t('ingredients.ingredient')}
                </Button>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mt-4">
                {error}
              </div>
            )}
          </form>
        </Modal>

        {/* Create Ingredient Modal */}
        <Modal
          isOpen={isIngredientModalOpen}
          onClose={handleCloseIngredientModal}
          title={t('ingredients.createIngredient')}
          footer={
            <>
              <Button variant="secondary" onClick={handleCloseIngredientModal}>
                {t('common.cancel')}
              </Button>
              <Button onClick={handleIngredientSubmit} disabled={ingredientSubmitting}>
                {ingredientSubmitting ? t('common.loading') : t('common.save')}
              </Button>
            </>
          }
        >
          <form onSubmit={handleIngredientSubmit} className="space-y-4">
            <Input
              label={t('common.name')}
              value={ingredientFormData.name}
              onChange={(e) => setIngredientFormData({ ...ingredientFormData, name: e.target.value })}
              required
              disabled={ingredientSubmitting}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {t('ingredients.unit')} <span className="text-red-500">*</span>
              </label>
              <select
                value={ingredientFormData.unit}
                onChange={(e) => setIngredientFormData({ ...ingredientFormData, unit: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                required
                disabled={ingredientSubmitting}
              >
                <option value="kg">{t('ingredients.units.kg')}</option>
                <option value="g">{t('ingredients.units.g')}</option>
                <option value="l">{t('ingredients.units.l')}</option>
                <option value="ml">{t('ingredients.units.ml')}</option>
                <option value="unit">{t('ingredients.units.unit')}</option>
                <option value="tbsp">{t('ingredients.units.tbsp')}</option>
                <option value="tsp">{t('ingredients.units.tsp')}</option>
                <option value="cup">{t('ingredients.units.cup')}</option>
              </select>
            </div>

            {ingredientError && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {ingredientError}
              </div>
            )}
          </form>
        </Modal>
      </div>
    </Layout>
  );
};
