import { ComponentFixture, TestBed } from '@angular/core/testing';
import { StatusBadgeComponent } from './status-badge.component';

describe('StatusBadgeComponent', () => {
  let component: StatusBadgeComponent;
  let fixture: ComponentFixture<StatusBadgeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StatusBadgeComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(StatusBadgeComponent);
    component = fixture.componentInstance;
  });

  it('should create the status badge', () => {
    component.status = 'NEW';
    fixture.detectChanges();
    expect(component).toBeTruthy();
    expect(component.statusClass).toBe('status-new');
    expect(component.statusLabel).toBe('New');
  });

  it('should map IN_PROGRESS properly', () => {
    component.status = 'IN_PROGRESS';
    fixture.detectChanges();
    expect(component.statusClass).toBe('status-in-progress');
    expect(component.statusLabel).toBe('In Progress');
  });

  it('should map RESOLVED properly', () => {
    component.status = 'RESOLVED';
    fixture.detectChanges();
    expect(component.statusClass).toBe('status-resolved');
    expect(component.statusLabel).toBe('Resolved');
  });
});
