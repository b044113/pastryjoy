import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
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
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

describe('RegisterPage', () => {
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

    expect(screen.getByText(/pastry/i)).toBeInTheDocument();
  });

  it('renders create account heading', () => {
    renderRegisterPage();

    expect(screen.getByText(/create.*account/i)).toBeInTheDocument();
  });

  it('renders email label', () => {
    renderRegisterPage();

    expect(screen.getByText(/email/i)).toBeInTheDocument();
  });

  it('renders username label', () => {
    renderRegisterPage();

    expect(screen.getByText(/username/i)).toBeInTheDocument();
  });

  it('renders password labels', () => {
    renderRegisterPage();

    expect(screen.getAllByText(/password/i).length).toBeGreaterThan(0);
  });

  it('renders register button', () => {
    renderRegisterPage();

    const button = screen.getByRole('button', { name: /register/i });
    expect(button).toBeInTheDocument();
  });

  it('renders link to login page', () => {
    renderRegisterPage();

    expect(screen.getByText(/login here/i)).toBeInTheDocument();
  });
});
