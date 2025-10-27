"""
LLM Manager - Quản lý Large Language Models.
Hỗ trợ OpenAI, Anthropic Claude, và Ollama (local).
"""
import asyncio
from typing import Optional, List, Dict, Any
from enum import Enum
from loguru import logger

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("⚠️  openai chưa cài đặt")

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("⚠️  anthropic chưa cài đặt")

from config.settings import LLMSettings


class LLMProvider(str, Enum):
    """Các LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class LLMResponse:
    """Response từ LLM."""
    
    def __init__(
        self,
        text: str,
        model: str,
        tokens_used: int,
        finish_reason: str,
        processing_time: float
    ):
        """
        Khởi tạo LLMResponse.
        
        Args:
            text: Text response
            model: Model đã dùng
            tokens_used: Số tokens đã dùng
            finish_reason: Lý do kết thúc
            processing_time: Thời gian xử lý (ms)
        """
        self.text = text
        self.model = model
        self.tokens_used = tokens_used
        self.finish_reason = finish_reason
        self.processing_time = processing_time


class LLMManager:
    """
    Quản lý và gọi các Large Language Models.
    """
    
    def __init__(self, config: LLMSettings):
        """
        Khởi tạo LLM Manager.
        
        Args:
            config: Cấu hình LLM
        """
        self.config = config
        self.provider = LLMProvider(config.provider)
        
        # Clients
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize client
        self._initialize_client()
        
        logger.info(f"LLM Manager đã khởi tạo (provider: {self.provider.value})")
    
    def _initialize_client(self) -> None:
        """Khởi tạo LLM client theo provider."""
        if self.provider == LLMProvider.OPENAI:
            self._initialize_openai()
        elif self.provider == LLMProvider.ANTHROPIC:
            self._initialize_anthropic()
        elif self.provider == LLMProvider.OLLAMA:
            self._initialize_ollama()
    
    def _initialize_openai(self) -> None:
        """Khởi tạo OpenAI client."""
        if not OPENAI_AVAILABLE:
            raise ImportError("openai chưa cài đặt. Cài: pip install openai")
        
        if not self.config.openai_api_key:
            logger.warning("⚠️  OpenAI API key chưa được set")
            return
        
        try:
            self.openai_client = openai.OpenAI(
                api_key=self.config.openai_api_key,
                organization=self.config.openai_org_id or None
            )
            logger.info("✅ OpenAI client đã khởi tạo")
        except Exception as e:
            logger.error(f"❌ Lỗi khởi tạo OpenAI: {e}")
    
    def _initialize_anthropic(self) -> None:
        """Khởi tạo Anthropic client."""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic chưa cài đặt. Cài: pip install anthropic")
        
        if not self.config.anthropic_api_key:
            logger.warning("⚠️  Anthropic API key chưa được set")
            return
        
        try:
            self.anthropic_client = anthropic.Anthropic(
                api_key=self.config.anthropic_api_key
            )
            logger.info("✅ Anthropic client đã khởi tạo")
        except Exception as e:
            logger.error(f"❌ Lỗi khởi tạo Anthropic: {e}")
    
    def _initialize_ollama(self) -> None:
        """Khởi tạo Ollama client."""
        # Ollama sử dụng HTTP requests đơn giản
        logger.info(f"✅ Ollama client (base_url: {self.config.ollama_base_url})")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Optional[LLMResponse]:
        """
        Generate response từ LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Temperature override
            max_tokens: Max tokens override
            
        Returns:
            LLMResponse hoặc None
        """
        import time
        start_time = time.time()
        
        try:
            if self.provider == LLMProvider.OPENAI:
                response = await self._generate_openai(
                    prompt, system_prompt, temperature, max_tokens
                )
            elif self.provider == LLMProvider.ANTHROPIC:
                response = await self._generate_anthropic(
                    prompt, system_prompt, temperature, max_tokens
                )
            elif self.provider == LLMProvider.OLLAMA:
                response = await self._generate_ollama(
                    prompt, system_prompt, temperature, max_tokens
                )
            else:
                logger.error(f"Provider không hỗ trợ: {self.provider}")
                return None
            
            # Tính processing time
            processing_time = (time.time() - start_time) * 1000
            
            if response:
                response.processing_time = processing_time
                logger.info(f"✅ LLM response ({processing_time:.0f}ms, {response.tokens_used} tokens)")
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Lỗi generate: {e}")
            return None
    
    async def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> Optional[LLMResponse]:
        """Generate từ OpenAI."""
        if not self.openai_client:
            logger.error("OpenAI client chưa khởi tạo")
            return None
        
        # Chuẩn bị messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Call API
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.openai_client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens
            )
        )
        
        # Parse response
        choice = response.choices[0]
        
        return LLMResponse(
            text=choice.message.content,
            model=response.model,
            tokens_used=response.usage.total_tokens,
            finish_reason=choice.finish_reason,
            processing_time=0.0
        )
    
    async def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> Optional[LLMResponse]:
        """Generate từ Anthropic Claude."""
        if not self.anthropic_client:
            logger.error("Anthropic client chưa khởi tạo")
            return None
        
        # Call API
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.anthropic_client.messages.create(
                model=self.config.model,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens
            )
        )
        
        # Parse response
        text = response.content[0].text
        
        return LLMResponse(
            text=text,
            model=response.model,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            finish_reason=response.stop_reason,
            processing_time=0.0
        )
    
    async def _generate_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: Optional[float],
        max_tokens: Optional[int]
    ) -> Optional[LLMResponse]:
        """Generate từ Ollama (local)."""
        import aiohttp
        
        url = f"{self.config.ollama_base_url}/api/generate"
        
        payload = {
            "model": self.config.ollama_model,
            "prompt": prompt,
            "system": system_prompt or "",
            "options": {
                "temperature": temperature or self.config.temperature,
                "num_predict": max_tokens or self.config.max_tokens
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status != 200:
                        logger.error(f"Ollama error: {resp.status}")
                        return None
                    
                    # Ollama streams response, collect all
                    full_response = ""
                    async for line in resp.content:
                        import json
                        data = json.loads(line)
                        if "response" in data:
                            full_response += data["response"]
                    
                    return LLMResponse(
                        text=full_response,
                        model=self.config.ollama_model,
                        tokens_used=0,  # Ollama không trả về token count
                        finish_reason="stop",
                        processing_time=0.0
                    )
        except Exception as e:
            logger.error(f"Lỗi Ollama: {e}")
            return None
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Optional[LLMResponse]:
        """
        Chat với conversation history.
        
        Args:
            messages: List messages [{"role": "user/assistant", "content": "..."}]
            temperature: Temperature
            max_tokens: Max tokens
            
        Returns:
            LLMResponse
        """
        # Convert messages sang prompt format
        prompt_parts = []
        system_prompt = None
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                system_prompt = content
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt = "\n".join(prompt_parts)
        
        return await self.generate(prompt, system_prompt, temperature, max_tokens)
    
    def get_available_models(self) -> List[str]:
        """
        Lấy danh sách models có sẵn.
        
        Returns:
            List model names
        """
        if self.provider == LLMProvider.OPENAI:
            return [
                "gpt-4-turbo-preview",
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-3.5-turbo-16k"
            ]
        elif self.provider == LLMProvider.ANTHROPIC:
            return [
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]
        elif self.provider == LLMProvider.OLLAMA:
            return [
                "llama2",
                "mistral",
                "phi",
                "gemma"
            ]
        return []
    
    def change_model(self, model: str) -> None:
        """
        Thay đổi model.
        
        Args:
            model: Tên model mới
        """
        self.config.model = model
        logger.info(f"Đã đổi model: {model}")
    
    def get_info(self) -> dict:
        """
        Lấy thông tin LLM Manager.
        
        Returns:
            Dictionary thông tin
        """
        return {
            "provider": self.provider.value,
            "model": self.config.model,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "timeout": self.config.timeout,
            "client_initialized": (
                self.openai_client is not None or
                self.anthropic_client is not None
            )
        }