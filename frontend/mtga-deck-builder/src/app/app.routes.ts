import { Routes } from '@angular/router';
import { DeckCreatorComponent } from './pages/deck-creator/deck-creator.component';
import { CardSelectorComponent } from './pages/card-selector/card-selector.component';
import { DeckPreviewComponent } from './pages/deck-preview/deck-preview.component';
import { ResourceManagerComponent } from './pages/resource-manager/resource-manager.component';

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