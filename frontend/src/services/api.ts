import axios from 'axios';
import { Card, Deck, DeckAnalysis } from '../types';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000/api',
});

export const DeckService = {
  async searchCards(query: string): Promise<Card[]> {
    const { data } = await api.get(`/cards/search?q=${query}`);
    return data;
  },

  async analyzeDeck(deck: Deck): Promise<DeckAnalysis> {
    const { data } = await api.post('/deck/analyze', deck);
    return data;
  },

  async saveDeck(deck: Deck): Promise<Deck> {
    const { data } = await api.post('/deck', deck);
    return data;
  },
};