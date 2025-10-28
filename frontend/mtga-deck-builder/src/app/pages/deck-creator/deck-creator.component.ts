import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import {
  FormsModule,
  ReactiveFormsModule,
  FormBuilder,
  FormGroup,
  Validators
} from '@angular/forms';

// Services
import { DeckService } from '../../core/services/deck.service';

// Models
import { DeckRequirements } from '../../models/deck-requirements.interface';
import { Deck } from '../../models/deck.interface';

@Component({
  selector: 'app-deck-creator',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule
  ],
  templateUrl: './deck-creator.component.html',
  styleUrls: ['./deck-creator.component.scss']
})
export class DeckCreatorComponent implements OnInit {
  deckForm!: FormGroup;
  isLoading = false;
  errorMessage = '';
  successMessage = '';

  formats = ['Standard', 'Historic', 'Pioneer', 'Modern', 'Legacy', 'Vintage'];
  strategies = ['Aggro', 'Control', 'Midrange', 'Combo', 'Tempo'];

  colorOptions = [
    { name: 'White', value: 'white' },
    { name: 'Blue', value: 'blue' },
    { name: 'Black', value: 'black' },
    { name: 'Red', value: 'red' },
    { name: 'Green', value: 'green' }
  ];

  constructor(
    private fb: FormBuilder,
    private deckService: DeckService,
    private router: Router
  ) {}

  ngOnInit() {
    this.initForm();
  }

  initForm() {
    this.deckForm = this.fb.group({
      name: ['', [
        Validators.required,
        Validators.minLength(3),
        Validators.maxLength(50)
      ]],
      format: ['', Validators.required],
      strategy: ['', Validators.required],
      colors: [[], [Validators.required, this.validateColors.bind(this)]],
      description: ['', Validators.maxLength(200)]
    });
  }

  // Custom validator for colors array
  validateColors(control: any) {
    const colors = control.value;
    if (!colors || colors.length === 0) {
      return { required: true };
    }
    if (colors.length > 3) {
      return { maxColors: true };
    }
    return null;
  }

  generateDeck() {
    // Clear previous messages
    this.errorMessage = '';
    this.successMessage = '';

    if (this.deckForm.invalid) {
      // Mark all fields as touched to show validation errors
      Object.keys(this.deckForm.controls).forEach(key => {
        this.deckForm.get(key)?.markAsTouched();
      });
      this.errorMessage = 'Please fill in all required fields correctly.';
      return;
    }

    this.isLoading = true;

    // Build deck requirements object
    const requirements: DeckRequirements = {
      format: this.deckForm.value.format,
      strategy: this.deckForm.value.strategy,
      colors: this.deckForm.value.colors,
      description: this.deckForm.value.description || undefined
    };

    // Call the deck service to generate the deck
    this.deckService.generateDeck(requirements).subscribe({
      next: (generatedDeck: Deck) => {
        this.isLoading = false;
        this.successMessage = `Deck "${this.deckForm.value.name}" generated successfully!`;

        // Update the deck name with user's input
        generatedDeck.name = this.deckForm.value.name;

        // Save the generated deck
        this.deckService.createDeck(generatedDeck).subscribe({
          next: (savedDeck: Deck) => {
            // Navigate to deck details or deck list after a short delay
            setTimeout(() => {
              this.router.navigate(['/decks', savedDeck.id]);
            }, 1500);
          },
          error: (error: any) => {
            this.isLoading = false;
            this.errorMessage = error?.error?.detail || 'Failed to save the generated deck. Please try again.';
            console.error('Error saving deck:', error);
          }
        });
      },
      error: (error: any) => {
        this.isLoading = false;
        this.errorMessage = error?.error?.detail || 'Failed to generate deck. Please try again.';
        console.error('Error generating deck:', error);
      }
    });
  }

  isColorSelected(color: string): boolean {
    const colors = this.deckForm.get('colors')?.value || [];
    return colors.includes(color);
  }

  toggleColor(color: string) {
    const colorsControl = this.deckForm.get('colors');
    const currentColors = colorsControl?.value || [];
    
    if (this.isColorSelected(color)) {
      // Remove the color if already selected
      colorsControl?.setValue(currentColors.filter((c: string) => c !== color));
    } else {
      // Add the color if not selected (with max 3 color limit)
      if (currentColors.length < 3) {
        colorsControl?.setValue([...currentColors, color]);
      }
    }
  }

  get f() {
    return this.deckForm.controls;
  }
}