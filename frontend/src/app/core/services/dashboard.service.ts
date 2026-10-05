import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { DashboardData, ReportsData } from '../../shared/models/dashboard.model';

export interface ReportsFilterParams {
  date_from?: string;
  date_to?: string;
  status?: string;
  priority?: string;
  category?: string;
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private dashboardUrl = `${environment.apiUrl}/dashboard`;
  private reportsUrl = `${environment.apiUrl}/reports`;

  constructor(private http: HttpClient) {}

  getDashboardData(): Observable<DashboardData> {
    return this.http.get<DashboardData>(`${this.dashboardUrl}/`);
  }

  getReportsData(filters?: ReportsFilterParams): Observable<ReportsData> {
    let params = new HttpParams();
    if (filters) {
      if (filters.date_from) params = params.set('date_from', filters.date_from);
      if (filters.date_to) params = params.set('date_to', filters.date_to);
      if (filters.status) params = params.set('status', filters.status);
      if (filters.priority) params = params.set('priority', filters.priority);
      if (filters.category) params = params.set('category', filters.category);
    }
    return this.http.get<ReportsData>(`${this.reportsUrl}/`, { params });
  }
}
