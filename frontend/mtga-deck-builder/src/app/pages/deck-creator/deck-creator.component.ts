import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { 
  FormsModule, 
  ReactiveFormsModule, 
  FormBuilder, 
  FormGroup, 
  Validators 
} from '@angular/forms';

// PrimeNG Imports
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { DropdownModule } from 'primeng/dropdown';
import { MultiSelectModule } from 'primeng/multiselect';
import { InputTextareaModule } from 'primeng/inputtextarea';

@Component({
  selector: 'app-deck-creator',
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
    InputTextareaModule
  ],
  templateUrl: './deck-creator.component.html',
  styleUrls: ['./deck-creator.component.scss']
})
export class DeckCreatorComponent implements OnInit {
  deckForm!: FormGroup;

  formats = [
    { label: 'Standard', value: 'Standard' },
    { label: 'Historic', value: 'Historic' },
    { label: 'Pioneer', value: 'Pioneer' },
    { label: 'Modern', value: 'Modern' },
    { label: 'Legacy', value: 'Legacy' },
    { label: 'Vintage', value: 'Vintage' }
  ];

  strategies = [
    { label: 'Aggro', value: 'Aggro' },
    { label: 'Control', value: 'Control' },
    { label: 'Midrange', value: 'Midrange' },
    { label: 'Combo', value: 'Combo' },
    { label: 'Tempo', value: 'Tempo' }
  ];

  colorOptions = [
    { name: 'White', value: 'white' },
    { name: 'Blue', value: 'blue' },
    { name: 'Black', value: 'black' },
    { name: 'Red', value: 'red' },
    { name: 'Green', value: 'green' }
  ];

  constructor(private fb: FormBuilder) {}

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
      colors: [[], [Validators.required, Validators.maxLength(3)]],
      description: ['', Validators.maxLength(200)]
    });
  }

  generateDeck() {
    if (this.deckForm.valid) {
      const deckData = this.deckForm.value;
      console.log('Deck generated:', deckData);
      // Call deck generation service or handle the deck creation logic here
    }
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