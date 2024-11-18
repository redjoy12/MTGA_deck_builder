import React, { useState } from 'react';
import { Card as CardComponent } from '../shared/Card';
import { DeckService } from '../../services/api';
import { useDeck } from '../../context/DeckContext';
import { Loading } from '../shared/Loading';
import { Card } from '../../types'; // Import Card as a type

export const CardList: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [cards, setCards] = useState<Card[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { addCardToDeck } = useDeck();

  const handleSearch = async () => {
    setIsLoading(true);
    try {
      const results = await DeckService.searchCards(searchQuery);
      setCards(results);
    } catch (error) {
      console.error('Card search failed', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-4">
      <div className="flex mb-4">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search cards..."
          className="flex-grow p-2 border rounded"
        />
        <button 
          onClick={handleSearch}
          className="bg-blue-500 text-white px-4 py-2 rounded ml-2"
        >
          Search
        </button>
      </div>

      {isLoading ? (
        <Loading />
      ) : (
        <div className="grid grid-cols-4 gap-4">
          {cards.map(card => (
            <CardComponent 
              key={card.id} 
              card={card} 
              onAdd={() => addCardToDeck(card)}
            />
          ))}
        </div>
      )}
    </div>
  );
};