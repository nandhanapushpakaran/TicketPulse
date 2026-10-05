import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { Router } from '@angular/router';
import { AuthService } from './auth.service';
import { environment } from '../../../environments/environment';
import { User, LoginResponse } from '../../shared/models/user.model';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;
  let mockRouter: jasmine.SpyObj<Router>;

  const mockUser: User = {
    id: 1,
    email: 'test@ticketpulse.local',
    first_name: 'Test',
    last_name: 'User',
    full_name: 'Test User',
    role: 'USER',
    is_active: true,
    is_staff: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  beforeEach(() => {
    localStorage.clear();
    mockRouter = jasmine.createSpyObj('Router', ['navigate']);

    TestBed.configureTestingModule({
      providers: [
        AuthService,
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: Router, useValue: mockRouter }
      ]
    });

    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('should be created and default to unauthenticated', () => {
    expect(service).toBeTruthy();
    expect(service.isAuthenticated()).toBeFalse();
    expect(service.currentUser()).toBeNull();
  });

  it('should store tokens and update signals on successful login', () => {
    const mockResponse: LoginResponse = {
      access: 'access-jwt-token-123',
      refresh: 'refresh-jwt-token-456',
      user: mockUser
    };

    service.login({ email: 'test@ticketpulse.local', password: 'password123' }).subscribe((res) => {
      expect(res.user.email).toBe('test@ticketpulse.local');
    });

    const req = httpMock.expectOne(`${environment.apiUrl}/auth/login/`);
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);

    expect(localStorage.getItem('tp_access_token')).toBe('access-jwt-token-123');
    expect(service.isAuthenticated()).toBeTrue();
    expect(service.currentUser()?.email).toBe('test@ticketpulse.local');
  });

  it('should clear session and redirect to login on logout', () => {
    localStorage.setItem('tp_access_token', 'sample-token');
    service.logout();

    expect(localStorage.getItem('tp_access_token')).toBeNull();
    expect(service.isAuthenticated()).toBeFalse();
    expect(mockRouter.navigate).toHaveBeenCalledWith(['/auth/login']);
  });
});
