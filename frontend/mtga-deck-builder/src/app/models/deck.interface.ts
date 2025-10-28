import { Card } from './card.interface';

/**
 * Deck interface matching backend SQLAlchemy Deck model.
 * Represents a deck with JSONB storage for mainboard/sideboard.
 */
export interface Deck {
  // Identification
  id?: number;
  name: string;
  format: string;
  description?: string;

  // Timestamps
  created_at?: string;
  updated_at?: string;

  // Deck composition stored as {card_id: quantity}
  mainboard: Record<string, number>;
  sideboard?: Record<string, number>;

  // Deck properties
  colors: string[];
  strategy_tags?: string[];

  // Optional: Full card objects for UI display (not stored in backend)
  cards?: Card[];
}

/**
 * Legacy deck interface for backwards compatibility.
 * @deprecated Use Deck interface with mainboard/sideboard as Record<string, number>
 */
export interface LegacyDeck {
  id?: string;
  name: string;
  format: string;
  strategy: string;
  colors: string[];
  description?: string;
  mainboard: Card[];
  sideboard?: Card[];
}
