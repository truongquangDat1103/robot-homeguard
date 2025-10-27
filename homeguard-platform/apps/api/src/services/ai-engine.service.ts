import redisClient from '@/config/redis';
import { logger } from '@/utils/logger';

interface FaceDetectionData {
  faces: Array<{
    id?: string;
    name?: string;
    confidence: number;
    bbox: { x: number; y: number; width: number; height: number };
  }>;
  timestamp: Date;
  imageUrl?: string;
}

interface MotionDetectionData {
  detected: boolean;
  confidence: number;
  regions: Array<{
    x: number;
    y: number;
    width: number;
    height: number;
  }>;
  timestamp: Date;
}

interface AIResultData {
  type: string;
  result: any;
  confidence: number;
  timestamp: Date;
}

// Process face detection results
export const processFaceDetection = async (data: FaceDetectionData) => {
  logger.debug('Processing face detection', { faceCount: data.faces.length });

  // Check for unknown faces (security alert)
  const unknownFaces = data.faces.filter((face) => !face.name || face.name === 'unknown');
  
  let actionRequired = false;
  let action = null;
  let parameters = {};

  if (unknownFaces.length > 0 && unknownFaces[0].confidence > 0.8) {
    logger.warn('Unknown face detected with high confidence');
    actionRequired = true;
    action = 'alert';
    parameters = {
      type: 'unknown_face',
      confidence: unknownFaces[0].confidence,
      bbox: unknownFaces[0].bbox,
    };
  }

  // Cache detected faces
  const cacheKey = `ai:faces:${Date.now()}`;
  await redisClient.set(cacheKey, JSON.stringify(data), {
    EX: 3600, // 1 hour
  });

  // Update face detection stats
  const statsKey = 'ai:stats:face_detection';
  await redisClient.incr(statsKey);

  return {
    faces: data.faces,
    unknownCount: unknownFaces.length,
    knownCount: data.faces.length - unknownFaces.length,
    actionRequired,
    action,
    parameters,
    timestamp: data.timestamp,
  };
};

// Process motion detection results
export const processMotionDetection = async (data: MotionDetectionData) => {
  logger.debug('Processing motion detection', { detected: data.detected });

  if (data.detected && data.confidence > 0.7) {
    logger.info('Motion detected with high confidence');

    // Cache motion event
    const cacheKey = `ai:motion:${Date.now()}`;
    await redisClient.set(cacheKey, JSON.stringify(data), {
      EX: 1800, // 30 minutes
    });

    // Update motion detection stats
    await redisClient.incr('ai:stats:motion_detection');
  }

  return {
    detected: data.detected,
    confidence: data.confidence,
    regions: data.regions,
    timestamp: data.timestamp,
  };
};

// Process generic AI results
export const processAIResult = async (data: AIResultData) => {
  logger.debug('Processing AI result', { type: data.type });

  // Cache result
  const cacheKey = `ai:result:${data.type}:${Date.now()}`;
  await redisClient.set(cacheKey, JSON.stringify(data), {
    EX: 3600, // 1 hour
  });

  // Update AI stats
  await redisClient.incr(`ai:stats:${data.type}`);

  return {
    type: data.type,
    result: data.result,
    confidence: data.confidence,
    timestamp: data.timestamp,
  };
};

// Get AI Engine statistics
export const getAIStats = async () => {
  const faceDetections = await redisClient.get('ai:stats:face_detection') || '0';
  const motionDetections = await redisClient.get('ai:stats:motion_detection') || '0';

  return {
    faceDetections: parseInt(faceDetections),
    motionDetections: parseInt(motionDetections),
  };
};

// Get recent face detections
export const getRecentFaceDetections = async (limit: number = 10) => {
  const keys = await redisClient.keys('ai:faces:*');
  const sortedKeys = keys.sort().reverse().slice(0, limit);

  const detections = await Promise.all(
    sortedKeys.map(async (key) => {
      const data = await redisClient.get(key);
      return data ? JSON.parse(data) : null;
    })
  );

  return detections.filter(Boolean);
};