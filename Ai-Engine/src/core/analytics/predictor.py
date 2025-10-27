"""
Predictor - Dự đoán giá trị tương lai.
Sử dụng time-series forecasting methods.
"""
from typing import Optional, Tuple
import numpy as np
from loguru import logger


class Prediction:
    """Đại diện cho một prediction."""
    
    def __init__(
        self,
        predicted_value: float,
        confidence_interval: Tuple[float, float],
        method: str
    ):
        """
        Khởi tạo Prediction.
        
        Args:
            predicted_value: Giá trị dự đoán
            confidence_interval: Khoảng tin cậy (lower, upper)
            method: Phương pháp dự đoán
        """
        self.predicted_value = predicted_value
        self.confidence_interval = confidence_interval
        self.method = method


class Predictor:
    """
    Dự đoán giá trị tương lai cho time-series data.
    """
    
    def __init__(self):
        """Khởi tạo Predictor."""
        logger.info("Predictor đã khởi tạo")
    
    def predict_moving_average(
        self,
        values: np.ndarray,
        window_size: int = 10,
        steps_ahead: int = 1
    ) -> Optional[Prediction]:
        """
        Dự đoán bằng Moving Average.
        
        Args:
            values: Historical values
            window_size: Kích thước window
            steps_ahead: Số bước dự đoán
            
        Returns:
            Prediction
        """
        if len(values) < window_size:
            return None
        
        # Tính moving average
        recent_values = values[-window_size:]
        predicted = np.mean(recent_values)
        
        # Tính confidence interval (dựa trên std)
        std = np.std(recent_values)
        lower = predicted - 1.96 * std  # 95% CI
        upper = predicted + 1.96 * std
        
        prediction = Prediction(
            predicted_value=float(predicted),
            confidence_interval=(float(lower), float(upper)),
            method="moving_average"
        )
        
        logger.debug(f"Prediction (MA): {predicted:.2f} [{lower:.2f}, {upper:.2f}]")
        return prediction
    
    def predict_exponential_smoothing(
        self,
        values: np.ndarray,
        alpha: float = 0.3,
        steps_ahead: int = 1
    ) -> Optional[Prediction]:
        """
        Dự đoán bằng Exponential Smoothing.
        
        Args:
            values: Historical values
            alpha: Smoothing parameter (0-1)
            steps_ahead: Số bước dự đoán
            
        Returns:
            Prediction
        """
        if len(values) < 2:
            return None
        
        # Simple exponential smoothing
        smoothed = [values[0]]
        
        for i in range(1, len(values)):
            s = alpha * values[i] + (1 - alpha) * smoothed[-1]
            smoothed.append(s)
        
        predicted = smoothed[-1]
        
        # Tính error để estimate confidence
        errors = values[1:] - np.array(smoothed[:-1])
        std_error = np.std(errors)
        
        lower = predicted - 1.96 * std_error
        upper = predicted + 1.96 * std_error
        
        prediction = Prediction(
            predicted_value=float(predicted),
            confidence_interval=(float(lower), float(upper)),
            method="exponential_smoothing"
        )
        
        logger.debug(f"Prediction (ES): {predicted:.2f}")
        return prediction
    
    def predict_linear_trend(
        self,
        values: np.ndarray,
        steps_ahead: int = 1
    ) -> Optional[Prediction]:
        """
        Dự đoán bằng Linear Trend.
        
        Args:
            values: Historical values
            steps_ahead: Số bước dự đoán
            
        Returns:
            Prediction
        """
        if len(values) < 10:
            return None
        
        # Linear regression
        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)
        slope, intercept = coeffs
        
        # Predict
        next_x = len(values) + steps_ahead - 1
        predicted = slope * next_x + intercept
        
        # Tính residuals để estimate confidence
        fitted = slope * x + intercept
        residuals = values - fitted
        std_residual = np.std(residuals)
        
        lower = predicted - 1.96 * std_residual
        upper = predicted + 1.96 * std_residual
        
        prediction = Prediction(
            predicted_value=float(predicted),
            confidence_interval=(float(lower), float(upper)),
            method="linear_trend"
        )
        
        logger.debug(f"Prediction (Linear): {predicted:.2f}")
        return prediction
    
    def predict_last_value(
        self,
        values: np.ndarray
    ) -> Optional[Prediction]:
        """
        Dự đoán đơn giản = giá trị cuối cùng (baseline).
        
        Args:
            values: Historical values
            
        Returns:
            Prediction
        """
        if len(values) == 0:
            return None
        
        predicted = values[-1]
        
        # Confidence dựa trên volatility gần đây
        if len(values) > 10:
            recent_std = np.std(values[-10:])
        else:
            recent_std = np.std(values)
        
        lower = predicted - 1.96 * recent_std
        upper = predicted + 1.96 * recent_std
        
        prediction = Prediction(
            predicted_value=float(predicted),
            confidence_interval=(float(lower), float(upper)),
            method="last_value"
        )
        
        return prediction
    
    def predict_ensemble(
        self,
        values: np.ndarray,
        steps_ahead: int = 1
    ) -> Optional[Prediction]:
        """
        Ensemble prediction (kết hợp nhiều methods).
        
        Args:
            values: Historical values
            steps_ahead: Số bước dự đoán
            
        Returns:
            Prediction
        """
        predictions = []
        
        # Thử các methods
        methods = [
            self.predict_moving_average,
            self.predict_exponential_smoothing,
            self.predict_linear_trend,
            self.predict_last_value
        ]
        
        for method in methods:
            try:
                pred = method(values, steps_ahead=steps_ahead) if 'steps_ahead' in method.__code__.co_varnames else method(values)
                if pred:
                    predictions.append(pred)
            except:
                pass
        
        if not predictions:
            return None
        
        # Weighted average (weight by inverse of CI width)
        weights = []
        for pred in predictions:
            ci_width = pred.confidence_interval[1] - pred.confidence_interval[0]
            weight = 1.0 / (ci_width + 1e-8)
            weights.append(weight)
        
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        # Ensemble prediction
        ensemble_value = sum(
            pred.predicted_value * weight
            for pred, weight in zip(predictions, weights)
        )
        
        # Ensemble confidence interval
        ensemble_lower = sum(
            pred.confidence_interval[0] * weight
            for pred, weight in zip(predictions, weights)
        )
        
        ensemble_upper = sum(
            pred.confidence_interval[1] * weight
            for pred, weight in zip(predictions, weights)
        )
        
        prediction = Prediction(
            predicted_value=float(ensemble_value),
            confidence_interval=(float(ensemble_lower), float(ensemble_upper)),
            method="ensemble"
        )
        
        logger.info(f"Ensemble prediction: {ensemble_value:.2f}")
        return prediction
    
    def get_info(self) -> dict:
        """
        Lấy thông tin predictor.
        
        Returns:
            Dictionary thông tin
        """
        return {
            "methods": [
                "moving_average",
                "exponential_smoothing",
                "linear_trend",
                "last_value",
                "ensemble"
            ]
        }