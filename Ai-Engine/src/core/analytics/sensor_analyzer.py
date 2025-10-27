"""
Sensor Analyzer - Phân tích dữ liệu từ sensors.
Thu thập, xử lý và phân tích dữ liệu time-series từ các sensors.
"""
from typing import Dict, List, Optional, Tuple
from collections import deque
import time
import numpy as np
from loguru import logger


class SensorReading:
    """Đại diện cho một sensor reading."""
    
    def __init__(
        self,
        sensor_id: str,
        value: float,
        unit: str = "",
        timestamp: Optional[float] = None
    ):
        """
        Khởi tạo SensorReading.
        
        Args:
            sensor_id: ID của sensor
            value: Giá trị đo được
            unit: Đơn vị
            timestamp: Thời gian
        """
        self.sensor_id = sensor_id
        self.value = value
        self.unit = unit
        self.timestamp = timestamp or time.time()


class SensorStats:
    """Statistics của sensor."""
    
    def __init__(self):
        """Khởi tạo SensorStats."""
        self.count = 0
        self.min_value = float('inf')
        self.max_value = float('-inf')
        self.sum = 0.0
        self.sum_squared = 0.0
    
    def update(self, value: float) -> None:
        """
        Cập nhật statistics.
        
        Args:
            value: Giá trị mới
        """
        self.count += 1
        self.min_value = min(self.min_value, value)
        self.max_value = max(self.max_value, value)
        self.sum += value
        self.sum_squared += value ** 2
    
    @property
    def mean(self) -> float:
        """Tính mean."""
        return self.sum / self.count if self.count > 0 else 0.0
    
    @property
    def variance(self) -> float:
        """Tính variance."""
        if self.count < 2:
            return 0.0
        mean = self.mean
        return (self.sum_squared / self.count) - (mean ** 2)
    
    @property
    def std(self) -> float:
        """Tính standard deviation."""
        return np.sqrt(self.variance)


