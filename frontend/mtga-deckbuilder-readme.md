# MTGA Deck Builder AI Assistant - Frontend Development Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Setup Instructions](#setup-instructions)
5. [Implementation Guide](#implementation-guide)
6. [Design Guidelines](#design-guidelines)
7. [Component Breakdown](#component-breakdown)
8. [State Management](#state-management)
9. [API Integration](#api-integration)
10. [Authentication & Authorization](#authentication--authorization)

## Project Overview

MTGA Deck Builder AI Assistant is a web application that helps Magic: The Gathering Arena players create optimal decks based on their available resources and preferences. The application provides an intuitive interface for deck building while incorporating AI-powered suggestions.

### Key Features
- Interactive deck building interface
- AI-powered deck suggestions
- Resource management (wildcards, gold, gems)
- Card preview on hover
- Deck history tracking
- Personal card collection management
- User authentication and authorization

## Technology Stack

- **Framework**: Angular 17+
- **UI Components**: PrimeNG 17
- **State Management**: NgRx
- **Styling**: SCSS with Angular Material
- **Authentication**: Auth0/Firebase Authentication
- **HTTP Client**: Angular HttpClient
- **Testing**: Jasmine & Karma
- **Build Tool**: Angular CLI

## Project Structure

```
src/
├── app/
│   ├── core/                 # Singleton services, guards, interceptors
│   │   ├── auth/
│   │   ├── services/
│   │   └── interceptors/
│   ├── shared/              # Shared components, pipes, directives
│   │   ├── components/
│   │   ├── directives/
│   │   └── pipes/
│   ├── features/            # Feature modules
│   │   ├── deck-builder/    # Main deck building feature
│   │   ├── deck-history/    # Deck history feature
│   │   └── card-collection/ # Card collection feature
│   └── store/               # NgRx store configuration
├── assets/
│   ├── images/
│   └── styles/
└── environments/
```

## Setup Instructions

1. Install Angular CLI:
```bash
npm install -g @angular/cli
```

2. Create new Angular project:
```bash
ng new mtga-deck-builder --routing --style scss
```

3. Install required dependencies:
```bash
npm install @angular/material @ngrx/store @ngrx/effects primeng primeicons
```

## Implementation Guide

### 1. Core Module Setup

Create the core module to handle application-wide singleton services:

```bash
ng generate module core
```

Create essential services:
```bash
ng generate service core/services/auth
ng generate service core/services/deck
ng generate service core/services/card
```

### 2. Feature Modules Implementation

#### 2.1 Deck Builder Module

```bash
ng generate module features/deck-builder --routing
```

Components to create:
```bash
ng generate component features/deck-builder/components/deck-creator
ng generate component features/deck-builder/components/card-selector
ng generate component features/deck-builder/components/deck-preview
ng generate component features/deck-builder/components/resource-manager
```

#### 2.2 Deck History Module

```bash
ng generate module features/deck-history --routing
```

#### 2.3 Card Collection Module

```bash
ng generate module features/card-collection --routing
```

### 3. Shared Components

Create reusable components:
```bash
ng generate component shared/components/card-preview
ng generate component shared/components/color-filter
ng generate component shared/components/strategy-selector
```

## Design Guidelines

### Theme Configuration

1. Create a custom theme using Angular Material's theming system:

```scss
// src/styles/theme.scss

@use '@angular/material' as mat;

$primary-palette: mat.define-palette(mat.$deep-purple-palette);
$accent-palette: mat.define-palette(mat.$amber-palette);

$theme: mat.define-light-theme((
  color: (
    primary: $primary-palette,
    accent: $accent-palette,
  )
));
```

### Layout Structure

The application should follow a responsive layout with these key elements:

1. Top Navigation Bar
2. Side Menu (collapsible)
3. Main Content Area
4. Card Preview Overlay

## Component Breakdown

### Main Page (Deck Builder)

```typescript
// deck-builder.component.ts
@Component({
  selector: 'app-deck-builder',
  template: `
    <div class="deck-builder-container">
      <div class="filters-section">
        <app-color-filter />
        <app-strategy-selector />
      </div>
      <div class="main-content">
        <app-card-selector />
        <app-deck-preview />
      </div>
      <div class="resources-section">
        <app-resource-manager />
      </div>
    </div>
  `
})
```

### Card Preview Component

Implementation guidance for card preview on hover:

```typescript
// card-preview.directive.ts
@Directive({
  selector: '[appCardPreview]'
})
export class CardPreviewDirective {
  @Input('appCardPreview') cardId: string;
  
  @HostListener('mouseenter')
  onMouseEnter() {
    // Show card preview
  }
  
  @HostListener('mouseleave')
  onMouseLeave() {
    // Hide card preview
  }
}
```

## State Management

### Store Structure

```typescript
interface AppState {
  auth: AuthState;
  deck: DeckState;
  cards: CardsState;
  resources: ResourcesState;
}

interface DeckState {
  currentDeck: Deck;
  savedDecks: Deck[];
  loading: boolean;
  error: string | null;
}
```

### Actions

Define key actions:
```typescript
export const loadDeck = createAction('[Deck] Load Deck', props<{ deckId: string }>());
export const saveDeck = createAction('[Deck] Save Deck', props<{ deck: Deck }>());
export const updateResources = createAction('[Resources] Update', props<{ resources: Resources }>());
```

## API Integration

Create a service for handling API calls:

```typescript
// deck.service.ts
@Injectable({
  providedIn: 'root'
})
export class DeckService {
  constructor(private http: HttpClient) {}

  getDeck(id: string): Observable<Deck> {
    return this.http.get<Deck>(`/api/decks/${id}`);
  }

  saveDeck(deck: Deck): Observable<Deck> {
    return this.http.post<Deck>('/api/decks', deck);
  }
}
```

## Authentication & Authorization

1. Implement Auth Guard:
```typescript
// auth.guard.ts
@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  canActivate(): Observable<boolean> {
    // Implement authentication logic
  }
}
```

2. Configure routes with guard:
```typescript
const routes: Routes = [
  {
    path: 'deck-builder',
    component: DeckBuilderComponent,
    canActivate: [AuthGuard]
  }
];
```

## Development Workflow

1. Start with core module implementation
2. Implement authentication
3. Create shared components
4. Develop feature modules one by one
5. Integrate state management
6. Add API integration
7. Implement card preview functionality
8. Add final styling and animations

## Testing Strategy

Create comprehensive tests for:
- Components
- Services
- State management
- Guards
- API integration

Example test:
```typescript
describe('DeckBuilderComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DeckBuilderComponent ],
      imports: [ SharedModule, StoreModule.forRoot({}) ]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(DeckBuilderComponent);
    const component = fixture.componentInstance;
    expect(component).toBeTruthy();
  });
});
```

## Deployment Considerations

1. Environment configuration
2. Production build optimization
3. CDN setup for assets
4. Error handling and logging
5. Performance monitoring

## Next Steps

1. Set up the project structure
2. Install dependencies
3. Implement core module
4. Create authentication system
5. Develop shared components
6. Implement feature modules
7. Add state management
8. Style the application
9. Test and deploy

Remember to follow Angular best practices and coding standards throughout the development process. Regular code reviews and testing will ensure high-quality implementation.
