import React from 'react';
import { Card as CardComponent } from '../shared/Card';
import { Deck, Card } from '../../types'; 
import { ManaCurve } from './ManaCurve';

interface DeckViewProps {
  deck: Deck;
  onCardRemove: (cardId: string) => void;
}

export const DeckView: React.FC<DeckViewProps> = ({ deck, onCardRemove }) => {
  const groupedCards = deck.cards.reduce((acc, { card, quantity }) => {
    const type = card.type.split(' ')[0];
    if (!acc[type]) acc[type] = [];
    acc[type].push({ card, quantity });
    return acc;
  }, {} as Record<string, Array<{card: Card, quantity: number}>>);

  return (
    <div className="space-y-4">
      <ManaCurve deck={deck} />
      
      {Object.entries(groupedCards).map(([type, cards]) => (
        <div key={type}>
          <h3 className="text-xl font-bold mb-2">{type}</h3>
          <div className="grid grid-cols-4 gap-4">
            {cards.map(({ card, quantity }) => (
              <CardComponent 
                key={card.id}
                card={card}
                quantity={quantity}
                onRemove={() => onCardRemove(card.id)}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};