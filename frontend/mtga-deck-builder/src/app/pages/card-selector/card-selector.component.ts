import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import {
  FormsModule,
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  FormArray,
  Validators
} from '@angular/forms';

// PrimeNG Imports
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { DropdownModule } from 'primeng/dropdown';
import { MultiSelectModule } from 'primeng/multiselect';
import { TableModule } from 'primeng/table';
import { PaginatorModule } from 'primeng/paginator';
import { TooltipModule } from 'primeng/tooltip';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';

// Services
import { CardService } from '../../core/services/card.service';
import { DeckService } from '../../core/services/deck.service';
import { Card } from '../../models/card.interface';

@Component({
  selector: 'app-card-selector',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    CardModule,
    ButtonModule,
    InputTextModule,
    DropdownModule,
    MultiSelectModule,
    TableModule,
    PaginatorModule,
    TooltipModule,
    ToastModule
  ],
  providers: [MessageService],
  templateUrl: './card-selector.component.html',
  styleUrls: ['./card-selector.component.scss']
})
export class CardSelectorComponent implements OnInit {
  cardSearchForm!: FormGroup;
  allCardResults: Card[] = [];
  paginatedCardResults: Card[] = [];
  currentDeckId: string | null = null;

  // Pagination state
  totalRecords: number = 0;
  rows: number = 20; // Cards per page
  first: number = 0; // Starting index

  // Preview state
  hoveredCard: Card | null = null;

  manaCostOptions = Array.from({length: 16}, (_, i) => i);

  colorOptions = [
    { name: 'White', value: 'white', cssClass: 'white' },
    { name: 'Blue', value: 'blue', cssClass: 'blue' },
    { name: 'Black', value: 'black', cssClass: 'black' },
    { name: 'Red', value: 'red', cssClass: 'red' },
    { name: 'Green', value: 'green', cssClass: 'green' }
  ];

  constructor(
    private formBuilder: FormBuilder,
    private cardService: CardService,
    private deckService: DeckService,
    private route: ActivatedRoute,
    private router: Router,
    private messageService: MessageService
  ) {}

  ngOnInit() {
    this.initForm();
    this.loadDeckContext();
  }

  initForm() {
    // Make searchTerm optional - allow searches by colors or mana cost alone
    this.cardSearchForm = this.formBuilder.group({
      searchTerm: [''],
      manaCost: [''],
      colors: this.formBuilder.array([])
    });
  }

  /**
   * Load deck context from route parameters or query parameters
   * Supports both /card-selector?deckId=xxx and /deck/:id/cards routes
   */
  loadDeckContext() {
    // First, check route params (for routes like /deck/:id/cards)
    this.route.paramMap.subscribe(params => {
      const deckId = params.get('id') || params.get('deckId');
      if (deckId) {
        this.currentDeckId = deckId;
      }
    });

    // Then check query params (for routes like /card-selector?deckId=xxx)
    this.route.queryParamMap.subscribe(params => {
      const deckId = params.get('deckId');
      if (deckId) {
        this.currentDeckId = deckId;
      }
    });
  }

  /**
   * Toggle color selection in the FormArray
   */
  toggleColor(color: string) {
    const colorsArray = this.cardSearchForm.get('colors') as FormArray;
    const index = colorsArray.controls.findIndex(control => control.value === color);

    if (index >= 0) {
      colorsArray.removeAt(index);
    } else {
      colorsArray.push(this.formBuilder.control(color));
    }
  }

  /**
   * Check if a color is currently selected
   */
  isColorSelected(color: string): boolean {
    const colorsArray = this.cardSearchForm.get('colors') as FormArray;
    return colorsArray.controls.some((control: { value: string; }) => control.value === color);
  }

  /**
   * Get all selected colors as an array
   */
  get selectedColors(): string[] {
    const colorsArray = this.cardSearchForm.get('colors') as FormArray;
    return colorsArray.value;
  }

