import { Request, Response } from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { z } from 'zod';
import prisma from '@/config/database';
import { AppError, asyncHandler } from '@/middleware/error.middleware';
import { ApiResponse, AuthTokens } from '@homeguard/types';

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
});

const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  name: z.string().min(2),
});

const generateTokens = (userId: string, email: string, role: string): AuthTokens => {
  const secret = process.env.JWT_SECRET;

  if (!secret) {
    throw new Error('JWT_SECRET is not defined');
  }

  const expiresIn = process.env.JWT_EXPIRES_IN || '7d';

  // Calculate expiresIn in seconds for the response
  const expiresInSeconds = expiresIn === '7d' ? 7 * 24 * 60 * 60 : 7 * 24 * 60 * 60;

  const accessToken = jwt.sign(
    { userId, email, role },
    secret,
    { expiresIn }
  );

  const refreshToken = jwt.sign(
    { userId, type: 'refresh' },
    secret,
    { expiresIn: '30d' }
  );

  return {
    accessToken,
    refreshToken,
    expiresIn: expiresInSeconds,
  };
};

export const login = asyncHandler(async (req: Request, res: Response) => {
  const { email, password } = loginSchema.parse(req.body);

  const user = await prisma.user.findUnique({ where: { email } });

  if (!user) {
    throw new AppError(401, 'INVALID_CREDENTIALS', 'Invalid email or password');
  }

  const isValidPassword = await bcrypt.compare(password, user.password);

  if (!isValidPassword) {
    throw new AppError(401, 'INVALID_CREDENTIALS', 'Invalid email or password');
  }

  const tokens = generateTokens(user.id, user.email, user.role);

  const response: ApiResponse = {
    success: true,
    data: {
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
      },
      tokens,
    },
    timestamp: new Date(),
  };

  res.json(response);
});

export const register = asyncHandler(async (req: Request, res: Response) => {
  const { email, password, name } = registerSchema.parse(req.body);

  const existingUser = await prisma.user.findUnique({ where: { email } });

  if (existingUser) {
    throw new AppError(400, 'USER_EXISTS', 'Email already registered');
  }

  const hashedPassword = await bcrypt.hash(password, 10);

  const user = await prisma.user.create({
    data: {
      email,
      password: hashedPassword,
      name,
      role: 'USER',
    },
  });

  const tokens = generateTokens(user.id, user.email, user.role);

  const response: ApiResponse = {
    success: true,
    data: {
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
      },
      tokens,
    },
    timestamp: new Date(),
  };

  res.status(201).json(response);
});

export const me = asyncHandler(async (req: Request, res: Response) => {
  if (!req.user) {
    throw new AppError(401, 'UNAUTHORIZED', 'Authentication required');
  }

  const user = await prisma.user.findUnique({
    where: { id: req.user.id },
    select: {
      id: true,
      email: true,
      name: true,
      role: true,
      createdAt: true,
    },
  });

  const response: ApiResponse = {
    success: true,
    data: { user },
    timestamp: new Date(),
  };

  res.json(response);
});

export const refreshToken = asyncHandler(async (req: Request, res: Response) => {
  const { refreshToken } = req.body;

  if (!refreshToken) {
    throw new AppError(400, 'MISSING_TOKEN', 'Refresh token required');
  }

  const secret = process.env.JWT_SECRET;

  if (!secret) {
    throw new AppError(500, 'SERVER_ERROR', 'JWT secret not configured');
  }

  try {
    const decoded = jwt.verify(refreshToken, secret) as jwt.JwtPayload & {
      userId: string;
      type?: string;
    };

    if (decoded.type !== 'refresh') {
      throw new AppError(400, 'INVALID_TOKEN', 'Invalid token type');
    }

    const user = await prisma.user.findUnique({
      where: { id: decoded.userId },
    });

    if (!user) {
      throw new AppError(404, 'USER_NOT_FOUND', 'User not found');
    }

    const tokens = generateTokens(user.id, user.email, user.role);

    const response: ApiResponse = {
      success: true,
      data: { tokens },
      timestamp: new Date(),
    };

    res.json(response);
  } catch (error) {
    if (error instanceof jwt.JsonWebTokenError) {
      throw new AppError(401, 'INVALID_TOKEN', 'Invalid or expired refresh token');
    }
    throw error;
  }
});