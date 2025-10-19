import React, { useState, useEffect } from 'react';
import { Layout } from '../../components/layout/Layout';
import { Button } from '../../components/common/Button';
import { Card } from '../../components/common/Card';
import { Modal } from '../../components/common/Modal';
import { Input } from '../../components/common/Input';
import { Loading } from '../../components/common/Loading';
import { productService } from '../../services/product.service';
import { recipeService } from '../../services/recipe.service';
import type { Product, Recipe } from '../../types';

export const ProductsPage: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    image_url: '',
    fixed_costs: '',
    variable_costs_percentage: '',
    profit_margin_percentage: '',
    recipes: [] as { recipe_id: string; quantity: number }[],
  });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // For adding recipes to product
  const [selectedRecipeId, setSelectedRecipeId] = useState('');
  const [recipeQuantity, setRecipeQuantity] = useState('1');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [productsData, recipesData] = await Promise.all([
        productService.getAll(),
        recipeService.getAll(),
      ]);
      setProducts(productsData);
      setRecipes(recipesData);
    } catch (err: any) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (product?: Product) => {
    if (product) {
      setEditingProduct(product);
      setFormData({
        name: product.name,
        image_url: product.image_url || '',
        fixed_costs: product.fixed_costs.toString(),
        variable_costs_percentage: product.variable_costs_percentage.toString(),
        profit_margin_percentage: product.profit_margin_percentage.toString(),
        recipes: product.recipes.map((rec) => ({
          recipe_id: rec.recipe_id,
          quantity: Number(rec.quantity),
        })),
      });
    } else {
      setEditingProduct(null);
      setFormData({
        name: '',
        image_url: '',
        fixed_costs: '0',
        variable_costs_percentage: '0',
        profit_margin_percentage: '0',
        recipes: [],
      });
    }
    setSelectedRecipeId('');
    setRecipeQuantity('1');
    setError('');
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingProduct(null);
    setFormData({
      name: '',
      image_url: '',
      fixed_costs: '0',
      variable_costs_percentage: '0',
      profit_margin_percentage: '0',
      recipes: [],
    });
    setSelectedRecipeId('');
    setRecipeQuantity('1');
    setError('');
  };

  const handleAddRecipe = () => {
    if (!selectedRecipeId || !recipeQuantity) {
      setError('Please select a recipe and enter quantity');
      return;
    }

    const quantity = parseFloat(recipeQuantity);
    if (quantity <= 0) {
      setError('Quantity must be greater than 0');
      return;
    }

    // Check if recipe already added
    if (formData.recipes.some((rec) => rec.recipe_id === selectedRecipeId)) {
      setError('Recipe already added');
      return;
    }

    setFormData({
      ...formData,
      recipes: [...formData.recipes, { recipe_id: selectedRecipeId, quantity }],
    });
    setSelectedRecipeId('');
    setRecipeQuantity('1');
    setError('');
  };

  const handleRemoveRecipe = (recipeId: string) => {
    setFormData({
      ...formData,
      recipes: formData.recipes.filter((rec) => rec.recipe_id !== recipeId),
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const fixedCosts = parseFloat(formData.fixed_costs);
    const variableCosts = parseFloat(formData.variable_costs_percentage);
    const profitMargin = parseFloat(formData.profit_margin_percentage);

    if (isNaN(fixedCosts) || fixedCosts < 0) {
      setError('Fixed costs must be a valid positive number');
      return;
    }

    if (isNaN(variableCosts) || variableCosts < 0 || variableCosts > 100) {
      setError('Variable costs percentage must be between 0 and 100');
      return;
    }

    if (isNaN(profitMargin) || profitMargin < 0) {
      setError('Profit margin percentage must be a valid positive number');
      return;
    }

    setSubmitting(true);

    try {
      if (editingProduct) {
        await productService.update(editingProduct.id, {
          name: formData.name,
          image_url: formData.image_url || undefined,
          fixed_costs: fixedCosts,
          variable_costs_percentage: variableCosts,
          profit_margin_percentage: profitMargin,
          recipes: formData.recipes,
        });
      } else {
        await productService.create({
          name: formData.name,
          image_url: formData.image_url || undefined,
          fixed_costs: fixedCosts,
          variable_costs_percentage: variableCosts,
          profit_margin_percentage: profitMargin,
          recipes: formData.recipes,
        });
      }
      await loadData();
      handleCloseModal();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save product');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this product?')) return;

    try {
      await productService.delete(id);
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete product');
    }
  };

  const getRecipeName = (recipeId: string): string => {
    const recipe = recipes.find((rec) => rec.id === recipeId);
    return recipe?.name || 'Unknown';
  };

  if (loading) return <Loading fullScreen />;

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Products</h1>
            <p className="text-gray-600 mt-2">Manage your product catalog</p>
          </div>
          <Button onClick={() => handleOpenModal()}>+ Add Product</Button>
        </div>

        {products.length === 0 ? (
          <Card>
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🎂</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No products yet
              </h3>
              <p className="text-gray-600 mb-6">
                Get started by adding your first product
              </p>
              <Button onClick={() => handleOpenModal()}>Add First Product</Button>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {products.map((product) => (
              <Card key={product.id} className="hover:shadow-lg transition-shadow">
                <div className="mb-4">
                  {product.image_url && (
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="w-full h-40 object-cover rounded-lg mb-3"
                    />
                  )}
                  <h3 className="text-lg font-semibold text-gray-900">
                    {product.name}
                  </h3>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Fixed Costs:</span>
                    <span className="font-medium">${product.fixed_costs}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Variable Costs:</span>
                    <span className="font-medium">
                      {product.variable_costs_percentage}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Profit Margin:</span>
                    <span className="font-medium">
                      {product.profit_margin_percentage}%
                    </span>
                  </div>
                  <div className="pt-2 border-t">
                    <span className="text-gray-600">
                      Recipes: {product.recipes.length}
                    </span>
                  </div>
                </div>

                <div className="flex gap-2 mt-4">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => handleOpenModal(product)}
                    className="flex-1"
                  >
                    Edit
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDelete(product.id)}
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
          title={editingProduct ? 'Edit Product' : 'Add Product'}
          size="lg"
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
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              required
              disabled={submitting}
            />

            <Input
              label="Image URL"
              type="url"
              value={formData.image_url}
              onChange={(e) =>
                setFormData({ ...formData, image_url: e.target.value })
              }
              disabled={submitting}
              helperText="Optional: URL to product image"
            />

            <div className="grid grid-cols-3 gap-4">
              <Input
                label="Fixed Costs ($)"
                type="number"
                step="0.01"
                value={formData.fixed_costs}
                onChange={(e) =>
                  setFormData({ ...formData, fixed_costs: e.target.value })
                }
                required
                disabled={submitting}
              />

              <Input
                label="Variable Costs (%)"
                type="number"
                step="0.01"
                value={formData.variable_costs_percentage}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    variable_costs_percentage: e.target.value,
                  })
                }
                required
                disabled={submitting}
              />

              <Input
                label="Profit Margin (%)"
                type="number"
                step="0.01"
                value={formData.profit_margin_percentage}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    profit_margin_percentage: e.target.value,
                  })
                }
                required
                disabled={submitting}
              />
            </div>

            {/* Add Recipes Section */}
            <div className="border-t pt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-3">Recipes</h4>

              <div className="flex gap-2 mb-3">
                <select
                  value={selectedRecipeId}
                  onChange={(e) => setSelectedRecipeId(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  disabled={submitting}
                >
                  <option value="">Select recipe...</option>
                  {recipes.map((rec) => (
                    <option key={rec.id} value={rec.id}>
                      {rec.name}
                    </option>
                  ))}
                </select>

                <Input
                  type="number"
                  step="0.001"
                  placeholder="Quantity"
                  value={recipeQuantity}
                  onChange={(e) => setRecipeQuantity(e.target.value)}
                  disabled={submitting}
                  className="w-32"
                />

                <Button
                  type="button"
                  variant="secondary"
                  onClick={handleAddRecipe}
                  disabled={submitting}
                >
                  Add
                </Button>
              </div>

              {/* List of added recipes */}
              {formData.recipes.length > 0 && (
                <div className="space-y-2">
                  {formData.recipes.map((rec) => (
                    <div
                      key={rec.recipe_id}
                      className="flex items-center justify-between bg-gray-50 px-3 py-2 rounded-lg"
                    >
                      <span className="text-sm">
                        {getRecipeName(rec.recipe_id)} - Qty: {rec.quantity}
                      </span>
                      <button
                        type="button"
                        onClick={() => handleRemoveRecipe(rec.recipe_id)}
                        className="text-red-600 hover:text-red-700 text-sm"
                        disabled={submitting}
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {formData.recipes.length === 0 && (
                <p className="text-sm text-gray-500 italic">
                  No recipes added yet
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
