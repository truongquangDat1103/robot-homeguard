import { Router } from 'express';
import { login, register, me, refreshToken } from '@/controllers/auth.controller';
import { authMiddleware } from '@/middleware/auth.middleware';

const router = Router();

router.post('/login', login);
router.post('/register', register);
router.post('/refresh', refreshToken);
router.get('/me', authMiddleware, me);

export default router;