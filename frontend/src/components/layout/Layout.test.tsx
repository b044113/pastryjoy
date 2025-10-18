import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Layout } from './Layout';
import { AuthProvider } from '../../contexts/AuthContext';
import { authService } from '../../services/auth.service';

// Mock the auth service
vi.mock('../../services/auth.service', () => ({
  authService: {
    isAuthenticated: vi.fn(),
    getCurrentUser: vi.fn(),
    clearToken: vi.fn(),
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

describe('Layout', () => {
  const renderLayout = (children: React.ReactNode) => {
    return render(
      <BrowserRouter>
        <AuthProvider>
          <Layout>{children}</Layout>
        </AuthProvider>
      </BrowserRouter>
    );
  };

  it('renders children content', () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(false);

    renderLayout(<div>Test Content</div>);

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('renders Navbar component', () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(false);

    renderLayout(<div>Content</div>);

    // Navbar should contain the logo
    expect(screen.getByText('PastryJoy')).toBeInTheDocument();
  });

  it('renders children inside main element', () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(false);

    const { container } = renderLayout(<div data-testid="child-content">Test</div>);

    const mainElement = container.querySelector('main');
    expect(mainElement).toBeInTheDocument();
    expect(mainElement).toContainElement(screen.getByTestId('child-content'));
  });

  it('applies correct container classes', () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(false);

    const { container } = renderLayout(<div>Content</div>);

    const rootDiv = container.firstChild;
    expect(rootDiv).toHaveClass('min-h-screen', 'bg-gray-50');
  });

  it('renders multiple children', () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(false);

    renderLayout(
      <>
        <h1>Title</h1>
        <p>Paragraph</p>
        <button>Button</button>
      </>
    );

    expect(screen.getByText('Title')).toBeInTheDocument();
    expect(screen.getByText('Paragraph')).toBeInTheDocument();
    expect(screen.getByText('Button')).toBeInTheDocument();
  });
});
