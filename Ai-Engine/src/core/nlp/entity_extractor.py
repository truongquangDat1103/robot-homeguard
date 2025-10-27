"""
Entity Extractor - Trích xuất Named Entities từ text.
Nhận diện người, địa điểm, thời gian, số lượng, v.v.
"""
import re
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from loguru import logger


class Entity:
    """Đại diện cho một entity."""
    
    def __init__(
        self,
        text: str,
        type: str,
        value: Any,
        confidence: float = 1.0
    ):
        """
        Khởi tạo Entity.
        
        Args:
            text: Text gốc
            type: Loại entity (person, location, time, ...)
            value: Giá trị đã parse
            confidence: Độ tin cậy
        """
        self.text = text
        self.type = type
        self.value = value
        self.confidence = confidence
    
    def __repr__(self) -> str:
        return f"Entity({self.type}: {self.text} = {self.value})"


class EntityExtractor:
    """
    Trích xuất entities từ text sử dụng regex và rules.
    """
    
    # Patterns cho các entity types
    TIME_PATTERNS = {
        'hour': r'\b(\d{1,2})\s*(giờ|h|hour)\b',
        'time': r'\b(\d{1,2}):(\d{2})\b',
        'relative': r'\b(hôm nay|ngày mai|hôm qua|tuần sau|tháng sau)\b'
    }
    
    NUMBER_PATTERNS = {
        'integer': r'\b(\d+)\b',
        'float': r'\b(\d+\.\d+)\b',
        'percentage': r'\b(\d+)\s*(%|phần trăm|percent)\b'
    }
    
    DURATION_PATTERNS = {
        'minutes': r'\b(\d+)\s*(phút|minute|minutes)\b',
        'hours': r'\b(\d+)\s*(giờ|hour|hours)\b',
        'days': r'\b(\d+)\s*(ngày|day|days)\b'
    }
    
    def __init__(self):
        """Khởi tạo Entity Extractor."""
        logger.info("Entity Extractor đã khởi tạo")
    
    def extract_all(self, text: str) -> List[Entity]:
        """
        Trích xuất tất cả entities từ text.
        
        Args:
            text: Input text
            
        Returns:
            List entities
        """
        entities = []
        
        # Extract time entities
        entities.extend(self.extract_time(text))
        
        # Extract number entities
        entities.extend(self.extract_numbers(text))
        
        # Extract duration entities
        entities.extend(self.extract_durations(text))
        
        # Extract location entities
        entities.extend(self.extract_locations(text))
        
        # Extract device entities
        entities.extend(self.extract_devices(text))
        
        return entities
    
    def extract_time(self, text: str) -> List[Entity]:
        """
        Trích xuất time entities.
        
        Args:
            text: Input text
            
        Returns:
            List time entities
        """
        entities = []
        
        # Relative time
        relative_map = {
            'hôm nay': datetime.now(),
            'ngày mai': datetime.now() + timedelta(days=1),
            'hôm qua': datetime.now() - timedelta(days=1),
            'tuần sau': datetime.now() + timedelta(weeks=1),
            'tháng sau': datetime.now() + timedelta(days=30)
        }
        
        for keyword, dt_value in relative_map.items():
            if keyword in text.lower():
                entities.append(Entity(
                    text=keyword,
                    type='time',
                    value=dt_value,
                    confidence=0.9
                ))
        
        # Absolute time (HH:MM)
        time_pattern = self.TIME_PATTERNS['time']
        for match in re.finditer(time_pattern, text):
            hour, minute = match.groups()
            entities.append(Entity(
                text=match.group(0),
                type='time',
                value={'hour': int(hour), 'minute': int(minute)},
                confidence=0.95
            ))
        
        return entities
    
    def extract_numbers(self, text: str) -> List[Entity]:
        """
        Trích xuất số từ text.
        
        Args:
            text: Input text
            
        Returns:
            List number entities
        """
        entities = []
        
        # Percentage
        perc_pattern = self.NUMBER_PATTERNS['percentage']
        for match in re.finditer(perc_pattern, text):
            value = int(match.group(1))
            entities.append(Entity(
                text=match.group(0),
                type='percentage',
                value=value,
                confidence=1.0
            ))
        
        # Float
        float_pattern = self.NUMBER_PATTERNS['float']
        for match in re.finditer(float_pattern, text):
            value = float(match.group(0))
            entities.append(Entity(
                text=match.group(0),
                type='number',
                value=value,
                confidence=1.0
            ))
        
        # Integer (nếu chưa match percentage hoặc float)
        int_pattern = self.NUMBER_PATTERNS['integer']
        existing_texts = {e.text for e in entities}
        for match in re.finditer(int_pattern, text):
            if match.group(0) not in existing_texts:
                value = int(match.group(0))
                entities.append(Entity(
                    text=match.group(0),
                    type='number',
                    value=value,
                    confidence=1.0
                ))
        
        return entities
    
    def extract_durations(self, text: str) -> List[Entity]:
        """
        Trích xuất duration entities.
        
        Args:
            text: Input text
            
        Returns:
            List duration entities
        """
        entities = []
        
        duration_types = {
            'minutes': ('phút', 'minute', 'minutes'),
            'hours': ('giờ', 'hour', 'hours'),
            'days': ('ngày', 'day', 'days')
        }
        
        for duration_type, keywords in duration_types.items():
            pattern = rf'\b(\d+)\s*({"|".join(keywords)})\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                value = int(match.group(1))
                entities.append(Entity(
                    text=match.group(0),
                    type='duration',
                    value={duration_type: value},
                    confidence=0.95
                ))
        
        return entities
    
    def extract_locations(self, text: str) -> List[Entity]:
        """
        Trích xuất location entities.
        
        Args:
            text: Input text
            
        Returns:
            List location entities
        """
        entities = []
        
        # Danh sách locations thường gặp
        locations = [
            'phòng khách', 'phòng ngủ', 'bếp', 'nhà tắm',
            'sân', 'vườn', 'tầng 1', 'tầng 2',
            'living room', 'bedroom', 'kitchen', 'bathroom'
        ]
        
        text_lower = text.lower()
        for location in locations:
            if location in text_lower:
                entities.append(Entity(
                    text=location,
                    type='location',
                    value=location,
                    confidence=0.8
                ))
        
        return entities
    
    def extract_devices(self, text: str) -> List[Entity]:
        """
        Trích xuất device entities.
        
        Args:
            text: Input text
            
        Returns:
            List device entities
        """
        entities = []
        
        # Danh sách devices
        devices = [
            'đèn', 'quạt', 'tivi', 'tv', 'điều hòa', 'ac',
            'cửa', 'cửa sổ', 'rèm', 'camera',
            'light', 'fan', 'television', 'air conditioner', 'door', 'window'
        ]
        
        text_lower = text.lower()
        for device in devices:
            pattern = rf'\b{device}\b'
            if re.search(pattern, text_lower):
                entities.append(Entity(
                    text=device,
                    type='device',
                    value=device,
                    confidence=0.85
                ))
        
        return entities
    
    def extract_by_type(self, text: str, entity_type: str) -> List[Entity]:
        """
        Trích xuất entities theo loại cụ thể.
        
        Args:
            text: Input text
            entity_type: Loại entity ('time', 'number', 'location', ...)
            
        Returns:
            List entities
        """
        if entity_type == 'time':
            return self.extract_time(text)
        elif entity_type == 'number':
            return self.extract_numbers(text)
        elif entity_type == 'duration':
            return self.extract_durations(text)
        elif entity_type == 'location':
            return self.extract_locations(text)
        elif entity_type == 'device':
            return self.extract_devices(text)
        else:
            return []
    
    def get_entities_dict(self, entities: List[Entity]) -> Dict[str, List]:
        """
        Convert list entities sang dictionary grouped by type.
        
        Args:
            entities: List entities
            
        Returns:
            Dictionary {type: [entities]}
        """
        result = {}
        for entity in entities:
            if entity.type not in result:
                result[entity.type] = []
            result[entity.type].append(entity)
        return result
    
    def get_info(self) -> dict:
        """
        Lấy thông tin extractor.
        
        Returns:
            Dictionary thông tin
        """
        return {
            "supported_types": [
                "time", "number", "percentage", "duration",
                "location", "device"
            ]
        }