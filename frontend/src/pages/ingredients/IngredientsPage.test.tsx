import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { IngredientsPage } from './IngredientsPage';
import { AuthProvider } from '../../contexts/AuthContext';
import { authService } from '../../services/auth.service';
import { ingredientService } from '../../services/ingredient.service';
import type { Ingredient } from '../../types';

// Mock services
vi.mock('../../services/auth.service', () => ({
  authService: {
    isAuthenticated: vi.fn(),
    getCurrentUser: vi.fn(),
    clearToken: vi.fn(),
  },
}));

vi.mock('../../services/ingredient.service', () => ({
  ingredientService: {
    getAll: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}));

// Mock window.confirm
global.confirm = vi.fn(() => true);
global.alert = vi.fn();

describe('IngredientsPage', () => {
  const mockAdmin = {
    id: '1',
    username: 'adminuser',
    email: 'admin@test.com',
    role: 'admin' as const,
  };

  const mockIngredients: Ingredient[] = [
    { id: '1', name: 'Flour', unit: 'kg' },
    { id: '2', name: 'Sugar', unit: 'kg' },
    { id: '3', name: 'Eggs', unit: 'unit' },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(authService.isAuthenticated).mockReturnValue(true);
    vi.mocked(authService.getCurrentUser).mockResolvedValue(mockAdmin);
  });

  const renderIngredientsPage = () => {
    return render(
      <BrowserRouter>
        <AuthProvider>
          <IngredientsPage />
        </AuthProvider>
      </BrowserRouter>
    );
  };

  describe('Loading State', () => {
    it('shows loading spinner while fetching ingredients', () => {
      vi.mocked(ingredientService.getAll).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      renderIngredientsPage();

      expect(screen.getByText(/loading/i)).toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('shows empty state when no ingredients exist', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue([]);

      renderIngredientsPage();

      expect(await screen.findByText('dashboard.noOrders')).toBeInTheDocument();
      expect(screen.getByText('🥚')).toBeInTheDocument();
    });

    it('shows add first ingredient button in empty state', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue([]);

      renderIngredientsPage();

      const createButtons = await screen.findAllByText('ingredients.createIngredient');
      expect(createButtons.length).toBeGreaterThan(0);
    });
  });

  describe('Ingredients List', () => {
    it('renders page heading and description', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue(mockIngredients);

      renderIngredientsPage();

      expect(await screen.findByText('ingredients.title')).toBeInTheDocument();
      expect(screen.getByText('dashboard.manageIngredients')).toBeInTheDocument();
    });

    it('renders all ingredients', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue(mockIngredients);

      renderIngredientsPage();

      expect(await screen.findByText('Flour')).toBeInTheDocument();
      expect(screen.getByText('Sugar')).toBeInTheDocument();
      expect(screen.getByText('Eggs')).toBeInTheDocument();
    });

    it('shows unit for each ingredient', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue(mockIngredients);

      renderIngredientsPage();

      // Wait for ingredients to load and verify unit values are displayed
      await screen.findByText('Flour');

      // In table structure, units are displayed as plain text in table cells
      const kgCells = screen.getAllByText('kg');
      const unitCells = screen.getAllByText('unit');
      expect(kgCells.length + unitCells.length).toBeGreaterThan(0);
    });

    it('renders edit and delete buttons for each ingredient', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue(mockIngredients);

      renderIngredientsPage();

      await waitFor(() => {
        // Buttons now use aria-label instead of text
        expect(screen.getAllByLabelText('ingredients.editIngredient')).toHaveLength(3);
        expect(screen.getAllByLabelText('ingredients.deleteIngredient')).toHaveLength(3);
      });
    });

    it('renders add ingredient button', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue(mockIngredients);

      renderIngredientsPage();

      expect(await screen.findByText(/ingredients.createIngredient/i)).toBeInTheDocument();
    });
  });

  describe('Create Ingredient', () => {
    it('opens modal when add ingredient button is clicked', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue(mockIngredients);
      const user = userEvent.setup();

      renderIngredientsPage();

      const addButton = await screen.findByText(/ingredients.createIngredient/i);
      await user.click(addButton);

      expect(screen.getByText('ingredients.createIngredient')).toBeInTheDocument();
    });

    it('creates new ingredient on form submit', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue(mockIngredients);
      vi.mocked(ingredientService.create).mockResolvedValue({
        id: '4',
        name: 'Butter',
        unit: 'kg',
      });
      const user = userEvent.setup();

      renderIngredientsPage();

      const addButton = await screen.findByText(/ingredients.createIngredient/i);
      await user.click(addButton);

      // Find input by placeholder or by querying all inputs
      const inputs = screen.getAllByRole('textbox');
      const nameInput = inputs[0]; // The first textbox should be the name input
      await user.clear(nameInput);
      await user.type(nameInput, 'Butter');

      const saveButton = screen.getByText('common.save');
      await user.click(saveButton);

      await waitFor(() => {
        expect(ingredientService.create).toHaveBeenCalledWith({
          name: 'Butter',
          unit: 'kg',
        });
      });
    });
  });

  describe('Edit Ingredient', () => {
    it('opens modal with ingredient data when edit is clicked', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue(mockIngredients);
      const user = userEvent.setup();

      renderIngredientsPage();

      const editButtons = await screen.findAllByLabelText('ingredients.editIngredient');
      await user.click(editButtons[0]);

      expect(screen.getByText('ingredients.editIngredient')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Flour')).toBeInTheDocument();
    });

    it('updates ingredient on form submit', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue(mockIngredients);
      vi.mocked(ingredientService.update).mockResolvedValue({
        id: '1',
        name: 'All-Purpose Flour',
        unit: 'kg',
      });
      const user = userEvent.setup();

      renderIngredientsPage();

      const editButtons = await screen.findAllByLabelText('ingredients.editIngredient');
      await user.click(editButtons[0]);

      const nameInput = screen.getByDisplayValue('Flour');
      await user.clear(nameInput);
      await user.type(nameInput, 'All-Purpose Flour');

      const saveButton = screen.getByText('common.save');
      await user.click(saveButton);

      await waitFor(() => {
        expect(ingredientService.update).toHaveBeenCalledWith('1', {
          name: 'All-Purpose Flour',
          unit: 'kg',
        });
      });
    });
  });

  describe('Delete Ingredient', () => {
    it('deletes ingredient when delete button is clicked and confirmed', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue(mockIngredients);
      vi.mocked(ingredientService.delete).mockResolvedValue(undefined);
      const user = userEvent.setup();

      renderIngredientsPage();

      const deleteButtons = await screen.findAllByLabelText('ingredients.deleteIngredient');
      await user.click(deleteButtons[0]);

      await waitFor(() => {
        expect(confirm).toHaveBeenCalledWith('ingredients.deleteConfirm');
        expect(ingredientService.delete).toHaveBeenCalledWith('1');
      });
    });

    it('does not delete ingredient when confirmation is cancelled', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue(mockIngredients);
      vi.mocked(confirm).mockReturnValueOnce(false);
      const user = userEvent.setup();

      renderIngredientsPage();

      const deleteButtons = await screen.findAllByLabelText('ingredients.deleteIngredient');
      await user.click(deleteButtons[0]);

      await waitFor(() => {
        expect(confirm).toHaveBeenCalled();
      });

      expect(ingredientService.delete).not.toHaveBeenCalled();
    });
  });

  describe('Modal Controls', () => {
    it('closes modal when cancel button is clicked', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue(mockIngredients);
      const user = userEvent.setup();

      renderIngredientsPage();

      const addButton = await screen.findByText(/ingredients.createIngredient/i);
      await user.click(addButton);

      // Modal should be open - find a unique element in the modal
      expect(screen.getByText('common.cancel')).toBeInTheDocument();

      const cancelButton = screen.getByText('common.cancel');
      await user.click(cancelButton);

      await waitFor(() => {
        // The cancel button should no longer be visible after clicking
        expect(screen.queryByText('common.cancel')).not.toBeInTheDocument();
      });
    });

    it('resets form when modal is closed and reopened', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue(mockIngredients);
      const user = userEvent.setup();

      renderIngredientsPage();

      const addButton = await screen.findByText(/ingredients.createIngredient/i);
      await user.click(addButton);

      const inputs = screen.getAllByRole('textbox');
      const nameInput = inputs[0];
      await user.type(nameInput, 'Test Ingredient');

      const cancelButton = screen.getByText('common.cancel');
      await user.click(cancelButton);

      await user.click(addButton);

      const newInputs = screen.getAllByRole('textbox');
      const newNameInput = newInputs[0];
      expect(newNameInput).toHaveValue('');
    });
  });

  describe('Error Handling', () => {
    it('shows error message when create fails', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue(mockIngredients);
      vi.mocked(ingredientService.create).mockRejectedValue({
        response: { data: { detail: 'Ingredient already exists' } },
      });
      const user = userEvent.setup();

      renderIngredientsPage();

      const addButton = await screen.findByText(/ingredients.createIngredient/i);
      await user.click(addButton);

      const inputs = screen.getAllByRole('textbox');
      const nameInput = inputs[0];
      await user.type(nameInput, 'Flour');

      const saveButton = screen.getByText('common.save');
      await user.click(saveButton);

      expect(await screen.findByText('Ingredient already exists')).toBeInTheDocument();
    });

    it('shows alert when delete fails', async () => {
      vi.mocked(ingredientService.getAll).mockResolvedValue(mockIngredients);
      vi.mocked(ingredientService.delete).mockRejectedValue({
        response: { data: { detail: 'Cannot delete ingredient in use' } },
      });
      const user = userEvent.setup();

      renderIngredientsPage();

      const deleteButtons = await screen.findAllByLabelText('ingredients.deleteIngredient');
      await user.click(deleteButtons[0]);

      await waitFor(() => {
        expect(alert).toHaveBeenCalledWith('Cannot delete ingredient in use');
      });
    });
  });
});
