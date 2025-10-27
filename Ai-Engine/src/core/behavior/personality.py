"""
Personality - Tính cách và đặc điểm cá nhân của robot.
Ảnh hưởng đến cách robot phản ứng và giao tiếp.
"""
from typing import Dict, Optional
from loguru import logger


class PersonalityTrait:
    """Đại diện cho một personality trait."""
    
    def __init__(
        self,
        name: str,
        value: float,
        description: str = ""
    ):
        """
        Khởi tạo PersonalityTrait.
        
        Args:
            name: Tên trait
            value: Giá trị (0.0 - 1.0)
            description: Mô tả
        """
        self.name = name
        self.value = max(0.0, min(1.0, value))
        self.description = description
    
    def __repr__(self) -> str:
        return f"PersonalityTrait({self.name}: {self.value:.2f})"


class Personality:
    """
    Tính cách của robot dựa trên Big Five personality model.
    """
    
    # Personality presets
    PRESETS = {
        'friendly': {
            'openness': 0.7,
            'conscientiousness': 0.6,
            'extraversion': 0.8,
            'agreeableness': 0.9,
            'emotional_stability': 0.7,
            'politeness': 0.8,
            'humor': 0.6,
            'curiosity': 0.7,
            'patience': 0.7,
            'empathy': 0.8
        },
        'professional': {
            'openness': 0.6,
            'conscientiousness': 0.9,
            'extraversion': 0.5,
            'agreeableness': 0.7,
            'emotional_stability': 0.8,
            'politeness': 0.9,
            'humor': 0.3,
            'curiosity': 0.6,
            'patience': 0.8,
            'empathy': 0.6
        },
        'playful': {
            'openness': 0.9,
            'conscientiousness': 0.5,
            'extraversion': 0.9,
            'agreeableness': 0.8,
            'emotional_stability': 0.6,
            'politeness': 0.6,
            'humor': 0.9,
            'curiosity': 0.9,
            'patience': 0.5,
            'empathy': 0.7
        }
    }
    
    def __init__(self, preset: str = 'friendly'):
        """
        Khởi tạo Personality.
        
        Args:
            preset: Preset name ('friendly', 'professional', 'playful')
        """
        self.preset = preset
        
        # Khởi tạo traits
        self.traits: Dict[str, PersonalityTrait] = {}
        
        # Load preset
        if preset in self.PRESETS:
            self._load_preset(preset)
        else:
            logger.warning(f"Preset không tồn tại: {preset}, dùng 'friendly'")
            self._load_preset('friendly')
        
        logger.info(f"Personality đã khởi tạo (preset: {preset})")
    
    def _load_preset(self, preset: str) -> None:
        """Load preset values."""
        preset_values = self.PRESETS[preset]
        
        for trait_name, value in preset_values.items():
            self.traits[trait_name] = PersonalityTrait(
                name=trait_name,
                value=value
            )
    
    def get_trait(self, trait_name: str) -> Optional[float]:
        """
        Lấy giá trị của trait.
        
        Args:
            trait_name: Tên trait
            
        Returns:
            Giá trị (0.0 - 1.0) hoặc None
        """
        trait = self.traits.get(trait_name)
        return trait.value if trait else None
    
    def set_trait(self, trait_name: str, value: float) -> None:
        """
        Set giá trị trait.
        
        Args:
            trait_name: Tên trait
            value: Giá trị mới
        """
        if trait_name in self.traits:
            self.traits[trait_name].value = max(0.0, min(1.0, value))
            logger.info(f"Trait '{trait_name}' = {value:.2f}")
        else:
            self.traits[trait_name] = PersonalityTrait(trait_name, value)
    
    def adjust_trait(self, trait_name: str, delta: float) -> None:
        """
        Điều chỉnh trait (tăng/giảm).
        
        Args:
            trait_name: Tên trait
            delta: Giá trị thay đổi
        """
        current = self.get_trait(trait_name)
        if current is not None:
            new_value = max(0.0, min(1.0, current + delta))
            self.set_trait(trait_name, new_value)
    
    def get_response_style(self) -> Dict[str, any]:
        """
        Lấy style phản hồi dựa trên personality.
        
        Returns:
            Dictionary với các thuộc tính response
        """
        return {
            'verbosity': self.get_trait('extraversion'),
            'formality': self.get_trait('conscientiousness'),
            'warmth': self.get_trait('agreeableness'),
            'humor_level': self.get_trait('humor'),
            'emoji_usage': self.get_trait('extraversion') * self.get_trait('humor'),
            'politeness_level': self.get_trait('politeness')
        }
    
    def should_show_emotion(self) -> bool:
        """
        Kiểm tra có nên thể hiện emotion không.
        
        Returns:
            True nếu nên show emotion
        """
        extraversion = self.get_trait('extraversion') or 0.5
        return extraversion > 0.6
    
    def get_greeting_style(self) -> str:
        """
        Lấy greeting style phù hợp.
        
        Returns:
            Greeting text
        """
        extraversion = self.get_trait('extraversion') or 0.5
        politeness = self.get_trait('politeness') or 0.5
        
        if extraversion > 0.7:
            if politeness > 0.7:
                return "Xin chào! Rất vui được gặp bạn!"
            else:
                return "Chào bạn! Có gì tôi giúp được không?"
        else:
            if politeness > 0.7:
                return "Xin chào."
            else:
                return "Chào."
    
    def get_error_handling_style(self) -> str:
        """
        Lấy cách xử lý lỗi phù hợp.
        
        Returns:
            Error response style
        """
        patience = self.get_trait('patience') or 0.5
        empathy = self.get_trait('empathy') or 0.5
        
        if patience > 0.7:
            if empathy > 0.7:
                return "Xin lỗi, tôi chưa hiểu rõ. Bạn có thể giải thích thêm được không?"
            else:
                return "Xin lỗi, tôi chưa hiểu. Vui lòng nói lại."
        else:
            return "Không hiểu. Nói lại."
    
    def should_ask_clarification(self, confusion_level: float) -> bool:
        """
        Kiểm tra có nên hỏi làm rõ không.
        
        Args:
            confusion_level: Mức độ confused (0.0 - 1.0)
            
        Returns:
            True nếu nên hỏi
        """
        conscientiousness = self.get_trait('conscientiousness') or 0.5
        patience = self.get_trait('patience') or 0.5
        
        threshold = 0.5 - (conscientiousness * 0.2)
        
        return confusion_level > threshold and patience > 0.5
    
    def get_wait_time_tolerance(self) -> float:
        """
        Lấy thời gian chờ tối đa trước khi nhắc nhở.
        
        Returns:
            Thời gian (giây)
        """
        patience = self.get_trait('patience') or 0.5
        
        # 5-30 giây tùy patience
        return 5.0 + (patience * 25.0)
    
    def should_use_humor(self, context_seriousness: float = 0.5) -> bool:
        """
        Kiểm tra có nên dùng humor không.
        
        Args:
            context_seriousness: Mức độ nghiêm trọng của context (0.0 - 1.0)
            
        Returns:
            True nếu nên dùng humor
        """
        humor = self.get_trait('humor') or 0.5
        
        # Không dùng humor trong context nghiêm trọng
        if context_seriousness > 0.7:
            return False
        
        return humor > 0.6
    
    def get_empathy_response(self, user_emotion: str) -> Optional[str]:
        """
        Lấy empathy response phù hợp.
        
        Args:
            user_emotion: Emotion của user
            
        Returns:
            Response text
        """
        empathy = self.get_trait('empathy') or 0.5
        
        if empathy < 0.5:
            return None
        
        responses = {
            'sad': "Tôi hiểu cảm giác của bạn. Có điều gì tôi có thể giúp không?",
            'angry': "Tôi xin lỗi nếu có điều gì làm bạn khó chịu.",
            'happy': "Thật tuyệt! Tôi cũng vui khi bạn vui!",
            'afraid': "Đừng lo lắng, tôi ở đây để giúp bạn."
        }
        
        return responses.get(user_emotion)
    
    def get_all_traits(self) -> Dict[str, float]:
        """
        Lấy tất cả traits.
        
        Returns:
            Dictionary {trait_name: value}
        """
        return {name: trait.value for name, trait in self.traits.items()}
    
    def describe(self) -> str:
        """
        Mô tả personality.
        
        Returns:
            Mô tả text
        """
        traits = self.get_all_traits()
        
        descriptions = []
        
        if traits.get('extraversion', 0) > 0.7:
            descriptions.append("năng động")
        elif traits.get('extraversion', 0) < 0.3:
            descriptions.append("trầm lặng")
        
        if traits.get('agreeableness', 0) > 0.7:
            descriptions.append("thân thiện")
        
        if traits.get('humor', 0) > 0.7:
            descriptions.append("hài hước")
        
        if traits.get('empathy', 0) > 0.7:
            descriptions.append("thấu hiểu")
        
        if not descriptions:
            descriptions.append("cân bằng")
        
        return f"Tính cách: {', '.join(descriptions)}"
    
    def get_info(self) -> dict:
        """
        Lấy thông tin personality.
        
        Returns:
            Dictionary thông tin
        """
        return {
            "preset": self.preset,
            "traits": self.get_all_traits(),
            "description": self.describe(),
            "response_style": self.get_response_style()
        }