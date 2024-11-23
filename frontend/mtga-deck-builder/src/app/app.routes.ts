import { Routes } from '@angular/router';
import { DeckCreatorComponent } from './features/deck-builder/components/deck-creator/deck-creator.component';
import { CardSelectorComponent } from './features/deck-builder/components/card-selector/card-selector.component';
import { DeckPreviewComponent } from './features/deck-builder/components/deck-preview/deck-preview.component';
import { ResourceManagerComponent } from './features/deck-builder/components/resource-manager/resource-manager.component';

export const routes: Routes = [
  { 
    path: 'deck-creator', 
    component: DeckCreatorComponent 
  },
  { 
    path: 'card-selector', 
    component: CardSelectorComponent 
  },
  { 
    path: 'deck-preview', 
    component: DeckPreviewComponent 
  },
  { 
    path: 'resource-manager', 
    component: ResourceManagerComponent 
  },
  { 
    path: '', 
    redirectTo: '/deck-creator', 
    pathMatch: 'full' 
  }
];