/**
 * Helper function to get translation keys for tests
 * This simulates the t() function behavior in tests
 */
export const t = (key: string, params?: Record<string, any>): string => {
  // For testing, we just return the key
  // In real implementation, this would look up the actual translation
  if (params) {
    let result = key;
    Object.entries(params).forEach(([paramKey, value]) => {
      result = result.replace(`{{${paramKey}}}`, String(value));
    });
    return result;
  }
  return key;
};

/**
 * Common translation keys used across components
 */
export const translations = {
  common: {
    cancel: 'common.cancel',
    save: 'common.save',
    delete: 'common.delete',
    edit: 'common.edit',
    create: 'common.create',
    search: 'common.search',
    loading: 'common.loading',
    actions: 'common.actions',
    name: 'common.name',
    description: 'common.description',
    quantity: 'common.quantity',
    price: 'common.price',
    total: 'common.total',
    status: 'common.status',
  },
  nav: {
    dashboard: 'nav.dashboard',
    ingredients: 'nav.ingredients',
    recipes: 'nav.recipes',
    products: 'nav.products',
    orders: 'nav.orders',
    logout: 'nav.logout',
  },
  dashboard: {
    title: 'dashboard.title',
    welcome: 'dashboard.welcome',
    manageIngredients: 'dashboard.manageIngredients',
    manageRecipes: 'dashboard.manageRecipes',
    manageProducts: 'dashboard.manageProducts',
  },
  ingredients: {
    title: 'ingredients.title',
    createIngredient: 'ingredients.createIngredient',
    editIngredient: 'ingredients.editIngredient',
    deleteIngredient: 'ingredients.deleteIngredient',
    unit: 'ingredients.unit',
  },
  recipes: {
    title: 'recipes.title',
    createRecipe: 'recipes.createRecipe',
    editRecipe: 'recipes.editRecipe',
    instructions: 'recipes.instructions',
    ingredients: 'recipes.ingredients',
  },
  products: {
    title: 'products.title',
    createProduct: 'products.createProduct',
    editProduct: 'products.editProduct',
    subtitle: 'products.subtitle',
  },
  orders: {
    title: 'orders.title',
    createOrder: 'orders.createOrder',
    manageAllOrders: 'orders.manageAllOrders',
    viewYourOrders: 'orders.viewYourOrders',
  },
};
