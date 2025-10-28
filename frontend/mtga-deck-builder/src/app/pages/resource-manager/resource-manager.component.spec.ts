import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { MessageService } from 'primeng/api';

import { ResourceManagerComponent } from './resource-manager.component';
import { UserResourcesService } from '../../core/services/user-resources.service';
import { AuthService } from '../../core/services/auth.service';

describe('ResourceManagerComponent', () => {
  let component: ResourceManagerComponent;
  let fixture: ComponentFixture<ResourceManagerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        ResourceManagerComponent,
        HttpClientTestingModule
      ],
      providers: [
        UserResourcesService,
        AuthService,
        MessageService
      ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ResourceManagerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize with default wildcard data', () => {
    expect(component.wildcardData).toBeDefined();
    expect(component.wildcardData.common).toBeDefined();
    expect(component.wildcardData.uncommon).toBeDefined();
    expect(component.wildcardData.rare).toBeDefined();
    expect(component.wildcardData.mythic).toBeDefined();
  });

  it('should calculate wildcard progress value correctly', () => {
    component.wildcardData.common = { current: 5, total: 10 };
    const progress = component.getWildcardProgressValue('common');
    expect(progress).toBe(50);
  });

  it('should handle zero total in progress calculation', () => {
    component.wildcardData.common = { current: 5, total: 0 };
    const progress = component.getWildcardProgressValue('common');
    expect(progress).toBe(0);
  });
});