class SensorAnalyzer:
    """
    Phân tích dữ liệu sensors.
    """
    
    def __init__(
        self,
        buffer_size: int = 1000,
        sampling_rate: float = 1.0  # Hz
    ):
        """
        Khởi tạo Sensor Analyzer.
        
        Args:
            buffer_size: Kích thước buffer cho mỗi sensor
            sampling_rate: Tần số lấy mẫu (Hz)
        """
        self.buffer_size = buffer_size
        self.sampling_rate = sampling_rate
        
        # Buffers cho từng sensor
        self.buffers: Dict[str, deque] = {}
        
        # Statistics
        self.stats: Dict[str, SensorStats] = {}
        
        # Thresholds cho alerts
        self.thresholds: Dict[str, Tuple[float, float]] = {}  # (min, max)
        
        logger.info("Sensor Analyzer đã khởi tạo")
    
    def add_reading(
        self,
        sensor_id: str,
        value: float,
        unit: str = ""
    ) -> None:
        """
        Thêm sensor reading mới.
        
        Args:
            sensor_id: ID của sensor
            value: Giá trị
            unit: Đơn vị
        """
        reading = SensorReading(sensor_id, value, unit)
        
        # Khởi tạo buffer nếu chưa có
        if sensor_id not in self.buffers:
            self.buffers[sensor_id] = deque(maxlen=self.buffer_size)
            self.stats[sensor_id] = SensorStats()
        
        # Thêm vào buffer
        self.buffers[sensor_id].append(reading)
        
        # Update statistics
        self.stats[sensor_id].update(value)
        
        # Kiểm tra threshold
        self._check_threshold(sensor_id, value)
    
    def get_readings(
        self,
        sensor_id: str,
        count: Optional[int] = None
    ) -> List[SensorReading]:
        """
        Lấy readings của sensor.
        
        Args:
            sensor_id: ID của sensor
            count: Số lượng readings (None = tất cả)
            
        Returns:
            List readings
        """
        if sensor_id not in self.buffers:
            return []
        
        readings = list(self.buffers[sensor_id])
        
        if count:
            readings = readings[-count:]
        
        return readings
    
    def get_values(
        self,
        sensor_id: str,
        count: Optional[int] = None
    ) -> np.ndarray:
        """
        Lấy values của sensor dạng array.
        
        Args:
            sensor_id: ID sensor
            count: Số lượng
            
        Returns:
            Numpy array
        """
        readings = self.get_readings(sensor_id, count)
        return np.array([r.value for r in readings])
    
    def get_statistics(self, sensor_id: str) -> Optional[Dict]:
        """
        Lấy statistics của sensor.
        
        Args:
            sensor_id: ID sensor
            
        Returns:
            Dictionary statistics
        """
        if sensor_id not in self.stats:
            return None
        
        stats = self.stats[sensor_id]
        
        return {
            'count': stats.count,
            'min': stats.min_value,
            'max': stats.max_value,
            'mean': stats.mean,
            'std': stats.std,
            'variance': stats.variance
        }
    
    def calculate_moving_average(
        self,
        sensor_id: str,
        window_size: int = 10
    ) -> Optional[float]:
        """
        Tính moving average.
        
        Args:
            sensor_id: ID sensor
            window_size: Kích thước window
            
        Returns:
            Moving average value
        """
        values = self.get_values(sensor_id, count=window_size)
        
        if len(values) < window_size:
            return None
        
        return float(np.mean(values))
    
    def detect_spike(
        self,
        sensor_id: str,
        threshold_factor: float = 3.0
    ) -> bool:
        """
        Phát hiện spike (giá trị bất thường).
        
        Args:
            sensor_id: ID sensor
            threshold_factor: Hệ số ngưỡng (x std)
            
        Returns:
            True nếu có spike
        """
        if sensor_id not in self.buffers or len(self.buffers[sensor_id]) < 10:
            return False
        
        values = self.get_values(sensor_id)
        
        # Lấy giá trị gần nhất
        latest_value = values[-1]
        
        # Tính mean và std của 90% data trước đó
        historical_values = values[:-max(1, len(values)//10)]
        
        if len(historical_values) < 5:
            return False
        
        mean = np.mean(historical_values)
        std = np.std(historical_values)
        
        # Kiểm tra spike
        if abs(latest_value - mean) > threshold_factor * std:
            logger.warning(f"⚠️  Spike detected in {sensor_id}: {latest_value:.2f}")
            return True
        
        return False
    
    def calculate_trend(
        self,
        sensor_id: str,
        window_size: int = 50
    ) -> Optional[float]:
        """
        Tính xu hướng (tăng/giảm).
        
        Args:
            sensor_id: ID sensor
            window_size: Kích thước window
            
        Returns:
            Trend slope (dương = tăng, âm = giảm)
        """
        values = self.get_values(sensor_id, count=window_size)
        
        if len(values) < 10:
            return None
        
        # Linear regression
        x = np.arange(len(values))
        
        # Calculate slope
        slope = np.polyfit(x, values, 1)[0]
        
        return float(slope)
    
    def set_threshold(
        self,
        sensor_id: str,
        min_value: float,
        max_value: float
    ) -> None:
        """
        Set threshold cho sensor.
        
        Args:
            sensor_id: ID sensor
            min_value: Giá trị tối thiểu
            max_value: Giá trị tối đa
        """
        self.thresholds[sensor_id] = (min_value, max_value)
        logger.info(f"Threshold set for {sensor_id}: [{min_value}, {max_value}]")
    
    def _check_threshold(self, sensor_id: str, value: float) -> None:
        """Kiểm tra threshold."""
        if sensor_id not in self.thresholds:
            return
        
        min_val, max_val = self.thresholds[sensor_id]
        
        if value < min_val:
            logger.warning(f"⚠️  {sensor_id} dưới ngưỡng: {value:.2f} < {min_val:.2f}")
        elif value > max_val:
            logger.warning(f"⚠️  {sensor_id} vượt ngưỡng: {value:.2f} > {max_val:.2f}")
    
    def calculate_correlation(
        self,
        sensor_id1: str,
        sensor_id2: str,
        window_size: int = 100
    ) -> Optional[float]:
        """
        Tính correlation giữa 2 sensors.
        
        Args:
            sensor_id1: ID sensor 1
            sensor_id2: ID sensor 2
            window_size: Kích thước window
            
        Returns:
            Correlation coefficient (-1 đến 1)
        """
        values1 = self.get_values(sensor_id1, count=window_size)
        values2 = self.get_values(sensor_id2, count=window_size)
        
        if len(values1) < 10 or len(values2) < 10:
            return None
        
        # Lấy chiều dài ngắn hơn
        min_len = min(len(values1), len(values2))
        values1 = values1[-min_len:]
        values2 = values2[-min_len:]
        
        # Tính correlation
        correlation = np.corrcoef(values1, values2)[0, 1]
        
        return float(correlation)
    
    def get_all_sensors(self) -> List[str]:
        """Lấy danh sách tất cả sensors."""
        return list(self.buffers.keys())
    
    def clear_sensor(self, sensor_id: str) -> None:
        """
        Xóa dữ liệu của sensor.
        
        Args:
            sensor_id: ID sensor
        """
        if sensor_id in self.buffers:
            self.buffers[sensor_id].clear()
            self.stats[sensor_id] = SensorStats()
            logger.info(f"Đã xóa dữ liệu sensor: {sensor_id}")
    
    def get_info(self) -> dict:
        """
        Lấy thông tin analyzer.
        
        Returns:
            Dictionary thông tin
        """
        return {
            "sensor_count": len(self.buffers),
            "sensors": self.get_all_sensors(),
            "buffer_size": self.buffer_size,
            "sampling_rate": self.sampling_rate,
            "total_readings": sum(len(buf) for buf in self.buffers.values())
        }