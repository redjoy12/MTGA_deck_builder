import React from 'react';
import { Deck, DeckRecommendation } from '../../types';
import { useDeck } from '../../context/DeckContext';

const generateRecommendations = (deck: Deck): DeckRecommendation[] => {
  const recommendations: DeckRecommendation[] = [];
  const totalCards = deck.cards.reduce((sum, { quantity }) => sum + quantity, 0);
  const landCount = deck.cards.filter(({ card }) => 
    card.type.toLowerCase().includes('land')
  ).reduce((sum, { quantity }) => sum + quantity, 0);
  
  // Check deck size
  if (totalCards < 60) {
    recommendations.push({
      type: 'warning',
      message: `Deck needs ${60 - totalCards} more cards to be legal`,
      priority: 'high',
      reason: 'Minimum deck size requirement'
    });
  }

  // Check land count
  const recommendedLands = Math.floor(totalCards * 0.4); // 40% lands is typical
  if (landCount < recommendedLands) {
    recommendations.push({
      type: 'add',
      message: `Consider adding ${recommendedLands - landCount} more lands`,
      priority: 'high',
      reason: 'Insufficient mana base'
    });
  }

  // Add more complex recommendations based on deck composition
  return recommendations;
};

interface RecommendationCardProps {
  recommendation: DeckRecommendation;
}

const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation }) => {
  const priorityColors = {
    high: 'bg-red-50 border-red-200',
    medium: 'bg-yellow-50 border-yellow-200',
    low: 'bg-green-50 border-green-200'
  };

  const typeIcons = {
    warning: '⚠️',
    add: '➕',
    remove: '➖'
  };

  return (
    <div className={`p-4 rounded-lg border ${priorityColors[recommendation.priority]}`}>
      <div className="flex items-start">
        <span className="text-xl mr-2">{typeIcons[recommendation.type]}</span>
        <div>
          <p className="font-medium">{recommendation.message}</p>
          <p className="text-sm text-gray-600 mt-1">{recommendation.reason}</p>
        </div>
      </div>
    </div>
  );
};

export const Recommendations: React.FC = () => {
  const { currentDeck } = useDeck();

  if (!currentDeck) {
    return (
      <div className="p-4 bg-gray-50 rounded-lg">
        <p className="text-gray-500">No deck loaded for recommendations</p>
      </div>
    );
  }

  const recommendations = generateRecommendations(currentDeck);

  return (
    <div className="bg-white rounded-lg shadow-sm">
      <div className="p-4 border-b">
        <h2 className="text-xl font-semibold">Recommendations</h2>
      </div>
      
      <div className="p-4">
        {recommendations.length > 0 ? (
          <div className="space-y-4">
            {recommendations.map((recommendation, index) => (
              <RecommendationCard 
                key={index} 
                recommendation={recommendation}
              />
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No recommendations at this time.</p>
        )}
      </div>
    </div>
  );
};