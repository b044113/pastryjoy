import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Loading } from './Loading';

describe('Loading', () => {
  it('renders loading spinner', () => {
    const { container } = render(<Loading />);
    const spinner = container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('renders inline loading by default', () => {
    const { container } = render(<Loading />);
    const wrapper = container.firstChild;
    expect(wrapper).toHaveClass('flex', 'justify-center', 'items-center', 'p-8');
  });

  it('renders fullscreen loading when fullScreen is true', () => {
    render(<Loading fullScreen />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('has fixed positioning when fullScreen', () => {
    const { container } = render(<Loading fullScreen />);
    const wrapper = container.firstChild;
    expect(wrapper).toHaveClass('fixed', 'inset-0');
  });

  it('does not show Loading text when not fullScreen', () => {
    render(<Loading />);
    expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
  });

  it('has larger spinner in fullScreen mode', () => {
    const { container } = render(<Loading fullScreen />);
    const spinner = container.querySelector('.animate-spin');
    expect(spinner).toHaveClass('w-12', 'h-12');
  });

  it('has smaller spinner in inline mode', () => {
    const { container } = render(<Loading />);
    const spinner = container.querySelector('.animate-spin');
    expect(spinner).toHaveClass('w-8', 'h-8');
  });
});
