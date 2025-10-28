import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DeckPreviewComponent } from './deck-preview.component';
import { Card } from '../../models/card.interface';
import { Deck } from '../../models/deck.interface';

describe('DeckPreviewComponent', () => {
  let component: DeckPreviewComponent;
  let fixture: ComponentFixture<DeckPreviewComponent>;

  const mockCards: Card[] = [
    {
      id: '1',
      name: 'Lightning Bolt',
      mana_cost: '{R}',
      cmc: 1,
      type_line: 'Instant',
      rarity: 'common',
      set_code: 'LEA',
      collector_number: '162'
    },
    {
      id: '2',
      name: 'Grizzly Bears',
      mana_cost: '{1}{G}',
      cmc: 2,
      type_line: 'Creature — Bear',
      power: '2',
      toughness: '2',
      rarity: 'common',
      set_code: 'LEA',
      collector_number: '200'
    },
    {
      id: '3',
      name: 'Forest',
      mana_cost: '',
      cmc: 0,
      type_line: 'Basic Land — Forest',
      rarity: 'common',
      set_code: 'LEA',
      collector_number: '294'
    },
    {
      id: '4',
      name: 'Fireball',
      mana_cost: '{X}{R}',
      cmc: 1,
      type_line: 'Sorcery',
      rarity: 'uncommon',
      set_code: 'LEA',
      collector_number: '150'
    }
  ];

  const mockDeck: Deck = {
    id: 1,
    name: 'Test Deck',
    format: 'Standard',
    description: 'A test deck',
    mainboard: {
      '1': 4,  // 4x Lightning Bolt
      '2': 3,  // 3x Grizzly Bears
      '3': 10, // 10x Forest
      '4': 2   // 2x Fireball
    },
    sideboard: {},
    colors: ['R', 'G']
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DeckPreviewComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DeckPreviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('Input handling', () => {
    it('should handle undefined deck gracefully', () => {
      component.deck = undefined;
      component.cards = [];
      component.ngOnChanges({
        deck: { currentValue: undefined, previousValue: null, firstChange: true, isFirstChange: () => true }
      });

      expect(component.deckCards).toEqual([]);
      expect(component.sideboardCards).toEqual([]);
      expect(component.statistics).toBeUndefined();
      expect(component.manaCurveData).toBeUndefined();
    });

    it('should process deck input correctly', () => {
      component.deck = mockDeck;
      component.cards = mockCards;
      component.ngOnChanges({
        deck: { currentValue: mockDeck, previousValue: null, firstChange: true, isFirstChange: () => true }
      });

      expect(component.deckCards.length).toBeGreaterThan(0);
      expect(component.statistics).toBeDefined();
      expect(component.manaCurveData).toBeDefined();
    });
  });

  describe('Computed properties', () => {
    beforeEach(() => {
      component.deck = mockDeck;
      component.cards = mockCards;
      component.ngOnInit();
    });

    it('should return correct deck name', () => {
      expect(component.deckName).toBe('Test Deck');
    });

    it('should return default name for undefined deck', () => {
      component.deck = undefined;
      expect(component.deckName).toBe('Unnamed Deck');
    });

    it('should return correct colors', () => {
      expect(component.colors).toBe('R, G');
    });

    it('should return correct format', () => {
      expect(component.format).toBe('Standard');
    });

    it('should return correct description', () => {
      expect(component.description).toBe('A test deck');
    });
  });

  describe('Statistics calculation', () => {
    beforeEach(() => {
      component.deck = mockDeck;
      component.cards = mockCards;
      component.ngOnInit();
    });

    it('should calculate total cards correctly', () => {
      expect(component.statistics?.totalCards).toBe(19); // 4+3+10+2
    });

    it('should calculate creatures correctly', () => {
      expect(component.statistics?.creatures).toBe(3); // 3x Grizzly Bears
    });

    it('should calculate spells correctly', () => {
      expect(component.statistics?.spells).toBe(6); // 4x Lightning Bolt + 2x Fireball
    });

    it('should calculate lands correctly', () => {
      expect(component.statistics?.lands).toBe(10); // 10x Forest
    });

    it('should calculate average CMC', () => {
      expect(component.statistics?.averageCmc).toBeGreaterThan(0);
    });

    it('should calculate median CMC', () => {
      expect(component.statistics?.medianCmc).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Mana curve', () => {
    beforeEach(() => {
      component.deck = mockDeck;
      component.cards = mockCards;
      component.ngOnInit();
    });

    it('should generate mana curve data', () => {
      expect(component.manaCurveData).toBeDefined();
      expect(component.manaCurveData.labels).toBeDefined();
      expect(component.manaCurveData.datasets).toBeDefined();
      expect(component.manaCurveData.datasets.length).toBe(1);
    });

    it('should have correct mana curve labels', () => {
      expect(component.manaCurveData.labels).toEqual(['0', '1', '2', '3', '4', '5', '6', '7+']);
    });

    it('should count cards by CMC correctly', () => {
      const data = component.manaCurveData.datasets[0].data;
      expect(data[0]).toBe(10); // 10x Forest (CMC 0)
      expect(data[1]).toBeGreaterThan(0); // Lightning Bolt and Fireball (CMC 1)
      expect(data[2]).toBe(3); // 3x Grizzly Bears (CMC 2)
    });
  });

  describe('Event emitters', () => {
    beforeEach(() => {
      component.deck = mockDeck;
      component.cards = mockCards;
      component.ngOnInit();
    });

    it('should emit saveDeck event', () => {
      spyOn(component.saveDeck, 'emit');
      component.onSaveDeck();
      expect(component.saveDeck.emit).toHaveBeenCalledWith(mockDeck);
    });

    it('should emit exportDeck event', () => {
      spyOn(component.exportDeck, 'emit');
      // Mock window.URL.createObjectURL and related functions
      spyOn(window.URL, 'createObjectURL').and.returnValue('mock-url');
      spyOn(window.URL, 'revokeObjectURL');

      component.onExportDeck();

      expect(component.exportDeck.emit).toHaveBeenCalledWith(mockDeck);
    });

    it('should emit cardRemoved event', () => {
      spyOn(component.cardRemoved, 'emit');
      const card = component.deckCards[0];
      component.removeCard(card, 'mainboard');
      expect(component.cardRemoved.emit).toHaveBeenCalledWith({ cardId: card.id, location: 'mainboard' });
    });
  });

  describe('Card array conversion', () => {
    it('should convert mainboard to card array with quantities', () => {
      component.deck = mockDeck;
      component.cards = mockCards;
      component.ngOnInit();

      expect(component.deckCards.length).toBe(4); // 4 unique cards

      const lightningBolt = component.deckCards.find(c => c.name === 'Lightning Bolt');
      expect(lightningBolt?.quantity).toBe(4);

      const grizzlyBears = component.deckCards.find(c => c.name === 'Grizzly Bears');
      expect(grizzlyBears?.quantity).toBe(3);
    });

    it('should sort cards by CMC then name', () => {
      component.deck = mockDeck;
      component.cards = mockCards;
      component.ngOnInit();

      // First card should be CMC 0 (Forest)
      expect(component.deckCards[0].cmc).toBe(0);

      // Cards should be sorted by CMC
      for (let i = 1; i < component.deckCards.length; i++) {
        expect(component.deckCards[i].cmc).toBeGreaterThanOrEqual(component.deckCards[i - 1].cmc || 0);
      }
    });
  });

  describe('Export functionality', () => {
    beforeEach(() => {
      component.deck = mockDeck;
      component.cards = mockCards;
      component.ngOnInit();
    });

    it('should generate MTGA format text', () => {
      // Mock DOM elements
      const mockLink = document.createElement('a');
      spyOn(document, 'createElement').and.returnValue(mockLink);
      spyOn(mockLink, 'click');
      spyOn(window.URL, 'createObjectURL').and.returnValue('mock-url');
      spyOn(window.URL, 'revokeObjectURL');

      component.onExportDeck();

      expect(window.URL.createObjectURL).toHaveBeenCalled();
      expect(mockLink.click).toHaveBeenCalled();
      expect(window.URL.revokeObjectURL).toHaveBeenCalled();
    });
  });
});
