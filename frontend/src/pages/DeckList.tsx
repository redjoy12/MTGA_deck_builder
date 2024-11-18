import React from 'react';
import { Link } from 'react-router-dom';
import { useDeck } from '../context/DeckContext';

export const DeckList: React.FC = () => {
  const { savedDecks, deleteDeck } = useDeck();

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">My Decks</h1>
        <Link
          to="/builder"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Create New Deck
        </Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {savedDecks.map(deck => (
          <div key={deck.id} className="border rounded-lg p-4">
            <h2 className="text-xl font-semibold mb-2">{deck.name}</h2>
            <p className="text-gray-600 mb-4">{deck.format}</p>
            <div className="flex space-x-2">
              <Link
                to={`/decks/${deck.id}`}
                className="px-3 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
              >
                View
              </Link>
              <button
                onClick={() => deleteDeck(deck.id)}
                className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};