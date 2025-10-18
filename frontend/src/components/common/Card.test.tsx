import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Card } from './Card';

describe('Card', () => {
  it('renders children content', () => {
    render(
      <Card>
        <p>Card content</p>
      </Card>
    );
    expect(screen.getByText('Card content')).toBeInTheDocument();
  });

  it('renders with title', () => {
    render(
      <Card title="Card Title">
        <p>Content</p>
      </Card>
    );
    expect(screen.getByText('Card Title')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('renders without title', () => {
    render(
      <Card>
        <p>Content without title</p>
      </Card>
    );
    expect(screen.getByText('Content without title')).toBeInTheDocument();
    expect(screen.queryByRole('heading')).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <Card className="custom-card">
        <p>Content</p>
      </Card>
    );
    const card = container.firstChild;
    expect(card).toHaveClass('custom-card');
  });

  it('has default styling classes', () => {
    const { container } = render(
      <Card>
        <p>Content</p>
      </Card>
    );
    const card = container.firstChild;
    expect(card).toHaveClass('bg-white', 'rounded-lg', 'shadow-md');
  });

  it('renders title with proper styling', () => {
    render(
      <Card title="Styled Title">
        <p>Content</p>
      </Card>
    );
    const title = screen.getByText('Styled Title');
    expect(title).toHaveClass('text-lg', 'font-semibold', 'text-gray-900');
  });

  it('renders complex children', () => {
    render(
      <Card title="Complex Card">
        <div>
          <h4>Subtitle</h4>
          <p>Paragraph 1</p>
          <p>Paragraph 2</p>
        </div>
      </Card>
    );
    expect(screen.getByText('Complex Card')).toBeInTheDocument();
    expect(screen.getByText('Subtitle')).toBeInTheDocument();
    expect(screen.getByText('Paragraph 1')).toBeInTheDocument();
    expect(screen.getByText('Paragraph 2')).toBeInTheDocument();
  });
});
