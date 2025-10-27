"""
Conversation Engine - Quản lý hội thoại với người dùng.
Lưu trữ context và history của conversation.
"""
import time
from typing import List, Dict, Optional, Any
from datetime import datetime
from loguru import logger

from src.core.nlp.llm_manager import LLMManager, LLMResponse
from src.utils.constants import MAX_CONVERSATION_HISTORY, CONVERSATION_TIMEOUT_SECONDS


class Message:
    """Đại diện cho một message trong conversation."""
    
    def __init__(
        self,
        role: str,
        content: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Khởi tạo Message.
        
        Args:
            role: Role ("user", "assistant", "system")
            content: Nội dung message
            timestamp: Thời gian
            metadata: Thông tin bổ sung
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, str]:
        """Convert sang dictionary format cho LLM."""
        return {
            "role": self.role,
            "content": self.content
        }


class Conversation:
    """Đại diện cho một conversation session."""
    
    def __init__(
        self,
        conversation_id: str,
        user_name: Optional[str] = None,
        system_prompt: Optional[str] = None
    ):
        """
        Khởi tạo Conversation.
        
        Args:
            conversation_id: ID của conversation
            user_name: Tên user
            system_prompt: System prompt
        """
        self.conversation_id = conversation_id
        self.user_name = user_name or "User"
        self.system_prompt = system_prompt
        
        # Message history
        self.messages: List[Message] = []
        
        # Timestamps
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        
        # Statistics
        self.total_tokens_used = 0
        self.message_count = 0
        
        # Add system prompt
        if system_prompt:
            self.add_message("system", system_prompt)
    
    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> Message:
        """
        Thêm message vào conversation.
        
        Args:
            role: Role của message
            content: Nội dung
            metadata: Metadata
            
        Returns:
            Message object
        """
        message = Message(role, content, metadata=metadata)
        self.messages.append(message)
        
        self.last_activity = datetime.now()
        self.message_count += 1
        
        return message
    
    def get_messages(
        self,
        limit: Optional[int] = None,
        exclude_system: bool = False
    ) -> List[Message]:
        """
        Lấy messages.
        
        Args:
            limit: Số lượng messages (None = tất cả)
            exclude_system: Loại bỏ system messages
            
        Returns:
            List Messages
        """
        messages = self.messages
        
        if exclude_system:
            messages = [msg for msg in messages if msg.role != "system"]
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_messages_dict(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Lấy messages dạng dict cho LLM.
        
        Args:
            limit: Số lượng messages
            
        Returns:
            List dictionaries
        """
        messages = self.get_messages(limit)
        return [msg.to_dict() for msg in messages]
    
    def clear_history(self, keep_system: bool = True) -> None:
        """
        Xóa history.
        
        Args:
            keep_system: Giữ lại system prompt
        """
        if keep_system and self.system_prompt:
            system_msg = self.messages[0] if self.messages else None
            self.messages.clear()
            if system_msg and system_msg.role == "system":
                self.messages.append(system_msg)
        else:
            self.messages.clear()
        
        logger.info(f"Đã xóa history conversation: {self.conversation_id}")
    
    def is_expired(self, timeout_seconds: int = CONVERSATION_TIMEOUT_SECONDS) -> bool:
        """
        Kiểm tra conversation có hết hạn không.
        
        Args:
            timeout_seconds: Thời gian timeout
            
        Returns:
            True nếu expired
        """
        elapsed = (datetime.now() - self.last_activity).total_seconds()
        return elapsed > timeout_seconds
    
    def get_summary(self) -> str:
        """
        Lấy summary của conversation.
        
        Returns:
            Summary string
        """
        return (
            f"Conversation {self.conversation_id}\n"
            f"User: {self.user_name}\n"
            f"Messages: {self.message_count}\n"
            f"Tokens: {self.total_tokens_used}\n"
            f"Duration: {(datetime.now() - self.created_at).total_seconds():.0f}s"
        )


class ConversationEngine:
    """
    Quản lý conversations và tương tác với LLM.
    """
    
    def __init__(
        self,
        llm_manager: LLMManager,
        max_history: int = MAX_CONVERSATION_HISTORY,
        default_system_prompt: Optional[str] = None
    ):
        """
        Khởi tạo Conversation Engine.
        
        Args:
            llm_manager: LLM Manager instance
            max_history: Số lượng messages tối đa trong history
            default_system_prompt: System prompt mặc định
        """
        self.llm_manager = llm_manager
        self.max_history = max_history
        self.default_system_prompt = default_system_prompt or self._get_default_prompt()
        
        # Active conversations
        self.conversations: Dict[str, Conversation] = {}
        
        logger.info("Conversation Engine đã khởi tạo")
    
    def _get_default_prompt(self) -> str:
        """Lấy system prompt mặc định."""
        return (
            "Bạn là một trợ lý AI thông minh và hữu ích trong robot gia đình. "
            "Hãy trả lời một cách tự nhiên, thân thiện và ngắn gọn. "
            "Luôn lắng nghe và hiểu nhu cầu của người dùng."
        )
    
    def create_conversation(
        self,
        conversation_id: str,
        user_name: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> Conversation:
        """
        Tạo conversation mới.
        
        Args:
            conversation_id: ID conversation
            user_name: Tên user
            system_prompt: System prompt custom
            
        Returns:
            Conversation object
        """
        if conversation_id in self.conversations:
            logger.warning(f"Conversation {conversation_id} đã tồn tại")
            return self.conversations[conversation_id]
        
        conversation = Conversation(
            conversation_id=conversation_id,
            user_name=user_name,
            system_prompt=system_prompt or self.default_system_prompt
        )
        
        self.conversations[conversation_id] = conversation
        logger.info(f"✅ Tạo conversation: {conversation_id}")
        
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Lấy conversation theo ID.
        
        Args:
            conversation_id: ID conversation
            
        Returns:
            Conversation hoặc None
        """
        return self.conversations.get(conversation_id)
    
    async def send_message(
        self,
        conversation_id: str,
        user_message: str,
        user_name: Optional[str] = None
    ) -> Optional[LLMResponse]:
        """
        Gửi message và nhận response.
        
        Args:
            conversation_id: ID conversation
            user_message: Message từ user
            user_name: Tên user
            
        Returns:
            LLMResponse
        """
        # Lấy hoặc tạo conversation
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            conversation = self.create_conversation(conversation_id, user_name)
        
        # Thêm user message
        conversation.add_message("user", user_message)
        
        # Lấy history
        messages = conversation.get_messages_dict(limit=self.max_history)
        
        # Generate response
        logger.info(f"💬 [{user_name or 'User'}]: {user_message}")
        response = await self.llm_manager.chat(messages)
        
        if not response:
            logger.error("Không nhận được response từ LLM")
            return None
        
        # Thêm assistant response
        conversation.add_message("assistant", response.text)
        conversation.total_tokens_used += response.tokens_used
        
        logger.info(f"🤖 [Assistant]: {response.text[:100]}...")
        
        return response
    
    async def quick_reply(
        self,
        user_message: str,
        system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """
        Quick reply không cần conversation context.
        
        Args:
            user_message: Message từ user
            system_prompt: System prompt
            
        Returns:
            Response text
        """
        response = await self.llm_manager.generate(
            prompt=user_message,
            system_prompt=system_prompt or self.default_system_prompt
        )
        
        return response.text if response else None
    
    def clear_conversation(self, conversation_id: str) -> bool:
        """
        Xóa conversation history.
        
        Args:
            conversation_id: ID conversation
            
        Returns:
            True nếu xóa thành công
        """
        conversation = self.get_conversation(conversation_id)
        if conversation:
            conversation.clear_history()
            return True
        return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Xóa conversation hoàn toàn.
        
        Args:
            conversation_id: ID conversation
            
        Returns:
            True nếu xóa thành công
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Đã xóa conversation: {conversation_id}")
            return True
        return False
    
    def cleanup_expired(
        self,
        timeout_seconds: int = CONVERSATION_TIMEOUT_SECONDS
    ) -> int:
        """
        Xóa các conversations đã hết hạn.
        
        Args:
            timeout_seconds: Timeout
            
        Returns:
            Số lượng conversations đã xóa
        """
        expired = [
            cid for cid, conv in self.conversations.items()
            if conv.is_expired(timeout_seconds)
        ]
        
        for cid in expired:
            self.delete_conversation(cid)
        
        if expired:
            logger.info(f"Đã xóa {len(expired)} expired conversations")
        
        return len(expired)
    
    def get_all_conversations(self) -> List[Conversation]:
        """Lấy tất cả conversations."""
        return list(self.conversations.values())
    
    def get_conversation_count(self) -> int:
        """Lấy số lượng conversations."""
        return len(self.conversations)
    
    def get_info(self) -> dict:
        """
        Lấy thông tin Conversation Engine.
        
        Returns:
            Dictionary thông tin
        """
        total_messages = sum(c.message_count for c in self.conversations.values())
        total_tokens = sum(c.total_tokens_used for c in self.conversations.values())
        
        return {
            "active_conversations": self.get_conversation_count(),
            "total_messages": total_messages,
            "total_tokens": total_tokens,
            "max_history": self.max_history
        }