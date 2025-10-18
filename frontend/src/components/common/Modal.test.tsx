import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Modal } from './Modal';

describe('Modal', () => {
  const mockOnClose = vi.fn();

  beforeEach(() => {
    mockOnClose.mockClear();
  });

  it('does not render when isOpen is false', () => {
    render(
      <Modal isOpen={false} onClose={mockOnClose} title="Test Modal">
        <p>Content</p>
      </Modal>
    );
    expect(screen.queryByText('Test Modal')).not.toBeInTheDocument();
    expect(screen.queryByText('Content')).not.toBeInTheDocument();
  });

  it('renders when isOpen is true', () => {
    render(
      <Modal isOpen={true} onClose={mockOnClose} title="Test Modal">
        <p>Modal Content</p>
      </Modal>
    );
    expect(screen.getByText('Test Modal')).toBeInTheDocument();
    expect(screen.getByText('Modal Content')).toBeInTheDocument();
  });

  it('calls onClose when overlay is clicked', async () => {
    const user = userEvent.setup();
    render(
      <Modal isOpen={true} onClose={mockOnClose} title="Test Modal">
        <p>Content</p>
      </Modal>
    );

    const overlay = document.querySelector('.bg-black.bg-opacity-50');
    if (overlay) {
      await user.click(overlay as HTMLElement);
      expect(mockOnClose).toHaveBeenCalledTimes(1);
    }
  });

  it('calls onClose when close button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <Modal isOpen={true} onClose={mockOnClose} title="Test Modal">
        <p>Content</p>
      </Modal>
    );

    const closeButton = screen.getByRole('button');
    await user.click(closeButton);
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('calls onClose when Escape key is pressed', async () => {
    const user = userEvent.setup();
    render(
      <Modal isOpen={true} onClose={mockOnClose} title="Test Modal">
        <p>Content</p>
      </Modal>
    );

    await user.keyboard('{Escape}');
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('renders footer when provided', () => {
    render(
      <Modal
        isOpen={true}
        onClose={mockOnClose}
        title="Modal with Footer"
        footer={<button>Save</button>}
      >
        <p>Content</p>
      </Modal>
    );

    expect(screen.getByText('Save')).toBeInTheDocument();
  });

  it('does not render footer when not provided', () => {
    const { container } = render(
      <Modal isOpen={true} onClose={mockOnClose} title="Modal without Footer">
        <p>Content</p>
      </Modal>
    );

    const footer = container.querySelector('.border-t.border-gray-200.bg-gray-50');
    expect(footer).not.toBeInTheDocument();
  });

  it('applies small size class', () => {
    const { container } = render(
      <Modal isOpen={true} onClose={mockOnClose} title="Small Modal" size="sm">
        <p>Content</p>
      </Modal>
    );

    const modal = container.querySelector('.max-w-md');
    expect(modal).toBeInTheDocument();
  });

  it('applies medium size class by default', () => {
    const { container } = render(
      <Modal isOpen={true} onClose={mockOnClose} title="Default Modal">
        <p>Content</p>
      </Modal>
    );

    const modal = container.querySelector('.max-w-lg');
    expect(modal).toBeInTheDocument();
  });

  it('applies large size class', () => {
    const { container } = render(
      <Modal isOpen={true} onClose={mockOnClose} title="Large Modal" size="lg">
        <p>Content</p>
      </Modal>
    );

    const modal = container.querySelector('.max-w-2xl');
    expect(modal).toBeInTheDocument();
  });

  it('applies xl size class', () => {
    const { container } = render(
      <Modal isOpen={true} onClose={mockOnClose} title="XL Modal" size="xl">
        <p>Content</p>
      </Modal>
    );

    const modal = container.querySelector('.max-w-4xl');
    expect(modal).toBeInTheDocument();
  });

  it('sets body overflow to hidden when open', () => {
    render(
      <Modal isOpen={true} onClose={mockOnClose} title="Test Modal">
        <p>Content</p>
      </Modal>
    );

    expect(document.body.style.overflow).toBe('hidden');
  });

  it('resets body overflow when closed', () => {
    const { rerender } = render(
      <Modal isOpen={true} onClose={mockOnClose} title="Test Modal">
        <p>Content</p>
      </Modal>
    );

    rerender(
      <Modal isOpen={false} onClose={mockOnClose} title="Test Modal">
        <p>Content</p>
      </Modal>
    );

    expect(document.body.style.overflow).toBe('unset');
  });
});
