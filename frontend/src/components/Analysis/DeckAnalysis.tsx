import React from 'react';
import { Deck, DeckAnalysis } from '../../types';
import { useDeck } from '../../context/DeckContext';

const analyzeDeck = (deck: Deck): DeckAnalysis => {
  const manaCurve: Record<number, number> = {};
  const colorDistribution: Record<string, number> = {};
  let totalCmc = 0;
  let landCount = 0;
  let creatureCount = 0;
  let spellCount = 0;

  deck.cards.forEach(({ card, quantity }) => {
    // Mana curve
    const cmc = card.cmc;
    manaCurve[cmc] = (manaCurve[cmc] || 0) + quantity;
    totalCmc += cmc * quantity;

    // Color distribution
    if (card.colors) {
      card.colors.forEach(color => {
        colorDistribution[color] = (colorDistribution[color] || 0) + quantity;
      });
    }

    // Card type counts
    if (card.type.toLowerCase().includes('land')) {
      landCount += quantity;
    } else if (card.type.toLowerCase().includes('creature')) {
      creatureCount += quantity;
    } else {
      spellCount += quantity;
    }
  });

  const totalCards = deck.cards.reduce((sum, { quantity }) => sum + quantity, 0);
  const averageCmc = totalCards > 0 ? totalCmc / (totalCards - landCount) : 0;

  return {
    manaCurve,
    colorDistribution,
    landCount,
    creatureCount,
    spellCount,
    averageCmc
  };
};

const colorNames = {
  W: 'White',
  U: 'Blue',
  B: 'Black',
  R: 'Red',
  G: 'Green'
};

export const DeckAnalysisComponent: React.FC = () => {
  const { currentDeck } = useDeck();
  
  if (!currentDeck) {
    return (
      <div className="p-4 bg-gray-50 rounded-lg">
        <p className="text-gray-500">No deck loaded for analysis</p>
      </div>
    );
  }

  const analysis = analyzeDeck(currentDeck);
  const totalCards = Object.values(analysis.manaCurve).reduce((a, b) => a + b, 0);

  return (
    <div className="bg-white rounded-lg shadow-sm">
      <div className="p-4 border-b">
        <h2 className="text-xl font-semibold">Deck Analysis</h2>
      </div>
      
      <div className="p-4 space-y-6">
        {/* Card Type Distribution */}
        <div>
          <h3 className="text-lg font-medium mb-2">Card Distribution</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-blue-50 p-3 rounded">
              <p className="text-sm text-gray-600">Lands</p>
              <p className="text-xl font-bold">{analysis.landCount}</p>
            </div>
            <div className="bg-green-50 p-3 rounded">
              <p className="text-sm text-gray-600">Creatures</p>
              <p className="text-xl font-bold">{analysis.creatureCount}</p>
            </div>
            <div className="bg-purple-50 p-3 rounded">
              <p className="text-sm text-gray-600">Spells</p>
              <p className="text-xl font-bold">{analysis.spellCount}</p>
            </div>
          </div>
        </div>

        {/* Color Distribution */}
        <div>
          <h3 className="text-lg font-medium mb-2">Color Distribution</h3>
          <div className="space-y-2">
            {Object.entries(analysis.colorDistribution).map(([color, count]) => (
              <div key={color} className="flex items-center">
                <span className="w-20 text-sm">{colorNames[color as keyof typeof colorNames]}</span>
                <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500"
                    style={{ width: `${(count / totalCards) * 100}%` }}
                  />
                </div>
                <span className="ml-2 text-sm">{count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Average CMC */}
        <div>
          <h3 className="text-lg font-medium mb-2">Mana Statistics</h3>
          <p className="text-sm">
            Average CMC: <span className="font-medium">{analysis.averageCmc.toFixed(2)}</span>
          </p>
        </div>
      </div>
    </div>
  );
};