import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { DeckProvider } from './context/DeckContext';
import { Home } from './pages/Home';
import { DeckBuilder } from './pages/DeckBuilder';
import { DeckList } from './pages/DeckList';
import { DeckView } from './components/DeckBuilder/DeckView';
import { CardList } from './components/DeckBuilder/CardList';
import { useDeck } from './context/DeckContext';
import { ChatInterface } from './components/Chat/ChatInterface';
import { DeckAnalysisComponent as DeckAnalysis } from './components/Analysis/DeckAnalysis';
import { Recommendations } from './components/Analysis/Recommendations';

function App() {
  return (
    <DeckProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/builder" element={<DeckBuilder />} />
          <Route path="/decks" element={<DeckList />} />
          <Route path="/decks/:id" element={<DeckBuilder />} />
        </Routes>
      </Router>
    </DeckProvider>
  );
}

const AppContent: React.FC = () => {
  const { currentDeck, removeCardFromDeck } = useDeck();

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">MTGA Deck Builder</h1>
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
          <DeckAnalysis />
          <Recommendations />
        </div>
      </div>
    </div>
  );
};

export default App;