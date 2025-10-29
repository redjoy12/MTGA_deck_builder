import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject, takeUntil } from 'rxjs';

// Import Chart.js with proper types
import { Chart, ChartData, ChartOptions, registerables } from 'chart.js';

// PrimeNG Imports
import { CardModule } from 'primeng/card';
import { PanelModule } from 'primeng/panel';
import { ChartModule } from 'primeng/chart';
import { ProgressBarModule } from 'primeng/progressbar';
import { MessageService } from 'primeng/api';
import { ToastModule } from 'primeng/toast';
import { ButtonModule } from 'primeng/button';

// Services and models
import {
  UserResourcesService,
  WildcardData,
  WildcardType,
  UserResources
} from '../../core/services/user-resources.service';
import { AuthService } from '../../core/services/auth.service';

Chart.register(...registerables);

@Component({
  selector: 'app-resource-manager',
  standalone: true,
  imports: [
    CommonModule,
    CardModule,
    PanelModule,
    ChartModule,
    ProgressBarModule,
    ToastModule,
    ButtonModule
  ],
  providers: [MessageService],
  templateUrl: './resource-manager.component.html',
  styleUrls: ['./resource-manager.component.scss']
})
export class ResourceManagerComponent implements OnInit, OnDestroy {
  // Define the wildcard types as a readonly array
  readonly wildcardTypes: readonly WildcardType[] = ['common', 'uncommon', 'rare', 'mythic'] as const;

  // Wildcard data with proper typing
  wildcardData: WildcardData = {
    common: { current: 0, total: 20 },
    uncommon: { current: 0, total: 20 },
    rare: { current: 0, total: 20 },
    mythic: { current: 0, total: 20 }
  };

  // Currency data
  currencyData = {
    gold: 0,
    gems: 0
  };

  // Chart data with proper Chart.js typing
  wildcardChartData: ChartData<'pie'> = {
    labels: ['Common', 'Uncommon', 'Rare', 'Mythic'],
    datasets: [{
      data: [0, 0, 0, 0],
      backgroundColor: [
        '#A0A0A0',  // Common - Gray
        '#808080',  // Uncommon - Silver
        '#D4AF37',  // Rare - Gold
        '#B94E31'   // Mythic - Orange/Red
      ],
      borderColor: '#ffffff',
      borderWidth: 2
    }]
  };

  // Chart options with proper typing
  wildcardChartOptions: ChartOptions<'pie'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'bottom',
        labels: {
          color: '#495057',
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.label || '';
            const value = context.parsed || 0;
            return `${label}: ${value} wildcards`;
          }
        }
      }
    }
  };

  // Loading state
  isLoading = false;

  // Subject for cleanup
  private destroy$ = new Subject<void>();

  constructor(
    private userResourcesService: UserResourcesService,
    private authService: AuthService,
    private messageService: MessageService
  ) {}

  ngOnInit(): void {
    this.loadUserResources();

    // Subscribe to resources changes
    this.userResourcesService.resources$
      .pipe(takeUntil(this.destroy$))
      .subscribe(resources => {
        if (resources) {
          this.updateComponentData(resources);
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load user resources from backend
   */
  loadUserResources(): void {
    const currentUser = this.authService.currentUserValue;

    // Use a default user ID if not authenticated (for demo purposes)
    // In production, this should redirect to login or show an error
    const userId = String(currentUser?.id || 'demo-user');

    this.isLoading = true;

    this.userResourcesService.getUserResources(userId).subscribe({
      next: (resources) => {
        this.updateComponentData(resources);
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading user resources:', error);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Failed to load user resources'
        });
        this.isLoading = false;
      }
    });
  }

  /**
   * Update component data from UserResources
   */
  private updateComponentData(resources: UserResources): void {
    // Update wildcard data
    this.wildcardData = this.userResourcesService.toWildcardData(resources);

    // Update currency data
    this.currencyData = {
      gold: resources.gold,
      gems: resources.gems
    };

    // Update chart data
    this.updateChartData();
  }

  /**
   * Update chart data based on current wildcard data
   */
  private updateChartData(): void {
    this.wildcardChartData = {
      labels: ['Common', 'Uncommon', 'Rare', 'Mythic'],
      datasets: [{
        data: [
          this.wildcardData.common.current,
          this.wildcardData.uncommon.current,
          this.wildcardData.rare.current,
          this.wildcardData.mythic.current
        ],
        backgroundColor: [
          '#A0A0A0',  // Common - Gray
          '#808080',  // Uncommon - Silver
          '#D4AF37',  // Rare - Gold
          '#B94E31'   // Mythic - Orange/Red
        ],
        borderColor: '#ffffff',
        borderWidth: 2
      }]
    };
  }

  /**
   * Get wildcard progress value for progress bar
   */
  getWildcardProgressValue(type: WildcardType): number {
    const data = this.wildcardData[type];
    if (data.total === 0) {
      return 0;
    }
    return (data.current / data.total) * 100;
  }

  /**
   * Get severity color for progress bar based on percentage
   */
  getProgressSeverity(type: WildcardType): 'success' | 'info' | 'warning' | 'danger' {
    const percentage = this.getWildcardProgressValue(type);
    if (percentage >= 75) return 'success';
    if (percentage >= 50) return 'info';
    if (percentage >= 25) return 'warning';
    return 'danger';
  }

  /**
   * Refresh resources from backend
   */
  refreshResources(): void {
    this.loadUserResources();
  }
}