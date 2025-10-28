// deck-preview.component.ts
import { Component, Input, Output, EventEmitter, OnInit, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';

// PrimeNG Imports
import { CardModule } from 'primeng/card';
import { TableModule } from 'primeng/table';
import { ButtonModule } from 'primeng/button';
import { PanelModule } from 'primeng/panel';
import { DividerModule } from 'primeng/divider';
import { ChartModule } from 'primeng/chart';

// Interfaces
import { Card } from '../../models/card.interface';
import { Deck } from '../../models/deck.interface';

/**
 * Interface for deck statistics
 */
interface DeckStatistics {
  totalCards: number;
  creatures: number;
  spells: number;
  lands: number;
  artifacts: number;
  enchantments: number;
  planeswalkers: number;
  averageCmc: number;
  medianCmc: number;
}

/**
 * Interface for card with quantity for display
 */
interface DeckCard extends Card {
  quantity: number;
}

@Component({
  selector: 'app-deck-preview',
  standalone: true,
  imports: [
    CommonModule,
    CardModule,
    TableModule,
    ButtonModule,
    PanelModule,
    DividerModule,
    ChartModule
  ],
  templateUrl: './deck-preview.component.html',
  styleUrls: ['./deck-preview.component.scss']
})
export class DeckPreviewComponent implements OnInit, OnChanges {
  // Inputs
  @Input() deck?: Deck;
  @Input() cards: Card[] = [];  // Array of all available cards to lookup

  // Outputs
  @Output() saveDeck = new EventEmitter<Deck>();
  @Output() exportDeck = new EventEmitter<Deck>();
  @Output() cardRemoved = new EventEmitter<{ cardId: string; location: 'mainboard' | 'sideboard' }>();

  // Component state
  deckCards: DeckCard[] = [];
  sideboardCards: DeckCard[] = [];
  statistics?: DeckStatistics;
  manaCurveData: any;
  manaCurveOptions: any;

  ngOnInit(): void {
    this.initializeManaCurveOptions();
    this.updateDeckData();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['deck'] || changes['cards']) {
      this.updateDeckData();
    }
  }

  /**
   * Update deck data when inputs change
   */
  private updateDeckData(): void {
    if (!this.deck) {
      this.deckCards = [];
      this.sideboardCards = [];
      this.statistics = undefined;
      this.manaCurveData = undefined;
      return;
    }

    // Convert mainboard and sideboard to card arrays with quantities
    this.deckCards = this.convertToCardArray(this.deck.mainboard);
    this.sideboardCards = this.convertToCardArray(this.deck.sideboard || {});

    // Calculate statistics
    this.statistics = this.calculateStatistics();

    // Update mana curve chart
    this.updateManaCurveChart();
  }

  /**
   * Convert Record<string, number> to DeckCard array
   */
  private convertToCardArray(cardMap: Record<string, number>): DeckCard[] {
    const result: DeckCard[] = [];

    for (const [cardId, quantity] of Object.entries(cardMap)) {
      // Find card in the cards array
      const card = this.cards.find(c => c.id === cardId);
      if (card) {
        result.push({
          ...card,
          quantity
        });
      } else {
        // If card not found, create a placeholder
        result.push({
          id: cardId,
          name: 'Unknown Card',
          quantity
        } as DeckCard);
      }
    }

    return result.sort((a, b) => {
      // Sort by CMC, then by name
      const cmcA = a.cmc || 0;
      const cmcB = b.cmc || 0;
      if (cmcA !== cmcB) {
        return cmcA - cmcB;
      }
      return a.name.localeCompare(b.name);
    });
  }

  /**
   * Calculate comprehensive deck statistics
   */
  private calculateStatistics(): DeckStatistics {
    const allCards = [...this.deckCards];

    let totalCards = 0;
    let creatures = 0;
    let spells = 0;
    let lands = 0;
    let artifacts = 0;
    let enchantments = 0;
    let planeswalkers = 0;
    const cmcValues: number[] = [];

    allCards.forEach(card => {
      const quantity = card.quantity || 1;
      totalCards += quantity;

      const typeLine = (card.type_line || card.type || '').toLowerCase();

      // Count card types
      if (typeLine.includes('creature')) {
        creatures += quantity;
      }
      if (typeLine.includes('land')) {
        lands += quantity;
      }
      if (typeLine.includes('artifact')) {
        artifacts += quantity;
      }
      if (typeLine.includes('enchantment')) {
        enchantments += quantity;
      }
      if (typeLine.includes('planeswalker')) {
        planeswalkers += quantity;
      }
      if ((typeLine.includes('instant') || typeLine.includes('sorcery')) && !typeLine.includes('creature')) {
        spells += quantity;
      }

      // Collect CMC values for average/median calculation
      const cmc = card.cmc || 0;
      for (let i = 0; i < quantity; i++) {
        cmcValues.push(cmc);
      }
    });

    // Calculate average CMC
    const totalCmc = cmcValues.reduce((sum, cmc) => sum + cmc, 0);
    const averageCmc = totalCards > 0 ? totalCmc / totalCards : 0;

    // Calculate median CMC
    const sortedCmcValues = [...cmcValues].sort((a, b) => a - b);
    const mid = Math.floor(sortedCmcValues.length / 2);
    const medianCmc = sortedCmcValues.length > 0
      ? sortedCmcValues.length % 2 === 0
        ? (sortedCmcValues[mid - 1] + sortedCmcValues[mid]) / 2
        : sortedCmcValues[mid]
      : 0;

    return {
      totalCards,
      creatures,
      spells,
      lands,
      artifacts,
      enchantments,
      planeswalkers,
      averageCmc: Math.round(averageCmc * 100) / 100,
      medianCmc: Math.round(medianCmc * 100) / 100
    };
  }

  /**
   * Update mana curve chart data
   */
  private updateManaCurveChart(): void {
    const cmcCounts = new Map<number, number>();

    // Count cards by CMC
    this.deckCards.forEach(card => {
      const cmc = Math.min(card.cmc || 0, 7); // Cap at 7+ for display
      const quantity = card.quantity || 1;
      cmcCounts.set(cmc, (cmcCounts.get(cmc) || 0) + quantity);
    });

    // Prepare chart data
    const labels = ['0', '1', '2', '3', '4', '5', '6', '7+'];
    const data = labels.map((_, index) => cmcCounts.get(index) || 0);

    this.manaCurveData = {
      labels,
      datasets: [
        {
          label: 'Cards',
          data,
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }
      ]
    };
  }

  /**
   * Initialize mana curve chart options
   */
  private initializeManaCurveOptions(): void {
    this.manaCurveOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: 'Mana Curve',
          color: '#ffffff'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1,
            color: '#ffffff'
          },
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          }
        },
        x: {
          ticks: {
            color: '#ffffff'
          },
          grid: {
            color: 'rgba(255, 255, 255, 0.1)'
          }
        }
      }
    };
  }

  // Computed properties
  get deckName(): string {
    return this.deck?.name || 'Unnamed Deck';
  }

  get colors(): string {
    return this.deck?.colors?.join(', ') || 'No colors selected';
  }

  get format(): string {
    return this.deck?.format || 'No format';
  }

  get description(): string {
    return this.deck?.description || '';
  }

  get totalCards(): number {
    return this.statistics?.totalCards || 0;
  }

  get averageCmc(): number {
    return this.statistics?.averageCmc || 0;
  }

  // Event handlers
  removeCard(card: DeckCard, location: 'mainboard' | 'sideboard' = 'mainboard'): void {
    this.cardRemoved.emit({ cardId: card.id, location });
  }

  onSaveDeck(): void {
    if (this.deck) {
      this.saveDeck.emit(this.deck);
    }
  }

  onExportDeck(): void {
    if (this.deck) {
      // Export deck as text format
      this.exportDeckAsText();
    }
  }

  /**
   * Export deck in MTGA Arena format
   */
  private exportDeckAsText(): void {
    if (!this.deck) return;

    let exportText = `Deck\n`;

    // Add mainboard cards
    this.deckCards.forEach(card => {
      const setCode = card.set_code || card.set || 'UNK';
      exportText += `${card.quantity} ${card.name} (${setCode.toUpperCase()}) ${card.collector_number || ''}\n`;
    });

    // Add sideboard if present
    if (this.sideboardCards.length > 0) {
      exportText += `\nSideboard\n`;
      this.sideboardCards.forEach(card => {
        const setCode = card.set_code || card.set || 'UNK';
        exportText += `${card.quantity} ${card.name} (${setCode.toUpperCase()}) ${card.collector_number || ''}\n`;
      });
    }

    // Create and download file
    const blob = new Blob([exportText], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${this.deck.name.replace(/\s+/g, '_')}.txt`;
    link.click();
    window.URL.revokeObjectURL(url);

    this.exportDeck.emit(this.deck);
  }
}