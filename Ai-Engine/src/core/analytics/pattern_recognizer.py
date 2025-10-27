"""
Pattern Recognizer - Nhận diện các patterns trong dữ liệu.
Phát hiện chu kỳ, xu hướng, và patterns lặp lại.
"""
from typing import List, Dict, Optional, Tuple
import numpy as np
from loguru import logger


class Pattern:
    """Đại diện cho một pattern được phát hiện."""
    
    def __init__(
        self,
        pattern_type: str,
        confidence: float,
        parameters: Dict,
        description: str = ""
    ):
        """
        Khởi tạo Pattern.
        
        Args:
            pattern_type: Loại pattern
            confidence: Độ tin cậy
            parameters: Parameters của pattern
            description: Mô tả
        """
        self.pattern_type = pattern_type
        self.confidence = confidence
        self.parameters = parameters
        self.description = description


class PatternRecognizer:
    """
    Nhận diện patterns trong time-series data.
    """
    
    def __init__(self):
        """Khởi tạo Pattern Recognizer."""
        # Detected patterns
        self.patterns: List[Pattern] = []
        
        logger.info("Pattern Recognizer đã khởi tạo")
    
    def detect_trend(
        self,
        values: np.ndarray,
        min_confidence: float = 0.6
    ) -> Optional[Pattern]:
        """
        Phát hiện trend (xu hướng).
        
        Args:
            values: Array giá trị
            min_confidence: Confidence tối thiểu
            
        Returns:
            Pattern hoặc None
        """
        if len(values) < 10:
            return None
        
        # Linear regression
        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)
        slope, intercept = coeffs
        
        # Predicted values
        predicted = slope * x + intercept
        
        # R-squared
        ss_res = np.sum((values - predicted) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        
        if ss_tot == 0:
            return None
        
        r_squared = 1 - (ss_res / ss_tot)
        
        if r_squared < min_confidence:
            return None
        
        # Xác định trend direction
        if abs(slope) < 0.01:
            trend_type = "stable"
        elif slope > 0:
            trend_type = "increasing"
        else:
            trend_type = "decreasing"
        
        pattern = Pattern(
            pattern_type="trend",
            confidence=r_squared,
            parameters={
                'slope': slope,
                'intercept': intercept,
                'trend_type': trend_type
            },
            description=f"Trend {trend_type} (slope: {slope:.4f})"
        )
        
        logger.info(f"✅ Phát hiện trend: {trend_type} (confidence: {r_squared:.2f})")
        return pattern
    
    def detect_periodicity(
        self,
        values: np.ndarray,
        min_confidence: float = 0.7
    ) -> Optional[Pattern]:
        """
        Phát hiện periodicity (chu kỳ) bằng autocorrelation.
        
        Args:
            values: Array giá trị
            min_confidence: Confidence tối thiểu
            
        Returns:
            Pattern hoặc None
        """
        if len(values) < 20:
            return None
        
        # Normalize
        normalized = (values - np.mean(values)) / (np.std(values) + 1e-8)
        
        # Autocorrelation
        autocorr = np.correlate(normalized, normalized, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        autocorr = autocorr / autocorr[0]
        
        # Tìm peaks
        peaks = []
        for i in range(1, len(autocorr) - 1):
            if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                if autocorr[i] > min_confidence:
                    peaks.append((i, autocorr[i]))
        
        if not peaks:
            return None
        
        # Lấy peak mạnh nhất
        period, confidence = max(peaks, key=lambda p: p[1])
        
        pattern = Pattern(
            pattern_type="periodic",
            confidence=confidence,
            parameters={
                'period': period,
                'frequency': 1.0 / period
            },
            description=f"Chu kỳ: {period} samples"
        )
        
        logger.info(f"✅ Phát hiện periodicity: period={period} (confidence: {confidence:.2f})")
        return pattern
    
    def detect_spike_pattern(
        self,
        values: np.ndarray,
        threshold: float = 3.0
    ) -> Optional[Pattern]:
        """
        Phát hiện spike pattern (các đỉnh đột biến).
        
        Args:
            values: Array giá trị
            threshold: Ngưỡng (x std)
            
        Returns:
            Pattern hoặc None
        """
        if len(values) < 10:
            return None
        
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return None
        
        # Tìm spikes
        z_scores = np.abs((values - mean) / std)
        spike_indices = np.where(z_scores > threshold)[0]
        
        if len(spike_indices) < 2:
            return None
        
        # Tính khoảng cách giữa các spikes
        intervals = np.diff(spike_indices)
        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        # Nếu intervals tương đối đều -> pattern
        if std_interval / avg_interval < 0.3:  # CV < 0.3
            confidence = 1.0 - (std_interval / avg_interval)
            
            pattern = Pattern(
                pattern_type="spike",
                confidence=confidence,
                parameters={
                    'spike_count': len(spike_indices),
                    'avg_interval': avg_interval,
                    'threshold': threshold
                },
                description=f"{len(spike_indices)} spikes với interval trung bình {avg_interval:.1f}"
            )
            
            logger.info(f"✅ Phát hiện spike pattern: {len(spike_indices)} spikes")
            return pattern
        
        return None
    
    def detect_seasonal(
        self,
        values: np.ndarray,
        season_length: int,
        min_confidence: float = 0.6
    ) -> Optional[Pattern]:
        """
        Phát hiện seasonal pattern.
        
        Args:
            values: Array giá trị
            season_length: Độ dài season
            min_confidence: Confidence tối thiểu
            
        Returns:
            Pattern hoặc None
        """
        if len(values) < season_length * 2:
            return None
        
        # Chia thành các seasons
        n_seasons = len(values) // season_length
        seasons = []
        
        for i in range(n_seasons):
            start = i * season_length
            end = start + season_length
            seasons.append(values[start:end])
        
        # Tính correlation giữa các seasons
        correlations = []
        for i in range(len(seasons) - 1):
            corr = np.corrcoef(seasons[i], seasons[i+1])[0, 1]
            correlations.append(corr)
        
        avg_corr = np.mean(correlations)
        
        if avg_corr < min_confidence:
            return None
        
        # Tính seasonal pattern (trung bình của các seasons)
        seasonal_pattern = np.mean(seasons, axis=0)
        
        pattern = Pattern(
            pattern_type="seasonal",
            confidence=avg_corr,
            parameters={
                'season_length': season_length,
                'n_seasons': n_seasons,
                'seasonal_pattern': seasonal_pattern.tolist()
            },
            description=f"Seasonal với length={season_length}"
        )
        
        logger.info(f"✅ Phát hiện seasonal pattern: length={season_length}")
        return pattern
    
    def detect_change_point(
        self,
        values: np.ndarray,
        min_segment_length: int = 10
    ) -> Optional[Pattern]:
        """
        Phát hiện change point (điểm thay đổi).
        
        Args:
            values: Array giá trị
            min_segment_length: Độ dài segment tối thiểu
            
        Returns:
            Pattern hoặc None
        """
        if len(values) < min_segment_length * 2:
            return None
        
        best_change_point = None
        best_score = 0.0
        
        # Thử từng vị trí có thể
        for i in range(min_segment_length, len(values) - min_segment_length):
            # Chia thành 2 segments
            segment1 = values[:i]
            segment2 = values[i:]
            
            # Tính mean và variance
            mean1, std1 = np.mean(segment1), np.std(segment1)
            mean2, std2 = np.mean(segment2), np.std(segment2)
            
            # Tính difference
            mean_diff = abs(mean1 - mean2)
            
            # Score (normalized)
            overall_std = np.std(values)
            if overall_std > 0:
                score = mean_diff / overall_std
                
                if score > best_score:
                    best_score = score
                    best_change_point = i
        
        if best_score < 1.0:  # Threshold
            return None
        
        confidence = min(best_score / 3.0, 1.0)
        
        pattern = Pattern(
            pattern_type="change_point",
            confidence=confidence,
            parameters={
                'change_point': best_change_point,
                'before_mean': float(np.mean(values[:best_change_point])),
                'after_mean': float(np.mean(values[best_change_point:]))
            },
            description=f"Change point tại index {best_change_point}"
        )
        
        logger.info(f"✅ Phát hiện change point tại {best_change_point}")
        return pattern
    
    def analyze(
        self,
        values: np.ndarray,
        detect_types: Optional[List[str]] = None
    ) -> List[Pattern]:
        """
        Phân tích và phát hiện tất cả patterns.
        
        Args:
            values: Array giá trị
            detect_types: Các loại cần detect (None = tất cả)
            
        Returns:
            List patterns
        """
        if detect_types is None:
            detect_types = ['trend', 'periodic', 'spike', 'change_point']
        
        patterns = []
        
        # Detect trend
        if 'trend' in detect_types:
            trend = self.detect_trend(values)
            if trend:
                patterns.append(trend)
        
        # Detect periodicity
        if 'periodic' in detect_types:
            periodic = self.detect_periodicity(values)
            if periodic:
                patterns.append(periodic)
        
        # Detect spikes
        if 'spike' in detect_types:
            spike = self.detect_spike_pattern(values)
            if spike:
                patterns.append(spike)
        
        # Detect change point
        if 'change_point' in detect_types:
            change = self.detect_change_point(values)
            if change:
                patterns.append(change)
        
        # Lưu vào history
        self.patterns.extend(patterns)
        
        logger.info(f"Phát hiện {len(patterns)} patterns")
        return patterns
    
    def get_dominant_pattern(
        self,
        patterns: List[Pattern]
    ) -> Optional[Pattern]:
        """
        Lấy pattern dominant (confidence cao nhất).
        
        Args:
            patterns: List patterns
            
        Returns:
            Pattern dominant
        """
        if not patterns:
            return None
        
        return max(patterns, key=lambda p: p.confidence)
    
    def clear_history(self) -> None:
        """Xóa pattern history."""
        self.patterns.clear()
        logger.info("Pattern history đã xóa")
    
    def get_info(self) -> dict:
        """
        Lấy thông tin recognizer.
        
        Returns:
            Dictionary thông tin
        """
        return {
            "total_patterns": len(self.patterns),
            "supported_types": ['trend', 'periodic', 'spike', 'seasonal', 'change_point']
        }