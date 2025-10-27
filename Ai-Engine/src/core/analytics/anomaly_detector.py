"""
Anomaly Detector - Phát hiện các bất thường trong dữ liệu.
Sử dụng statistical methods và machine learning.
"""
from typing import List, Dict, Optional, Tuple
import numpy as np
from loguru import logger


class Anomaly:
    """Đại diện cho một anomaly được phát hiện."""
    
    def __init__(
        self,
        timestamp: float,
        value: float,
        score: float,
        method: str,
        description: str = ""
    ):
        """
        Khởi tạo Anomaly.
        
        Args:
            timestamp: Thời gian
            value: Giá trị bất thường
            score: Anomaly score (0.0 - 1.0)
            method: Phương pháp phát hiện
            description: Mô tả
        """
        self.timestamp = timestamp
        self.value = value
        self.score = score
        self.method = method
        self.description = description


class AnomalyDetector:
    """
    Phát hiện anomalies sử dụng statistical methods.
    """
    
    def __init__(
        self,
        sensitivity: float = 0.7,
        z_score_threshold: float = 3.0
    ):
        """
        Khởi tạo Anomaly Detector.
        
        Args:
            sensitivity: Độ nhạy (0.0 - 1.0)
            z_score_threshold: Ngưỡng Z-score
        """
        self.sensitivity = sensitivity
        self.z_score_threshold = z_score_threshold
        
        # Detected anomalies
        self.anomalies: List[Anomaly] = []
        self.max_anomaly_history = 1000
        
        logger.info("Anomaly Detector đã khởi tạo")
    
    def detect_zscore(
        self,
        values: np.ndarray,
        timestamps: Optional[np.ndarray] = None
    ) -> List[Anomaly]:
        """
        Phát hiện anomalies bằng Z-score method.
        
        Args:
            values: Array giá trị
            timestamps: Array timestamps
            
        Returns:
            List anomalies
        """
        if len(values) < 10:
            return []
        
        anomalies = []
        
        # Tính mean và std
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return []
        
        # Tính Z-scores
        z_scores = np.abs((values - mean) / std)
        
        # Tìm anomalies
        anomaly_indices = np.where(z_scores > self.z_score_threshold)[0]
        
        for idx in anomaly_indices:
            score = min(z_scores[idx] / (self.z_score_threshold * 2), 1.0)
            
            timestamp = timestamps[idx] if timestamps is not None else float(idx)
            
            anomaly = Anomaly(
                timestamp=timestamp,
                value=values[idx],
                score=score,
                method="z-score",
                description=f"Z-score: {z_scores[idx]:.2f}"
            )
            
            anomalies.append(anomaly)
        
        logger.debug(f"Phát hiện {len(anomalies)} anomalies (Z-score)")
        return anomalies
    
    def detect_iqr(
        self,
        values: np.ndarray,
        timestamps: Optional[np.ndarray] = None
    ) -> List[Anomaly]:
        """
        Phát hiện anomalies bằng IQR (Interquartile Range) method.
        
        Args:
            values: Array giá trị
            timestamps: Array timestamps
            
        Returns:
            List anomalies
        """
        if len(values) < 10:
            return []
        
        anomalies = []
        
        # Tính quartiles
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1
        
        if iqr == 0:
            return []
        
        # Tính bounds
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Tìm outliers
        outlier_mask = (values < lower_bound) | (values > upper_bound)
        outlier_indices = np.where(outlier_mask)[0]
        
        for idx in outlier_indices:
            value = values[idx]
            
            # Tính score
            if value < lower_bound:
                distance = lower_bound - value
            else:
                distance = value - upper_bound
            
            score = min(distance / iqr, 1.0)
            
            timestamp = timestamps[idx] if timestamps is not None else float(idx)
            
            anomaly = Anomaly(
                timestamp=timestamp,
                value=value,
                score=score,
                method="iqr",
                description=f"Outside bounds: [{lower_bound:.2f}, {upper_bound:.2f}]"
            )
            
            anomalies.append(anomaly)
        
        logger.debug(f"Phát hiện {len(anomalies)} anomalies (IQR)")
        return anomalies
    
    def detect_moving_average(
        self,
        values: np.ndarray,
        window_size: int = 20,
        threshold_factor: float = 2.0,
        timestamps: Optional[np.ndarray] = None
    ) -> List[Anomaly]:
        """
        Phát hiện anomalies bằng Moving Average method.
        
        Args:
            values: Array giá trị
            window_size: Kích thước window
            threshold_factor: Hệ số ngưỡng
            timestamps: Array timestamps
            
        Returns:
            List anomalies
        """
        if len(values) < window_size * 2:
            return []
        
        anomalies = []
        
        # Tính moving average
        moving_avg = np.convolve(values, np.ones(window_size)/window_size, mode='valid')
        
        # Tính moving std
        moving_std = np.array([
            np.std(values[max(0, i-window_size):i+1])
            for i in range(window_size-1, len(values))
        ])
        
        # Tìm anomalies
        for i in range(len(moving_avg)):
            actual_idx = i + window_size - 1
            deviation = abs(values[actual_idx] - moving_avg[i])
            
            if moving_std[i] > 0 and deviation > threshold_factor * moving_std[i]:
                score = min(deviation / (threshold_factor * moving_std[i]), 1.0)
                
                timestamp = timestamps[actual_idx] if timestamps is not None else float(actual_idx)
                
                anomaly = Anomaly(
                    timestamp=timestamp,
                    value=values[actual_idx],
                    score=score,
                    method="moving-average",
                    description=f"Deviation: {deviation:.2f}"
                )
                
                anomalies.append(anomaly)
        
        logger.debug(f"Phát hiện {len(anomalies)} anomalies (Moving Average)")
        return anomalies
    
    def detect_all(
        self,
        values: np.ndarray,
        timestamps: Optional[np.ndarray] = None,
        methods: Optional[List[str]] = None
    ) -> List[Anomaly]:
        """
        Phát hiện anomalies bằng nhiều methods.
        
        Args:
            values: Array giá trị
            timestamps: Array timestamps
            methods: Danh sách methods ('zscore', 'iqr', 'moving-average')
            
        Returns:
            List anomalies (merged và sorted)
        """
        if methods is None:
            methods = ['zscore', 'iqr', 'moving-average']
        
        all_anomalies = []
        
        if 'zscore' in methods:
            all_anomalies.extend(self.detect_zscore(values, timestamps))
        
        if 'iqr' in methods:
            all_anomalies.extend(self.detect_iqr(values, timestamps))
        
        if 'moving-average' in methods:
            all_anomalies.extend(self.detect_moving_average(values, timestamps=timestamps))
        
        # Merge anomalies gần nhau
        merged_anomalies = self._merge_anomalies(all_anomalies)
        
        # Add vào history
        self.anomalies.extend(merged_anomalies)
        if len(self.anomalies) > self.max_anomaly_history:
            self.anomalies = self.anomalies[-self.max_anomaly_history:]
        
        return merged_anomalies
    
    def _merge_anomalies(
        self,
        anomalies: List[Anomaly],
        time_threshold: float = 1.0
    ) -> List[Anomaly]:
        """
        Merge các anomalies gần nhau.
        
        Args:
            anomalies: List anomalies
            time_threshold: Ngưỡng thời gian
            
        Returns:
            List merged anomalies
        """
        if not anomalies:
            return []
        
        # Sort by timestamp
        sorted_anomalies = sorted(anomalies, key=lambda a: a.timestamp)
        
        merged = [sorted_anomalies[0]]
        
        for anomaly in sorted_anomalies[1:]:
            last = merged[-1]
            
            # Nếu gần nhau về thời gian
            if abs(anomaly.timestamp - last.timestamp) < time_threshold:
                # Giữ anomaly có score cao hơn
                if anomaly.score > last.score:
                    merged[-1] = anomaly
            else:
                merged.append(anomaly)
        
        return merged
    
    def is_anomalous(
        self,
        value: float,
        historical_values: np.ndarray,
        method: str = 'zscore'
    ) -> Tuple[bool, float]:
        """
        Kiểm tra một giá trị có phải anomaly không.
        
        Args:
            value: Giá trị cần kiểm tra
            historical_values: Dữ liệu lịch sử
            method: Method sử dụng
            
        Returns:
            (is_anomalous, anomaly_score)
        """
        if len(historical_values) < 10:
            return False, 0.0
        
        if method == 'zscore':
            mean = np.mean(historical_values)
            std = np.std(historical_values)
            
            if std == 0:
                return False, 0.0
            
            z_score = abs((value - mean) / std)
            
            is_anomalous = z_score > self.z_score_threshold
            score = min(z_score / (self.z_score_threshold * 2), 1.0)
            
            return is_anomalous, score
        
        elif method == 'iqr':
            q1 = np.percentile(historical_values, 25)
            q3 = np.percentile(historical_values, 75)
            iqr = q3 - q1
            
            if iqr == 0:
                return False, 0.0
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            is_anomalous = value < lower_bound or value > upper_bound
            
            if value < lower_bound:
                score = min((lower_bound - value) / iqr, 1.0)
            elif value > upper_bound:
                score = min((value - upper_bound) / iqr, 1.0)
            else:
                score = 0.0
            
            return is_anomalous, score
        
        return False, 0.0
    
    def get_anomaly_rate(
        self,
        total_samples: int
    ) -> float:
        """
        Tính tỷ lệ anomaly.
        
        Args:
            total_samples: Tổng số samples
            
        Returns:
            Tỷ lệ (0.0 - 1.0)
        """
        if total_samples == 0:
            return 0.0
        
        return len(self.anomalies) / total_samples
    
    def get_recent_anomalies(self, count: int = 10) -> List[Anomaly]:
        """
        Lấy anomalies gần đây.
        
        Args:
            count: Số lượng
            
        Returns:
            List anomalies
        """
        return self.anomalies[-count:]
    
    def clear_history(self) -> None:
        """Xóa anomaly history."""
        self.anomalies.clear()
        logger.info("Anomaly history đã xóa")
    
    def get_info(self) -> dict:
        """
        Lấy thông tin detector.
        
        Returns:
            Dictionary thông tin
        """
        return {
            "sensitivity": self.sensitivity,
            "z_score_threshold": self.z_score_threshold,
            "total_anomalies": len(self.anomalies),
            "methods": ['zscore', 'iqr', 'moving-average']
        }