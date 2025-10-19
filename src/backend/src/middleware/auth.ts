import { Request, Response, NextFunction } from 'express';
import { UnauthorizedError } from '../utils/errors';

// Placeholder authentication middleware
// TODO: Implement actual JWT authentication
export const authenticate = (req: Request, res: Response, next: NextFunction) => {
  // For now, attach a mock user to the request
  // In production, this would verify JWT token and attach actual user
  (req as any).user = {
    id: 1,
    email: 'demo@ppcsimulator.com',
    role: 'STUDENT',
  };
  next();
};

// Authorization middleware - check if user has required role
export const authorize = (...allowedRoles: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const user = (req as any).user;
    
    if (!user) {
      throw new UnauthorizedError('Authentication required');
    }
    
    if (allowedRoles.length && !allowedRoles.includes(user.role)) {
      throw new UnauthorizedError('Insufficient permissions');
    }
    
    next();
  };
};
