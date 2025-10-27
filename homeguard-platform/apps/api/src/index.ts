import 'dotenv/config';
import app from './app';
import { createWebSocketServer } from '@/websocket';
import { logger } from '@/utils/logger';
import { connectDatabase } from '@/config/database';
import { connectRedis } from '@/config/redis';

const PORT = process.env.API_PORT || 4000;

async function startServer() {
  try {
    // Connect to database
    await connectDatabase();
    logger.info('✓ Database connected');

    // Connect to Redis
    await connectRedis();
    logger.info('✓ Redis connected');

    // Start HTTP server
    const server = app.listen(PORT, () => {
      logger.info(`✓ API Server running on port ${PORT}`);
      logger.info(`✓ Environment: ${process.env.NODE_ENV}`);
    });

    // Initialize WebSocket server
    createWebSocketServer(server);
    logger.info('✓ WebSocket server initialized');

    // Graceful shutdown
    process.on('SIGTERM', async () => {
      logger.info('SIGTERM received, shutting down gracefully...');
      server.close(() => {
        logger.info('Server closed');
        process.exit(0);
      });
    });
  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
}

startServer();