import { Card } from './card.interface';

export interface Deck {
    id?: string;
    name: string;
    format: string;
    strategy: string;
    colors: string[];
    description?: string;
    mainboard: Card[];
    sideboard?: Card[];
}