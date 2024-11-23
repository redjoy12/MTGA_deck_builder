// color-filter.component.ts
import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

// PrimeNG Imports
import { ButtonModule } from 'primeng/button';
import { MultiSelectModule } from 'primeng/multiselect';

@Component({
  selector: 'app-color-filter',
  standalone: true,
  imports: [
    CommonModule,
    ButtonModule,
    MultiSelectModule
  ],
  templateUrl: './color-filter.component.html',
  styleUrls: ['./color-filter.component.scss']
})
export class ColorFilterComponent {
  @Output() filterChange = new EventEmitter<string[]>();

  colors: string[] = ['Red', 'Blue', 'Green', 'Black', 'White'];
  selectedColors: string[] = [];

  applyFilter() {
    this.filterChange.emit(this.selectedColors);
  }
}