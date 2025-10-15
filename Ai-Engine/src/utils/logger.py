"""
Thiết lập hệ thống ghi log có cấu trúc sử dụng Loguru.
Cung cấp log có màu trên console và tự động xoay, lưu trữ file log.
"""

import sys
from pathlib import Path
from typing import Optional
from loguru import logger
from config.settings import settings


def setup_logger(
    log_file: Optional[str] = None,
    rotation: str = "10 MB",
    retention: str = "7 days",
    level: str = "INFO"
) -> None:
    """
    Cấu hình hệ thống ghi log (logging) cho toàn dự án.
    
    Chức năng:
        - Ghi log ra màn hình console có màu sắc (dễ đọc)
        - Lưu log vào file có cơ chế tự xoay và nén file
        - Đảm bảo thread-safe khi ghi log song song

    Tham số:
        log_file: Đường dẫn file log (mặc định lấy từ settings)
        rotation: Giới hạn dung lượng hoặc thời gian để xoay log (mặc định: 10 MB)
        retention: Thời gian lưu trữ log trước khi xoá (mặc định: 7 ngày)
        level: Mức độ log (DEBUG, INFO, WARNING, ERROR)
    """
    # Xóa handler mặc định
    logger.remove()
    
    # Ghi log ra console (hiển thị có màu)
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level=level,
        backtrace=True,
        diagnose=True
    )
    
    # Ghi log ra file (tự xoay và lưu trữ)
    if log_file is None:
        log_file = settings.monitoring.log_file
        rotation = settings.monitoring.log_rotation
        retention = settings.monitoring.log_retention
    
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_file,
        rotation=rotation,
        retention=retention,
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=level,
        backtrace=True,
        diagnose=True,
        enqueue=True  # Đảm bảo an toàn khi ghi log từ nhiều luồng
    )
    
    logger.info(f"Đã khởi tạo hệ thống ghi log - Mức: {level}, File: {log_file}")


def get_logger(name: str):
    """
    Lấy một logger riêng biệt theo tên module.
    
    Mục đích:
        - Cho phép các file/module khác sử dụng logger riêng
        - Giúp dễ phân biệt nguồn log khi phân tích
    
    Tham số:
        name: Tên logger (thường truyền __name__)
    
    Trả về:
        Đối tượng logger đã được gắn nhãn tên
    """
    return logger.bind(name=name)


def log_execution_time(func):
    """
    Decorator dùng để ghi lại thời gian thực thi của hàm (đồng bộ).
    
    Mục đích:
        - Theo dõi hiệu năng của từng hàm
        - Hỗ trợ tối ưu và phân tích chậm trễ
    """
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.debug(f"{func.__name__} thực thi trong {elapsed:.4f}s")
        return result
    
    return wrapper


def log_async_execution_time(func):
    """
    Decorator dùng để ghi lại thời gian thực thi của hàm bất đồng bộ (async).
    
    Mục đích:
        - Theo dõi hiệu năng các hàm async (ví dụ trong xử lý IO, WebSocket)
        - Ghi log chi tiết thời gian chạy từng coroutine
    """
    import functools
    import time
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.debug(f"{func.__name__} thực thi trong {elapsed:.4f}s")
        return result
    
    return wrapper


# Tự động khởi tạo logger khi import module này
setup_logger(level=settings.log_level)
