import { Router } from 'express';
import authRoutes from './auth.routes';
import sensorRoutes from './sensor.routes';

const router: Router = Router();

// Mount routes
router.use('/auth', authRoutes);
router.use('/sensors', sensorRoutes);

export default router;