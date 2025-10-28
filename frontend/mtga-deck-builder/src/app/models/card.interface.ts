/**
 * Card interface matching backend SQLAlchemy Card model.
 * Represents an MTGA card with comprehensive Scryfall data.
 */
export interface Card {
  // Core identification
  id: string;
  scryfall_id?: string;
  oracle_id?: string;
  name: string;

  // Mana and casting
  mana_cost?: string;
  cmc?: number;
  color_identity?: string[];
  color_indicator?: string[];

  // Card text and type
  oracle_text?: string;
  type_line?: string;
  flavor_text?: string;

  // Stats
  power?: string;
  toughness?: string;
  loyalty?: string;
  hand_modifier?: string;  // For Vanguard cards
  life_modifier?: string;  // For Vanguard cards

  // Rarity and collection
  rarity?: string;
  set_code?: string;
  collector_number?: string;
  artist?: string;
  released_at?: string;  // YYYY-MM-DD format

  // Images
  image_uri?: string;
  back_image_uri?: string;  // For double-faced cards

  // Mechanics
  keywords?: string[];
  produced_mana?: string[];

  // Format legality
  legalities?: Record<string, string>;

  // Pricing
  price?: number;
  prices?: Record<string, string>;  // Complete price data (usd, usd_foil, eur, tix)

  // Commander/EDH
  edhrec_rank?: number;

  // Double-faced cards
  layout?: string;  // 'normal', 'transform', 'modal_dfc', etc.
  card_faces?: any;  // Full face data for double-faced cards

  // AI features
  vector_embedding?: Record<string, number>;

  // Legacy fields for backwards compatibility
  manaCost?: string;  // Alias for mana_cost
  type?: string;      // Alias for type_line
  colors?: string[];  // Alias for color_identity
  set?: string;       // Alias for set_code
  imageUrl?: string;  // Alias for image_uri
}
