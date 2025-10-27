// Parse face detection results from AI engine
export const parseFaceDetection = (rawData: any) => {
  // Example: Convert from AI engine format to our format
  return {
    faces: rawData.detections?.map((detection: any) => ({
      id: detection.id,
      name: detection.label || 'unknown',
      confidence: detection.confidence,
      bbox: {
        x: detection.bbox[0],
        y: detection.bbox[1],
        width: detection.bbox[2],
        height: detection.bbox[3],
      },
    })) || [],
    timestamp: new Date(rawData.timestamp || Date.now()),
    imageUrl: rawData.image_url,
  };
};

// Parse motion detection results
export const parseMotionDetection = (rawData: any) => {
  return {
    detected: rawData.motion_detected || false,
    confidence: rawData.confidence || 0,
    regions: rawData.regions?.map((region: any) => ({
      x: region.x,
      y: region.y,
      width: region.width,
      height: region.height,
    })) || [],
    timestamp: new Date(rawData.timestamp || Date.now()),
  };
};

// Parse object detection results
export const parseObjectDetection = (rawData: any) => {
  return {
    objects: rawData.objects?.map((obj: any) => ({
      class: obj.class,
      confidence: obj.confidence,
      bbox: {
        x: obj.bbox[0],
        y: obj.bbox[1],
        width: obj.bbox[2],
        height: obj.bbox[3],
      },
    })) || [],
    timestamp: new Date(rawData.timestamp || Date.now()),
  };
};

// Validate face detection data
export const validateFaceDetection = (data: any): boolean => {
  if (!data || typeof data !== 'object') return false;
  if (!Array.isArray(data.faces)) return false;
  
  return data.faces.every((face: any) => 
    typeof face.confidence === 'number' &&
    face.confidence >= 0 &&
    face.confidence <= 1 &&
    face.bbox &&
    typeof face.bbox.x === 'number' &&
    typeof face.bbox.y === 'number'
  );
};

// Validate motion detection data
export const validateMotionDetection = (data: any): boolean => {
  if (!data || typeof data !== 'object') return false;
  if (typeof data.detected !== 'boolean') return false;
  if (typeof data.confidence !== 'number') return false;
  
  return true;
};