  /**
   * Search for cards with the current form values
   */
  searchCards() {
    const formValue = this.cardSearchForm.value;

    // Validate that at least one search criterion is provided
    if (!formValue.searchTerm &&
        (!formValue.colors || formValue.colors.length === 0) &&
        (formValue.manaCost === '' || formValue.manaCost === null)) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Search Required',
        detail: 'Please enter at least one search criterion (name, color, or mana cost)'
      });
      return;
    }

    const searchParams: any = {};

    if (formValue.searchTerm) {
      searchParams.searchTerm = formValue.searchTerm;
    }

    if (formValue.colors && formValue.colors.length > 0) {
      searchParams.colors = formValue.colors;
    }

    if (formValue.manaCost !== '' && formValue.manaCost !== null) {
      searchParams.manaCost = formValue.manaCost;
    }

    this.cardService.searchCards(searchParams).subscribe({
      next: (results: Card[]) => {
        this.allCardResults = results;
        this.totalRecords = results.length;
        this.first = 0; // Reset to first page
        this.updatePaginatedResults();

        // Safely validate and use results count
        const count = Number.isInteger(results.length) && results.length >= 0 ? results.length : 0;
        const cardText = count !== 1 ? 'cards' : 'card';

        if (count === 0) {
          this.messageService.add({
            severity: 'info',
            summary: 'No Results',
            detail: 'No cards found matching your search criteria'
          });
        } else {
          this.messageService.add({
            severity: 'success',
            summary: 'Search Complete',
            detail: 'Found ' + count + ' ' + cardText
          });
        }
      },
      error: (error) => {
        console.error('Error searching cards', error);
        // Never display raw error messages from external sources
        this.messageService.add({
          severity: 'error',
          summary: 'Search Failed',
          detail: 'Failed to search cards. Please try again.'
        });
      }
    });
  }

  /**
   * Handle pagination changes
   */
  onPageChange(event: any) {
    this.first = event.first;
    this.rows = event.rows;
    this.updatePaginatedResults();
  }

  /**
   * Update the paginated results based on current page
   */
  updatePaginatedResults() {
    const start = this.first;
    const end = this.first + this.rows;
    this.paginatedCardResults = this.allCardResults.slice(start, end);
  }

  /**
   * Add a card to the current deck
   */
  addCardToDeck(card: Card, quantity: number = 1) {
    // Check if a deck is selected
    if (!this.currentDeckId) {
      this.messageService.add({
        severity: 'warn',
        summary: 'No Deck Selected',
        detail: 'Please create or select a deck first. You can navigate to the deck creator to create a new deck.',
        life: 5000
      });
      return;
    }

    // Sanitize card name to prevent format string vulnerabilities
    const sanitizedCardName = this.sanitizeText(card.name);

    // Call the deck service to add the card
    this.deckService.addCardToDeck(this.currentDeckId, card, quantity).subscribe({
      next: (updatedDeck) => {
        this.messageService.add({
          severity: 'success',
          summary: 'Card Added',
          detail: 'Added ' + quantity + 'x ' + sanitizedCardName + ' to your deck'
        });
      },
      error: (error) => {
        console.error('Error adding card to deck', error);
        // Never display raw error messages from external sources
        this.messageService.add({
          severity: 'error',
          summary: 'Failed to Add Card',
          detail: 'Could not add card to deck. Please try again.'
        });
      }
    });
  }

  /**
   * Show card preview on hover
   */
  onCardHover(card: Card) {
    this.hoveredCard = card;
  }

  /**
   * Clear card preview
   */
  onCardLeave() {
    this.hoveredCard = null;
  }

  /**
   * Get card image URL with fallback
   */
  getCardImageUrl(card: Card): string {
    return card.image_uri || card.imageUrl || '/assets/images/card-back.png';
  }

  /**
   * Clear search form and results
   */
  clearSearch() {
    this.cardSearchForm.reset();
    const colorsArray = this.cardSearchForm.get('colors') as FormArray;
    colorsArray.clear();
    this.allCardResults = [];
    this.paginatedCardResults = [];
    this.totalRecords = 0;
    this.first = 0;
  }

  /**
   * Convenience getter for form controls
   */
  get f() {
    return this.cardSearchForm.controls;
  }

  /**
   * Get the FormArray for colors
   */
  get colorsFormArray(): FormArray {
    return this.cardSearchForm.get('colors') as FormArray;
  }

  /**
   * Calculate the end index for pagination display
   */
  getEndIndex(): number {
    return Math.min(this.first + this.rows, this.totalRecords);
  }

  /**
   * Sanitize text to prevent format string vulnerabilities and XSS
   * Removes or escapes potentially dangerous characters
   */
  private sanitizeText(text: string | undefined): string {
    if (!text) {
      return '';
    }

    // Convert to string and trim
    const str = String(text).trim();

    // Limit length to prevent DoS
    const maxLength = 200;
    const truncated = str.length > maxLength ? str.substring(0, maxLength) + '...' : str;

    // Remove control characters and other potentially dangerous characters
    // Allow only alphanumeric, spaces, and common punctuation
    const sanitized = truncated.replace(/[^\w\s\-',.:!?()]/g, '');

    return sanitized;
  }
}