import json
from typing import Optional, Dict, Any
from pydantic import BaseModel, ValidationError
from .qwen_ai import Qwen3Chat
from ..utils.logger import Logger

class ParsedCommand(BaseModel):
    intent: str        # Ý định: "control_device", "conversation", "query_info", ...
    command: str       # Lệnh chính: "turn_on_light", "move_forward", ...
    params: dict = {}  # Tham số đi kèm (vd: {"room": "phòng khách", "speed": "fast"})

class NLPParser:
    """
    NLPParser: lớp phân tích ngôn ngữ tự nhiên
    - Nhận text từ STT
    - Gửi cho Qwen-8B để phân tích
    - Ép output về dạng JSON (ParsedCommand)
    """

    def __init__(self, model_name: str = "qwen8b"):
        self.logger = Logger("NLPParser")
        self.llm = Qwen3Chat(model=model_name)

    def parse(self, text: str) -> Optional[ParsedCommand]:
        """
        Phân tích câu text từ giọng nói → ParsedCommand
        """
        schema = {
            "intent": "string (vd: control_device, query_info, conversation)",
            "command": "string (vd: turn_on_light, move_forward, ask_weather)",
            "params": "object (có thể rỗng hoặc chứa key-value)"
        }

        system_prompt = f"""
Bạn là bộ parser lệnh cho Robot Pet HomeGuard.
Nhiệm vụ: phân tích câu lệnh ngôn ngữ tự nhiên thành JSON hợp lệ theo schema:
{json.dumps(schema, ensure_ascii=False, indent=2)}

Yêu cầu:
- Luôn trả về JSON hợp lệ.
- Không thêm giải thích, không text ngoài JSON.
"""

        response = self.llm.ask(system_prompt, text)
        raw_output = response.strip()
        self.logger.info(f"Raw output từ LLM: {raw_output}")

        try:
            data = json.loads(raw_output)
            cmd = ParsedCommand(**data)
            return cmd
        except (json.JSONDecodeError, ValidationError) as e:
            self.logger.error(f"Lỗi parse JSON: {e}")
            return ParsedCommand(intent="conversation", command="fallback", params={"text": text})
