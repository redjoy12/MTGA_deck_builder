import React from 'react';
import { Deck } from '../../types';

interface ManaCurveProps {
  deck: Deck;
}

export const ManaCurve: React.FC<ManaCurveProps> = ({ deck }) => {
  // Calculate mana curve distribution
  const manaCurve = deck.cards.reduce((acc, { card, quantity }) => {
    const cmc = card.cmc;
    acc[cmc] = (acc[cmc] || 0) + quantity;
    return acc;
  }, {} as Record<number, number>);

  // Determine the maximum count for scaling
  const maxCount = Math.max(...Object.values(manaCurve), 1);

  return (
    <div className="bg-gray-100 p-4 rounded-lg">
      <h3 className="text-lg font-semibold mb-2">Mana Curve</h3>
      <div className="flex justify-between items-end h-24">
        {[0, 1, 2, 3, 4, 5, 6, 7].map((cmc) => (
          <div key={cmc} className="flex flex-col items-center w-10">
            <div 
              className="bg-blue-500 w-full" 
              style={{
                height: `${(manaCurve[cmc] || 0) / maxCount * 100}%`,
                minHeight: '4px'
              }}
            />
            <span className="text-xs mt-1">{cmc}</span>
            <span className="text-xs">{manaCurve[cmc] || 0}</span>
          </div>
        ))}
      </div>
    </div>
  );
};