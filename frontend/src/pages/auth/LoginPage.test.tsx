import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
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
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

describe('LoginPage', () => {
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

    expect(screen.getByText(/welcome/i)).toBeInTheDocument();
  });

  it('renders username label', () => {
    renderLoginPage();

    expect(screen.getByText(/username/i)).toBeInTheDocument();
  });

  it('renders password label', () => {
    renderLoginPage();

    expect(screen.getByText(/password/i)).toBeInTheDocument();
  });

  it('renders login button', () => {
    renderLoginPage();

    const button = screen.getByRole('button', { name: /login/i });
    expect(button).toBeInTheDocument();
  });

  it('renders link to register page', () => {
    renderLoginPage();

    expect(screen.getByText(/register here/i)).toBeInTheDocument();
  });
});
