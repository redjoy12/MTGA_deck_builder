import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StrategySelectorComponent } from './strategy-selector.component';

describe('StrategySelectorComponent', () => {
  let component: StrategySelectorComponent;
  let fixture: ComponentFixture<StrategySelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StrategySelectorComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(StrategySelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
