/**
 * Requirements interface for deck generation and AI agent expectations.
 * This interface defines all possible parameters for building a deck.
 */
export interface DeckRequirements {
  // Core requirements
  format: string;
  strategy: string;
  colors: string[];

  // Budget constraints
  budget?: number;
  maxCmc?: number;

  // Deck composition
  deckSize?: number;  // Default 60 for most formats
  sideboardSize?: number;  // Default 15
  minCreatures?: number;
  maxCreatures?: number;
  minLands?: number;
  maxLands?: number;
  minSpells?: number;
  maxSpells?: number;

  // Strategy and archetype
  archetype?: string;  // e.g., 'aggro', 'control', 'midrange', 'combo'
  strategy_tags?: string[];  // Multiple strategy tags

  // Card preferences
  includedCards?: string[];  // Card IDs that must be included
  excludedCards?: string[];  // Card IDs that must not be included
  preferredKeywords?: string[];  // e.g., ['flying', 'lifelink']
  avoidKeywords?: string[];

  // Card type preferences
  preferredTypes?: string[];  // e.g., ['Creature', 'Instant']
  avoidTypes?: string[];

  // Mana curve preferences
  targetCurveDistribution?: Record<number, number>;  // {cmc: percentage}

  // Advanced preferences
  tribalType?: string;  // For tribal decks (e.g., 'Elf', 'Goblin')
  synergies?: string[];  // Preferred synergies
  winConditions?: string[];  // Preferred win conditions

  // Competitive level
  competitiveLevel?: 'casual' | 'competitive' | 'cedh';

  // Additional constraints
  mustIncludePlaneswalkers?: boolean;
  mustIncludeArtifacts?: boolean;
  banList?: string[];  // Additional cards to ban beyond format

  // Metadata
  description?: string;
  notes?: string;
}

/**
 * Result of deck validation against requirements.
 */
export interface DeckValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  suggestions?: string[];
}
