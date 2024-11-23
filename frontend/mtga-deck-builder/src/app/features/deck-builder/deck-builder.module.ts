import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';

// Routing Module
import { DeckBuilderRoutingModule } from './deck-builder-routing.module';

// Components
import { DeckCreatorComponent } from './components/deck-creator/deck-creator.component';
import { CardSelectorComponent } from './components/card-selector/card-selector.component';
import { DeckPreviewComponent } from './components/deck-preview/deck-preview.component';
import { ResourceManagerComponent } from './components/resource-manager/resource-manager.component';

// Shared Components (if needed in this module)
import { CardPreviewComponent } from '../../shared/components/card-preview/card-preview.component';
import { ColorFilterComponent } from '../../shared/components/color-filter/color-filter.component';
import { StrategySelectorComponent } from '../../shared/components/strategy-selector/strategy-selector.component';

@NgModule({
  declarations: [
    // Deck Builder Specific Components
    DeckCreatorComponent,
    CardSelectorComponent,
    DeckPreviewComponent,
    ResourceManagerComponent,

    // Shared Components (if they are used exclusively in this module)
    CardPreviewComponent,
    ColorFilterComponent,
    StrategySelectorComponent
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    DeckBuilderRoutingModule
  ],
  exports: [
    // Components that might be used in parent components
    DeckCreatorComponent,
    CardSelectorComponent,
    DeckPreviewComponent,
    ResourceManagerComponent
  ]
})
export class DeckBuilderModule { }