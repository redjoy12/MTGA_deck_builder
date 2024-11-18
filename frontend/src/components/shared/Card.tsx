import React from 'react';
import { Card as CardType } from '../../types';

interface CardProps {
  card: CardType;
  quantity?: number;
  onAdd?: (card: CardType) => void;
  onRemove?: (card: CardType) => void;
}

export const Card: React.FC<CardProps> = ({ card, quantity, onAdd, onRemove }) => {
  return (
    <div className="relative rounded-lg overflow-hidden shadow-lg">
      <img 
        src={card.imageUrl} 
        alt={card.name} 
        className="w-full h-auto"
      />
      {quantity && (
        <div className="absolute top-0 right-0 bg-black bg-opacity-70 text-white px-2 py-1">
          {quantity}x
        </div>
      )}
      {(onAdd || onRemove) && (
        <div className="absolute bottom-0 w-full bg-black bg-opacity-70 p-2 flex justify-between">
          {onAdd && (
            <button 
              onClick={() => onAdd(card)}
              className="text-green-500 hover:text-green-400"
            >
              +
            </button>
          )}
          {onRemove && (
            <button 
              onClick={() => onRemove(card)}
              className="text-red-500 hover:text-red-400"
            >
              -
            </button>
          )}
        </div>
      )}
    </div>
  );
};