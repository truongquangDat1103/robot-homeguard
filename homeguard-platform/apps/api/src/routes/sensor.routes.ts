import { Router } from 'express';
import {
  getSensorData,
  getSensorHistory,
  getLatestReading,
} from '@/controllers/sensor.controller';
import { authMiddleware } from '@/middleware/auth.middleware';

const router = Router();

// All sensor routes require authentication
router.use(authMiddleware);

router.get('/', getSensorData);
router.get('/history', getSensorHistory);
router.get('/latest/:deviceId', getLatestReading);

export default router;