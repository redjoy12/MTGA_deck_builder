import React from 'react';
import { CardList } from '../components/DeckBuilder/CardList';
import { DeckView } from '../components/DeckBuilder/DeckView';
import { ChatInterface } from '../components/Chat/ChatInterface';
import { DeckAnalysisComponent } from '../components/Analysis/DeckAnalysis';
import { Recommendations } from '../components/Analysis/Recommendations';
import { useDeck } from '../context/DeckContext';

export const DeckBuilder: React.FC = () => {
  const { currentDeck, removeCardFromDeck } = useDeck();

  return (
    <div className="container mx-auto p-4">
      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2">
          <CardList />
          <div className="mt-4">
            <ChatInterface />
          </div>
        </div>
        <div className="space-y-4">
          <DeckView 
            deck={currentDeck || {
              id: '',
              name: 'New Deck',
              format: 'Standard',
              cards: []
            }} 
            onCardRemove={removeCardFromDeck}
          />
          <DeckAnalysisComponent />
          <Recommendations />
        </div>
      </div>
    </div>
  );
};