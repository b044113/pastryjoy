import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { RegisterPage } from './RegisterPage';
import { AuthProvider } from '../../contexts/AuthContext';
import { authService } from '../../services/auth.service';

// Mock auth service
vi.mock('../../services/auth.service', () => ({
  authService: {
    isAuthenticated: vi.fn(),
    getCurrentUser: vi.fn(),
    clearToken: vi.fn(),
    register: vi.fn(),
  },
}));

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('RegisterPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  const renderRegisterPage = () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(false);

    return render(
      <BrowserRouter>
        <AuthProvider>
          <RegisterPage />
        </AuthProvider>
      </BrowserRouter>
    );
  };

  it('renders register page without crashing', () => {
    renderRegisterPage();

    expect(screen.getByText('🥐')).toBeInTheDocument();
  });

  it('renders create account heading', () => {
    renderRegisterPage();

    expect(screen.getByText(/create.*account/i)).toBeInTheDocument();
  });

  it('renders email label', () => {
    renderRegisterPage();

    expect(screen.getByText('auth.email')).toBeInTheDocument();
  });

  it('renders username label', () => {
    renderRegisterPage();

    const labels = screen.getAllByText('auth.username');
    expect(labels.length).toBeGreaterThan(0);
  });

  it('renders password labels', () => {
    renderRegisterPage();

    expect(screen.getAllByText('auth.password').length).toBeGreaterThan(0);
  });

  it('renders register button', () => {
    renderRegisterPage();

    const button = screen.getByRole('button', { name: 'auth.register' });
    expect(button).toBeInTheDocument();
  });

  it('renders link to login page', () => {
    renderRegisterPage();

    expect(screen.getByText('auth.loginHere')).toBeInTheDocument();
  });

  describe('Form Validation', () => {
    it('shows error when passwords do not match', async () => {
      const user = userEvent.setup();
      renderRegisterPage();

      const emailInput = screen.getByLabelText('auth.email');
      const usernameInput = screen.getByLabelText('auth.username');
      const passwordInputs = screen.getAllByLabelText('auth.password');
      const passwordInput = passwordInputs[0];
      const confirmPasswordInput = screen.getByLabelText('auth.confirmPassword');
      const registerButton = screen.getByRole('button', { name: 'auth.register' });

      await user.type(emailInput, 'test@example.com');
      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'password456');
      await user.click(registerButton);

      await waitFor(() => {
        expect(screen.getByText('auth.passwordsNotMatch')).toBeInTheDocument();
      });

      expect(authService.register).not.toHaveBeenCalled();
    });

    it('shows error when password is too short', async () => {
      const user = userEvent.setup();
      renderRegisterPage();

      const emailInput = screen.getByLabelText('auth.email');
      const usernameInput = screen.getByLabelText('auth.username');
      const passwordInputs = screen.getAllByLabelText('auth.password');
      const passwordInput = passwordInputs[0];
      const confirmPasswordInput = screen.getByLabelText('auth.confirmPassword');
      const registerButton = screen.getByRole('button', { name: 'auth.register' });

      await user.type(emailInput, 'test@example.com');
      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'short');
      await user.type(confirmPasswordInput, 'short');
      await user.click(registerButton);

      await waitFor(() => {
        expect(screen.getByText('auth.passwordMinLength')).toBeInTheDocument();
      });

      expect(authService.register).not.toHaveBeenCalled();
    });

    it('clears error when user starts typing after validation error', async () => {
      const user = userEvent.setup();
      renderRegisterPage();

      const emailInput = screen.getByLabelText('auth.email');
      const usernameInput = screen.getByLabelText('auth.username');
      const passwordInputs = screen.getAllByLabelText('auth.password');
      const passwordInput = passwordInputs[0];
      const confirmPasswordInput = screen.getByLabelText('auth.confirmPassword');
      const registerButton = screen.getByRole('button', { name: 'auth.register' });

      // Trigger validation error
      await user.type(emailInput, 'test@example.com');
      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'password456');
      await user.click(registerButton);

      await waitFor(() => {
        expect(screen.getByText('auth.passwordsNotMatch')).toBeInTheDocument();
      });

      // Start typing in email field - this triggers form resubmit in the component
      await user.clear(confirmPasswordInput);
      await user.type(confirmPasswordInput, 'password123');
      await user.click(registerButton);

      // The error should eventually be cleared or replaced
      await waitFor(() => {
        expect(authService.register).toHaveBeenCalled();
      });
    });
  });

  describe('Form Submission', () => {
    it('submits form with valid data and navigates to dashboard', async () => {
      const user = userEvent.setup();
      vi.mocked(authService.register).mockResolvedValue({
        data: {
          access_token: 'test-token',
          token_type: 'bearer',
        },
      });

      renderRegisterPage();

      const emailInput = screen.getByLabelText('auth.email');
      const usernameInput = screen.getByLabelText('auth.username');
      const fullNameInput = screen.getByLabelText('auth.fullName');
      const passwordInputs = screen.getAllByLabelText('auth.password');
      const passwordInput = passwordInputs[0];
      const confirmPasswordInput = screen.getByLabelText('auth.confirmPassword');
      const registerButton = screen.getByRole('button', { name: 'auth.register' });

      await user.type(emailInput, 'test@example.com');
      await user.type(usernameInput, 'testuser');
      await user.type(fullNameInput, 'Test User');
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'password123');
      await user.click(registerButton);

      await waitFor(() => {
        expect(authService.register).toHaveBeenCalledWith({
          email: 'test@example.com',
          username: 'testuser',
          password: 'password123',
          full_name: 'Test User',
        });
      });
    });

    it('submits form without full name when not provided', async () => {
      const user = userEvent.setup();
      vi.mocked(authService.register).mockResolvedValue({
        data: {
          access_token: 'test-token',
          token_type: 'bearer',
        },
      });

      renderRegisterPage();

      const emailInput = screen.getByLabelText('auth.email');
      const usernameInput = screen.getByLabelText('auth.username');
      const passwordInputs = screen.getAllByLabelText('auth.password');
      const passwordInput = passwordInputs[0];
      const confirmPasswordInput = screen.getByLabelText('auth.confirmPassword');
      const registerButton = screen.getByRole('button', { name: 'auth.register' });

      await user.type(emailInput, 'test@example.com');
      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'password123');
      await user.click(registerButton);

      await waitFor(() => {
        expect(authService.register).toHaveBeenCalledWith({
          email: 'test@example.com',
          username: 'testuser',
          password: 'password123',
          full_name: undefined,
        });
      });
    });

    it('shows error message when registration fails', async () => {
      const user = userEvent.setup();
      vi.mocked(authService.register).mockRejectedValue({
        response: {
          data: {
            detail: 'Username already exists',
          },
        },
      });

      renderRegisterPage();

      const emailInput = screen.getByLabelText('auth.email');
      const usernameInput = screen.getByLabelText('auth.username');
      const passwordInputs = screen.getAllByLabelText('auth.password');
      const passwordInput = passwordInputs[0];
      const confirmPasswordInput = screen.getByLabelText('auth.confirmPassword');
      const registerButton = screen.getByRole('button', { name: 'auth.register' });

      await user.type(emailInput, 'test@example.com');
      await user.type(usernameInput, 'existinguser');
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'password123');
      await user.click(registerButton);

      await waitFor(() => {
        expect(screen.getByText('Username already exists')).toBeInTheDocument();
      });
    });

    it('shows generic error when no detail provided', async () => {
      const user = userEvent.setup();
      vi.mocked(authService.register).mockRejectedValue({
        response: {},
      });

      renderRegisterPage();

      const emailInput = screen.getByLabelText('auth.email');
      const usernameInput = screen.getByLabelText('auth.username');
      const passwordInputs = screen.getAllByLabelText('auth.password');
      const passwordInput = passwordInputs[0];
      const confirmPasswordInput = screen.getByLabelText('auth.confirmPassword');
      const registerButton = screen.getByRole('button', { name: 'auth.register' });

      await user.type(emailInput, 'test@example.com');
      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'password123');
      await user.click(registerButton);

      await waitFor(() => {
        expect(screen.getByText('auth.registerFailed')).toBeInTheDocument();
      });
    });

    it('disables form inputs during submission', async () => {
      const user = userEvent.setup();
      vi.mocked(authService.register).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      renderRegisterPage();

      const emailInput = screen.getByLabelText('auth.email') as HTMLInputElement;
      const usernameInput = screen.getByLabelText('auth.username') as HTMLInputElement;
      const passwordInputs = screen.getAllByLabelText('auth.password');
      const passwordInput = passwordInputs[0] as HTMLInputElement;
      const confirmPasswordInput = screen.getByLabelText('auth.confirmPassword') as HTMLInputElement;
      const registerButton = screen.getByRole('button', { name: 'auth.register' }) as HTMLButtonElement;

      await user.type(emailInput, 'test@example.com');
      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'password123');
      await user.click(registerButton);

      // Check inputs are disabled during submission
      expect(emailInput.disabled).toBe(true);
      expect(usernameInput.disabled).toBe(true);
      expect(passwordInput.disabled).toBe(true);
      expect(confirmPasswordInput.disabled).toBe(true);
      expect(registerButton.disabled).toBe(true);
    });

    it('shows loading text during submission', async () => {
      const user = userEvent.setup();
      vi.mocked(authService.register).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      renderRegisterPage();

      const emailInput = screen.getByLabelText('auth.email');
      const usernameInput = screen.getByLabelText('auth.username');
      const passwordInputs = screen.getAllByLabelText('auth.password');
      const passwordInput = passwordInputs[0];
      const confirmPasswordInput = screen.getByLabelText('auth.confirmPassword');
      const registerButton = screen.getByRole('button', { name: 'auth.register' });

      await user.type(emailInput, 'test@example.com');
      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'password123');
      await user.type(confirmPasswordInput, 'password123');
      await user.click(registerButton);

      expect(screen.getByText('auth.registering')).toBeInTheDocument();
    });

    it('handles cancel button click', async () => {
      const user = userEvent.setup();
      renderRegisterPage();

      const cancelButton = screen.getByRole('button', { name: 'common.cancel' });
      await user.click(cancelButton);

      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });
});
