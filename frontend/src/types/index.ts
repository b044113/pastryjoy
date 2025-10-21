// Auth types
export interface UserSettings {
  preferred_language: 'en' | 'es';
}

export interface User {
  id: string;
  email: string;
  username: string;
  role: 'admin' | 'user';
  is_active: boolean;
  full_name: string | null;
  settings: UserSettings;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UpdateUserSettingsRequest {
  preferred_language: 'en' | 'es';
}

// Ingredient types
export interface Ingredient {
  id: string;
  name: string;
  unit: string;
  created_at: string;
  updated_at: string;
}

export interface IngredientCreate {
  name: string;
  unit: string;
}

export interface IngredientUpdate {
  name?: string;
  unit?: string;
}

// Recipe types
export interface RecipeIngredient {
  id: string;
  ingredient_id: string;
  ingredient_name: string | null;
  quantity: number;
}

export interface Recipe {
  id: string;
  name: string;
  instructions: string | null;
  ingredients: RecipeIngredient[];
  created_at: string;
  updated_at: string;
}

export interface RecipeCreate {
  name: string;
  instructions?: string;
  ingredients: {
    ingredient_id: string;
    quantity: number;
  }[];
}

export interface RecipeUpdate {
  name?: string;
  instructions?: string;
}

// Product types
export interface ProductRecipe {
  recipe_id: string;
  recipe_name: string | null;
  quantity: number;
}

export interface Product {
  id: string;
  name: string;
  image_url: string | null;
  fixed_costs: number;
  variable_costs_percentage: number;
  profit_margin_percentage: number;
  recipes: ProductRecipe[];
  created_at: string;
  updated_at: string;
}

export interface ProductCreate {
  name: string;
  image_url?: string;
  fixed_costs: number;
  variable_costs_percentage: number;
  profit_margin_percentage: number;
  recipes: {
    recipe_id: string;
    quantity: number;
  }[];
}

export interface ProductUpdate {
  name?: string;
  image_url?: string;
  fixed_costs?: number;
  variable_costs_percentage?: number;
  profit_margin_percentage?: number;
  recipes?: {
    recipe_id: string;
    quantity: number;
  }[];
}

// Order types
export interface OrderItem {
  id: string;
  product_id: string;
  product_name: string | null;
  quantity: number;
  unit_price: number;
  total: number;
}

export interface Order {
  id: string;
  customer_name: string;
  customer_email: string;
  status: 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled';
  notes: string;
  items: OrderItem[];
  total: number;
  created_at: string;
  updated_at: string;
}

export interface OrderCreate {
  customer_name: string;
  customer_email: string;
  notes?: string;
  items: {
    product_id: string;
    quantity: number;
    unit_price: number;
  }[];
}

export interface OrderUpdateStatus {
  status: 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled';
}

// API Error type
export interface ApiError {
  detail: string;
}
