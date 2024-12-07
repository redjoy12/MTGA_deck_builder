export interface Card {
  id: string;
  name: string;
  manaCost: string;  // Add this property
  type: string;
  colors: string[];
  rarity?: string;
  set?: string;
  imageUrl?: string;
}