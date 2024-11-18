import React from 'react';
import { Link } from 'react-router-dom';
import { useDeck } from '../context/DeckContext';

export const Home: React.FC = () => {
  const { savedDecks } = useDeck();

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">MTGA Deck Builder</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="space-y-4">
            <Link
              to="/builder"
              className="block w-full p-4 bg-blue-600 text-white rounded-lg text-center hover:bg-blue-700"
            >
              Create New Deck
            </Link>
            <Link
              to="/decks"
              className="block w-full p-4 bg-gray-600 text-white rounded-lg text-center hover:bg-gray-700"
            >
              View All Decks
            </Link>
          </div>
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-4">Recent Decks</h2>
          <div className="space-y-2">
            {savedDecks.slice(0, 5).map(deck => (
              <Link
                key={deck.id}
                to={`/decks/${deck.id}`}
                className="block p-4 border rounded-lg hover:bg-gray-50"
              >
                <h3 className="font-medium">{deck.name}</h3>
                <p className="text-sm text-gray-600">{deck.format} - {deck.cards.length} cards</p>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};