import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
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

// Services
import { CardService } from '../../core/services/card.service';
import { DeckService } from '../../core/services/deck.service';

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
    TableModule
  ],
  templateUrl: './card-selector.component.html',
  styleUrls: ['./card-selector.component.scss']
})
export class CardSelectorComponent implements OnInit {
  cardSearchForm!: FormGroup;
  cardResults: any[] = [];
  currentDeckId: string | null = null; // Add this to track the current deck

  manaCostOptions = Array.from({length: 8}, (_, i) => i);

  colorOptions = [
    { name: 'White', value: 'white' },
    { name: 'Blue', value: 'blue' },
    { name: 'Black', value: 'black' },
    { name: 'Red', value: 'red' },
    { name: 'Green', value: 'green' }
  ];

  constructor(
    private formBuilder: FormBuilder, 
    private cardService: CardService,
    private deckService: DeckService
  ) {}

  ngOnInit() {
    this.initForm();
  }

  initForm() {
    this.cardSearchForm = this.formBuilder.group({
      searchTerm: ['', Validators.required],
      manaCost: ['', Validators.min(0)],
      colors: this.formBuilder.array([])
    });
  }

  toggleColor(color: string) {
    const colorsArray = this.cardSearchForm.get('colors') as FormArray;
    const index = colorsArray.controls.findIndex(control => control.value === color);

    if (index >= 0) {
      colorsArray.removeAt(index);
    } else {
      colorsArray.push(this.formBuilder.control(color));
    }
  }

  isColorSelected(color: string): boolean {
    const colorsArray = this.cardSearchForm.get('colors') as FormArray;
    return colorsArray.controls.some((control: { value: string; }) => control.value === color);
  }

  searchCards() {
    if (this.cardSearchForm.valid) {
      const searchParams = this.cardSearchForm.value;
      this.cardService.searchCards(searchParams).subscribe({
        next: (results: any[]) => {
          this.cardResults = results;
        },
        error: (error) => {
          console.error('Error searching cards', error);
        }
      });
    } else {
      this.markFormGroupTouched(this.cardSearchForm);
    }
  }

  markFormGroupTouched(formGroup: FormGroup) {
    Object.values(formGroup.controls).forEach(control => {
      control.markAsTouched();
    });
  }
  addCardToDeck(card: any) {
    // Check if a deck is selected
    if (!this.currentDeckId) {
      // Optionally, show a message to create/select a deck first
      console.warn('Please create or select a deck first');
      return;
    }

    // Call the deck service to add the card
    this.deckService.addCardToDeck(this.currentDeckId, card, 1).subscribe({
      next: (updatedDeck) => {
        // Handle successful card addition
        console.log('Card added to deck', updatedDeck);
        // Optionally, update the UI or show a success message
      },
      error: (error) => {
        console.error('Error adding card to deck', error);
        // Handle error (show error message, etc.)
      }
    });
  }
  get f() {
    return this.cardSearchForm.controls;
  }
}