import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { UserRole } from '../../shared/models/user.model';

export const roleGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  const allowedRoles = route.data?.['roles'] as UserRole[] | undefined;
  const currentRole = authService.userRole();

  if (!allowedRoles || allowedRoles.length === 0) {
    return true;
  }

  if (currentRole && allowedRoles.includes(currentRole)) {
    return true;
  }

  // Fallback to dashboard if unauthorized for this specific role
  router.navigate(['/dashboard']);
  return false;
};
