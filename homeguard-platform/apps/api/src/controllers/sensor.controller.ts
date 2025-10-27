import { Request, Response } from 'express';
import prisma from '@/config/database';
import { AppError, asyncHandler } from '@/middleware/error.middleware';
import { ApiResponse, PaginatedResponse } from '@homeguard/types';

export const getSensorData = asyncHandler(async (req: Request, res: Response) => {
  const page = parseInt(req.query.page as string) || 1;
  const pageSize = parseInt(req.query.pageSize as string) || 20;
  const deviceId = req.query.deviceId as string;
  const sensorType = req.query.sensorType as string;

  const where: any = {};
  if (deviceId) where.deviceId = deviceId;
  if (sensorType) where.sensorType = sensorType;

  const [data, total] = await Promise.all([
    prisma.sensorData.findMany({
      where,
      skip: (page - 1) * pageSize,
      take: pageSize,
      orderBy: { timestamp: 'desc' },
    }),
    prisma.sensorData.count({ where }),
  ]);

  const paginatedResponse: PaginatedResponse<typeof data[0]> = {
    items: data,
    total,
    page,
    pageSize,
    hasNext: page * pageSize < total,
    hasPrevious: page > 1,
  };

  const response: ApiResponse = {
    success: true,
    data: paginatedResponse,
    timestamp: new Date(),
  };

  res.json(response);
});

export const getSensorHistory = asyncHandler(
  async (req: Request, res: Response) => {
    const deviceId = req.query.deviceId as string;
    const sensorType = req.query.sensorType as string;
    const startDate = req.query.startDate as string;
    const endDate = req.query.endDate as string;

    if (!deviceId || !sensorType) {
      throw new AppError(
        400,
        'MISSING_PARAMS',
        'deviceId and sensorType are required'
      );
    }

    const where: any = { deviceId, sensorType };

    if (startDate || endDate) {
      where.timestamp = {};
      if (startDate) where.timestamp.gte = new Date(startDate);
      if (endDate) where.timestamp.lte = new Date(endDate);
    }

    const data = await prisma.sensorData.findMany({
      where,
      orderBy: { timestamp: 'asc' },
      take: 1000, // Limit to 1000 records
    });

    const response: ApiResponse = {
      success: true,
      data: {
        deviceId,
        sensorType,
        count: data.length,
        readings: data,
      },
      timestamp: new Date(),
    };

    res.json(response);
  }
);

export const getLatestReading = asyncHandler(
  async (req: Request, res: Response) => {
    const { deviceId } = req.params;
    const sensorType = req.query.sensorType as string;

    const where: any = { deviceId };
    if (sensorType) where.sensorType = sensorType;

    const latestReadings = await prisma.sensorData.findMany({
      where,
      orderBy: { timestamp: 'desc' },
      take: sensorType ? 1 : 10,
    });

    if (latestReadings.length === 0) {
      throw new AppError(404, 'NO_DATA', 'No sensor data found');
    }

    const response: ApiResponse = {
      success: true,
      data: sensorType ? latestReadings[0] : latestReadings,
      timestamp: new Date(),
    };

    res.json(response);
  }
);