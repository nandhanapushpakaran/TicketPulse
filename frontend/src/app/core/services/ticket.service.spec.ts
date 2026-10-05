import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { TicketService } from './ticket.service';
import { environment } from '../../../environments/environment';
import { Ticket, PaginatedResponse } from '../../shared/models/ticket.model';

describe('TicketService', () => {
  let service: TicketService;
  let httpMock: HttpTestingController;

  const mockTicket: Ticket = {
    id: 10,
    ticket_number: 'TIC-1010',
    title: 'Test issue with database connection',
    description: 'Detailed description of the issue',
    category: 'SOFTWARE',
    priority: 'HIGH',
    status: 'OPEN',
    created_by: {
      id: 1,
      email: 'user@test.local',
      first_name: 'Test',
      last_name: 'User',
      full_name: 'Test User',
      role: 'USER',
      is_active: true,
      is_staff: false,
      created_at: '',
      updated_at: ''
    },
    assigned_to: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    resolved_at: null
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        TicketService,
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    });

    service = TestBed.inject(TicketService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should query tickets with query parameters', () => {
    const mockResponse: PaginatedResponse<Ticket> = {
      count: 1,
      next: null,
      previous: null,
      results: [mockTicket]
    };

    service.getTickets({ status: 'OPEN', priority: 'HIGH' }).subscribe((res) => {
      expect(res.results.length).toBe(1);
      expect(res.results[0].ticket_number).toBe('TIC-1010');
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/tickets/?status=OPEN&priority=HIGH`);
    expect(req.request.method).toBe('GET');
    req.flush(mockResponse);
  });

  it('should submit a new ticket payload via POST', () => {
    const payload = {
      title: 'New Hardware Ticket',
      description: 'Broken display cable',
      category: 'HARDWARE' as const,
      priority: 'MEDIUM' as const
    };

    service.createTicket(payload).subscribe((res) => {
      expect(res.title).toBe(payload.title);
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/tickets/`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(payload);
    req.flush({ ...mockTicket, title: payload.title });
  });
});
