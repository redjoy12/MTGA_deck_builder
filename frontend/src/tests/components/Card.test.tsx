import React from 'react';
import { render, fireEvent, screen } from '@testing-library/react';
import { Card } from '../../components/shared/Card';

describe('Card Component', () => {
  const mockCard = {
    id: '1',
    name: 'Test Card',
    manaCost: '{1}{B}',
    cmc: 2,
    colors: ['Black'],
    type: 'Creature',
    rarity: 'Common',
    imageUrl: 'test-url.jpg'
  };

  it('renders card with image and name', () => {
    render(<Card card={mockCard} />);
    expect(screen.getByAltText('Test Card')).toBeInTheDocument();
  });

  it('shows quantity when provided', () => {
    render(<Card card={mockCard} quantity={3} />);
    expect(screen.getByText('3x')).toBeInTheDocument();
  });

  it('calls onAdd when add button is clicked', () => {
    const onAdd = jest.fn();
    render(<Card card={mockCard} onAdd={onAdd} />);
    fireEvent.click(screen.getByText('+'));
    expect(onAdd).toHaveBeenCalledWith(mockCard);
  });
});