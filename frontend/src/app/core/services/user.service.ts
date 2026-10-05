import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { User, UserRole } from '../../shared/models/user.model';
import { PaginatedResponse } from '../../shared/models/ticket.model';

export interface UserFilterParams {
  search?: string;
  role?: string;
  is_active?: boolean;
  page?: number;
}

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = `${environment.apiUrl}/users`;

  constructor(private http: HttpClient) {}

  getUsers(filters?: UserFilterParams): Observable<PaginatedResponse<User>> {
    let params = new HttpParams();
    if (filters) {
      if (filters.search) params = params.set('search', filters.search);
      if (filters.role) params = params.set('role', filters.role);
      if (filters.is_active !== undefined) params = params.set('is_active', filters.is_active.toString());
      if (filters.page) params = params.set('page', filters.page.toString());
    }
    return this.http.get<PaginatedResponse<User>>(`${this.apiUrl}/`, { params });
  }

  getAgents(): Observable<User[]> {
    return this.http.get<User[]>(`${this.apiUrl}/agents/`);
  }

  updateUser(id: number, payload: { role?: UserRole; is_active?: boolean }): Observable<User> {
    return this.http.patch<User>(`${this.apiUrl}/${id}/`, payload);
  }
}
