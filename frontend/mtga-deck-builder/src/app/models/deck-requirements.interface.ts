export interface DeckRequirements {
  format: string;
  strategy: string;
  colors: string[];
  budget?: number;
  maxCmc?: number;
  archetype?: string;
  // Add more properties for deck generation requirements
}