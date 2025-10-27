/**
 * Auth Middleware - Xác thực JWT token
 */

import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { AppError } from './error.middleware';
import prisma from '@/config/database';

interface JwtPayload {
  userId: string;
  email: string;
  role: string;
}

declare global {
  namespace Express {
    interface Request {
      user?: {
        id: string;
        email: string;
        role: string;
      };
    }
  }
}

/**
 * Middleware xác thực JWT token
 */
export const authMiddleware = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    // Lấy token từ header
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new AppError(401, 'UNAUTHORIZED', 'No token provided');
    }

    const token = authHeader.split(' ')[1];
    const secret = process.env.JWT_SECRET;

    if (!secret) {
      throw new AppError(500, 'SERVER_ERROR', 'JWT secret not configured');
    }

    // Verify token
    const decoded = jwt.verify(token, secret) as JwtPayload;

    // Kiểm tra user còn tồn tại không
    const user = await prisma.user.findUnique({
      where: { id: decoded.userId },
      select: { id: true, email: true, role: true },
    });

    if (!user) {
      throw new AppError(401, 'UNAUTHORIZED', 'User not found');
    }

    // Gắn user vào request
    req.user = user;
    next();
  } catch (error) {
    if (error instanceof jwt.JsonWebTokenError) {
      return next(new AppError(401, 'UNAUTHORIZED', 'Invalid token'));
    }
    if (error instanceof jwt.TokenExpiredError) {
      return next(new AppError(401, 'UNAUTHORIZED', 'Token expired'));
    }
    next(error);
  }
};

/**
 * Middleware kiểm tra role
 */
export const requireRole = (roles: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return next(new AppError(401, 'UNAUTHORIZED', 'Authentication required'));
    }

    if (!roles.includes(req.user.role)) {
      return next(
        new AppError(403, 'FORBIDDEN', 'Insufficient permissions')
      );
    }

    next();
  };
};