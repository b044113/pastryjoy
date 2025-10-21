import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { LoginPage } from './LoginPage';
import { AuthProvider } from '../../contexts/AuthContext';
import { authService } from '../../services/auth.service';

// Mock auth service
vi.mock('../../services/auth.service', () => ({
  authService: {
    isAuthenticated: vi.fn(),
    getCurrentUser: vi.fn(),
    clearToken: vi.fn(),
    login: vi.fn(),
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

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockNavigate.mockClear();
  });

  const renderLoginPage = () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(false);

    return render(
      <BrowserRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </BrowserRouter>
    );
  };

  it('renders login page without crashing', () => {
    renderLoginPage();

    expect(screen.getByText(/pastry/i)).toBeInTheDocument();
  });

  it('renders welcome message', () => {
    renderLoginPage();

    expect(screen.getByText('auth.welcomeBack')).toBeInTheDocument();
  });

  it('renders username label', () => {
    renderLoginPage();

    expect(screen.getByText('auth.username')).toBeInTheDocument();
  });

  it('renders password label', () => {
    renderLoginPage();

    expect(screen.getByText('auth.password')).toBeInTheDocument();
  });

  it('renders login button', () => {
    renderLoginPage();

    const button = screen.getByRole('button', { name: /login/i });
    expect(button).toBeInTheDocument();
  });

  it('renders link to register page', () => {
    renderLoginPage();

    expect(screen.getByText('auth.registerHere')).toBeInTheDocument();
  });

  describe('Form Submission', () => {
    it('submits form with valid credentials and navigates to dashboard', async () => {
      const user = userEvent.setup();
      vi.mocked(authService.login).mockResolvedValue({
        data: {
          access_token: 'test-token',
          token_type: 'bearer',
        },
      });

      renderLoginPage();

      const usernameInput = screen.getByLabelText('auth.username');
      const passwordInput = screen.getByLabelText('auth.password');
      const loginButton = screen.getByRole('button', { name: 'auth.login' });

      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'password123');
      await user.click(loginButton);

      await waitFor(() => {
        expect(authService.login).toHaveBeenCalledWith({
          username: 'testuser',
          password: 'password123',
        });
      });
    });

    it('shows error message when login fails', async () => {
      const user = userEvent.setup();
      vi.mocked(authService.login).mockRejectedValue({
        response: {
          data: {
            detail: 'Invalid credentials',
          },
        },
      });

      renderLoginPage();

      const usernameInput = screen.getByLabelText('auth.username');
      const passwordInput = screen.getByLabelText('auth.password');
      const loginButton = screen.getByRole('button', { name: 'auth.login' });

      await user.type(usernameInput, 'wronguser');
      await user.type(passwordInput, 'wrongpass');
      await user.click(loginButton);

      await waitFor(() => {
        expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
      });
    });

    it('shows generic error when no detail provided', async () => {
      const user = userEvent.setup();
      vi.mocked(authService.login).mockRejectedValue({
        response: {},
      });

      renderLoginPage();

      const usernameInput = screen.getByLabelText('auth.username');
      const passwordInput = screen.getByLabelText('auth.password');
      const loginButton = screen.getByRole('button', { name: 'auth.login' });

      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'password123');
      await user.click(loginButton);

      await waitFor(() => {
        expect(screen.getByText('auth.loginFailed')).toBeInTheDocument();
      });
    });

    it('disables form inputs during submission', async () => {
      const user = userEvent.setup();
      vi.mocked(authService.login).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      renderLoginPage();

      const usernameInput = screen.getByLabelText('auth.username') as HTMLInputElement;
      const passwordInput = screen.getByLabelText('auth.password') as HTMLInputElement;
      const loginButton = screen.getByRole('button', { name: 'auth.login' }) as HTMLButtonElement;

      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'password123');
      await user.click(loginButton);

      // Check inputs are disabled during submission
      expect(usernameInput.disabled).toBe(true);
      expect(passwordInput.disabled).toBe(true);
      expect(loginButton.disabled).toBe(true);
    });

    it('shows loading text during submission', async () => {
      const user = userEvent.setup();
      vi.mocked(authService.login).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

      renderLoginPage();

      const usernameInput = screen.getByLabelText('auth.username');
      const passwordInput = screen.getByLabelText('auth.password');
      const loginButton = screen.getByRole('button', { name: 'auth.login' });

      await user.type(usernameInput, 'testuser');
      await user.type(passwordInput, 'password123');
      await user.click(loginButton);

      expect(screen.getByText('auth.loggingIn')).toBeInTheDocument();
    });

    it('handles cancel button click', async () => {
      const user = userEvent.setup();
      renderLoginPage();

      const cancelButton = screen.getByRole('button', { name: 'common.cancel' });
      await user.click(cancelButton);

      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });
});
