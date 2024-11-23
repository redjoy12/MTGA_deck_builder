import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

// Import Chart.js
import { Chart, registerables } from 'chart.js';

// PrimeNG Imports
import { CardModule } from 'primeng/card';
import { PanelModule } from 'primeng/panel';
import { ChartModule } from 'primeng/chart';
import { ProgressBarModule } from 'primeng/progressbar';

Chart.register(...registerables);
// Define an interface for the wildcard data structure
interface WildcardData {
  common: { current: number; total: number };
  uncommon: { current: number; total: number };
  rare: { current: number; total: number };
  mythic: { current: number; total: number };
}

// Define a type for valid wildcard types
type WildcardType = keyof WildcardData;

@Component({
  selector: 'app-resource-manager',
  standalone: true,
  imports: [
    CommonModule,
    CardModule,
    PanelModule,
    ChartModule,
    ProgressBarModule
  ],
  templateUrl: './resource-manager.component.html',
  styleUrls: ['./resource-manager.component.scss']
})
export class ResourceManagerComponent implements OnInit{
  // Define the wildcard types as a readonly array
  readonly wildcardTypes: WildcardType[] = ['common', 'uncommon', 'rare', 'mythic'];

  // Use the WildcardData interface
  wildcardData: WildcardData = {
    common: { current: 10, total: 20 },
    uncommon: { current: 5, total: 15 },
    rare: { current: 3, total: 10 },
    mythic: { current: 1, total: 5 }
  };

  // Method to safely get wildcard data
  getWildcardProgressValue(type: WildcardType): number {
    const data = this.wildcardData[type];
    return (data.current / data.total) * 100;
  }

  currencyData = {
    gold: 5000,
    gems: 500
  };

  wildcardChartData = {
    labels: ['Common', 'Uncommon', 'Rare', 'Mythic'],
    datasets: [{
      data: [10, 5, 3, 1],
      backgroundColor: ['#A0A0A0', '#808080', '#D4AF37', '#B94E31']
    }]
  };
  ngOnInit() {
    // Optional: Additional Chart.js configuration if needed
  }
}