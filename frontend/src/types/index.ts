export interface Card {
    id: string;
    name: string;
    manaCost: string;
    cmc: number;
    colors: string[];
    type: string;
    rarity: string;
    imageUrl: string;
  }
  
  export interface Deck {
    id: string;
    name: string;
    format: string;
    cards: Array<{card: Card; quantity: number}>;
  }
  
  export interface ChatMessage {
    id: string;
    content: string;
    sender: 'user' | 'ai';
    timestamp: Date;
  }

  export interface DeckSuggestion {
    cardName: string;
    reason: string;
    action: 'add' | 'remove';
  }

  export interface DeckAnalysis {
    manaCurve: Record<number, number>;
    colorDistribution: Record<string, number>;
    landCount: number;
    creatureCount: number;
    spellCount: number;
    averageCmc: number;
  }
  
  export interface DeckRecommendation {
    type: 'add' | 'remove' | 'warning';
    message: string;
    priority: 'high' | 'medium' | 'low';
    reason: string;
  }