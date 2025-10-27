import { SensorType } from '@homeguard/types';

export const isValidEmail = (email: string): boolean => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
};

export const isValidSensorValue = (
  type: SensorType,
  value: number
): boolean => {
  switch (type) {
    case SensorType.TEMPERATURE:
      return value >= -50 && value <= 100;
    case SensorType.HUMIDITY:
      return value >= 0 && value <= 100;
    case SensorType.LIGHT:
      return value >= 0 && value <= 1023;
    case SensorType.DISTANCE:
      return value >= 0 && value <= 400;
    case SensorType.GAS:
      return value >= 0 && value <= 1000;
    case SensorType.SOUND:
      return value >= 0 && value <= 1023;
    default:
      return true;
  }
};

export const validateJsonPayload = <T>(
  payload: unknown,
  requiredFields: string[]
): { valid: boolean; missing?: string[] } => {
  if (typeof payload !== 'object' || payload === null) {
    return { valid: false };
  }

  const missing = requiredFields.filter(
    (field) => !(field in (payload as Record<string, unknown>))
  );

  return missing.length === 0 ? { valid: true } : { valid: false, missing };
};

export const isValidDeviceId = (deviceId: string): boolean => {
  return /^[a-zA-Z0-9_-]{8,32}$/.test(deviceId);
};

export const sanitizeString = (input: string): string => {
  return input.replace(/[<>'"]/g, '');
};