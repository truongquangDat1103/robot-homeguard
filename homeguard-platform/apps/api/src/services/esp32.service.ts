import prisma from '@/config/database';
import redisClient from '@/config/redis';
import { logger } from '@/utils/logger';
import { SensorReading, RobotStatus, SensorType } from '@homeguard/types';
import { isValidSensorValue } from '@homeguard/utils';

// Save sensor data to database
export const saveSensorData = async (data: SensorReading | SensorReading[]) => {
  const readings = Array.isArray(data) ? data : [data];

  // Validate sensor values
  const validReadings = readings.filter((reading) => {
    const isValid = isValidSensorValue(reading.type, reading.value);
    if (!isValid) {
      logger.warn(`Invalid sensor value: ${reading.type} = ${reading.value}`);
    }
    return isValid;
  });

  if (validReadings.length === 0) {
    logger.warn('No valid sensor readings to save');
    return;
  }

  // Save to database
  await prisma.sensorData.createMany({
    data: validReadings.map((reading) => ({
      deviceId: reading.deviceId,
      sensorType: reading.type as any,
      value: reading.value,
      unit: reading.unit,
      timestamp: reading.timestamp,
    })),
  });

  // Cache latest readings in Redis
  for (const reading of validReadings) {
    const cacheKey = `sensor:latest:${reading.deviceId}:${reading.type}`;
    await redisClient.set(cacheKey, JSON.stringify(reading), {
      EX: 3600, // 1 hour expiry
    });
  }

  logger.debug(`Saved ${validReadings.length} sensor readings`);
};

// Get latest sensor reading from cache or DB
export const getLatestSensorReading = async (
  deviceId: string,
  sensorType: SensorType
): Promise<SensorReading | null> => {
  // Try cache first
  const cacheKey = `sensor:latest:${deviceId}:${sensorType}`;
  const cached = await redisClient.get(cacheKey);

  if (cached) {
    return JSON.parse(cached);
  }

  // Fallback to database
  const dbReading = await prisma.sensorData.findFirst({
    where: { deviceId, sensorType: sensorType as any },
    orderBy: { timestamp: 'desc' },
  });

  if (!dbReading) return null;

  const reading: SensorReading = {
    id: dbReading.id,
    type: dbReading.sensorType as SensorType,
    value: dbReading.value,
    unit: dbReading.unit,
    timestamp: dbReading.timestamp,
    deviceId: dbReading.deviceId,
  };

  return reading;
};

// Save robot status
export const saveRobotStatus = async (deviceId: string, status: RobotStatus) => {
  // Cache in Redis
  const cacheKey = `robot:status:${deviceId}`;
  await redisClient.set(cacheKey, JSON.stringify(status), {
    EX: 300, // 5 minutes expiry
  });

  // Log behavior if state changed
  const prevStatus = await redisClient.get(`robot:prev_status:${deviceId}`);
  
  if (!prevStatus || JSON.parse(prevStatus).state !== status.state) {
    await prisma.behaviorLog.create({
      data: {
        robotId: deviceId,
        behavior: status.state,
        description: `Robot state changed to ${status.state}`,
        metadata: {
          emotion: status.emotion,
          battery: status.battery,
          position: status.position,
        },
      },
    });
  }

  // Update previous status
  await redisClient.set(`robot:prev_status:${deviceId}`, JSON.stringify(status), {
    EX: 300,
  });

  logger.debug(`Saved robot status for ${deviceId}`);
};

// Get robot status from cache
export const getRobotStatus = async (deviceId: string): Promise<RobotStatus | null> => {
  const cacheKey = `robot:status:${deviceId}`;
  const cached = await redisClient.get(cacheKey);

  return cached ? JSON.parse(cached) : null;
};

// Check sensor thresholds and create alerts
export const checkSensorThresholds = async (reading: SensorReading) => {
  // This would check against configured thresholds
  // For now, simple example:
  if (reading.type === SensorType.TEMPERATURE && reading.value > 35) {
    logger.warn(`High temperature alert: ${reading.value}°C`);
    // Could create alert in DB or send notification
  }

  if (reading.type === SensorType.GAS && reading.value > 500) {
    logger.error(`Gas leak detected: ${reading.value} ppm`);
    // Critical alert
  }
};