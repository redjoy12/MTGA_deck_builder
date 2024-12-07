import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ResourceManagerComponent } from './resource-manager.component';

describe('ResourceManagerComponent', () => {
  let component: ResourceManagerComponent;
  let fixture: ComponentFixture<ResourceManagerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ResourceManagerComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ResourceManagerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
