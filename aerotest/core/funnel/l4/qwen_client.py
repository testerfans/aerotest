"""Qwen 客户�?

调用阿里云百炼平台的 Qwen 模型 API
"""

import json
from typing import Any, Optional

import httpx

from aerotest.config.settings import settings
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l4.qwen")


class QwenClient:
    """Qwen API 客户�?
    
    调用阿里云百炼平台的 Qwen 模型（兼�?OpenAI API 格式�?
    
    支持的模型：
    - qwen-max: 最强大的模�?
    - qwen-plus: 平衡性能和成�?
    - qwen-turbo: 快速响�?
    
    Example:
        ```python
        client = QwenClient()
        
        response = await client.chat(
            messages=[
                {"role": "user", "content": "你好"}
            ]
        )
        
        print(response)
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 60,
    ):
        """
        初始�?Qwen 客户�?
        
        Args:
            api_key: API Key（默认从配置读取�?
            base_url: API Base URL（默认从配置读取�?
            model: 模型名称（默认从配置读取�?
            timeout: 超时时间（秒�?
        """
        # 使用 get_settings() 获取配置
        from aerotest.config.settings import get_settings
        config = get_settings()
        
        self.api_key = api_key or config.dashscope_api_key
        self.base_url = base_url or config.qwen_base_url
        self.model = model or config.qwen_max_model
        self.timeout = timeout
        
        # 创建 HTTP 客户�?
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        
        logger.info(f"Qwen 客户端初始化完成 (model={self.model})")
    
    async def chat(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
    ) -> str:
        """
        调用 Chat API
        
        Args:
            messages: 消息列表，格式：[{"role": "user", "content": "..."}]
            model: 模型名称（覆盖默认值）
            max_tokens: 最大生�?tokens
            temperature: 温度参数�?-1�?
            stream: 是否流式返回
            
        Returns:
            AI 返回的文本内�?
        """
        if not messages:
            raise ValueError("messages 不能为空")
        
        # 构建请求参数
        request_data = {
            "model": model or self.model,
            "messages": messages,
            "max_tokens": max_tokens or config.qwen_max_tokens,
            "temperature": temperature or config.qwen_temperature,
            "stream": stream,
        }
        
        logger.debug(f"调用 Qwen API: {request_data['model']}")
        
        try:
            # 发送请�?
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions",
                json=request_data,
            )
            
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            # 提取内容
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                
                # 记录使用情况
                if "usage" in result:
                    usage = result["usage"]
                    logger.info(
                        f"Qwen API 调用成功: "
                        f"tokens={usage.get('total_tokens', 0)}, "
                        f"cost={usage.get('total_tokens', 0) * 0.0001:.4f}�?
                    )
                
                return content
            else:
                raise ValueError(f"API 返回格式错误: {result}")
        
        except httpx.HTTPStatusError as e:
            error_msg = f"Qwen API 请求失败: {e.response.status_code}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        
        except Exception as e:
            error_msg = f"Qwen API 调用异常: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    async def chat_with_json(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        调用 Chat API 并期望返�?JSON 格式
        
        Args:
            messages: 消息列表
            model: 模型名称
            
        Returns:
            解析后的 JSON 对象
        """
        # 在最后一条消息添�?JSON 格式要求
        if messages:
            last_message = messages[-1]
            if last_message["role"] == "user":
                last_message["content"] += "\n\n请以 JSON 格式返回结果�?
        
        # 调用 API
        response = await self.chat(messages, model=model)
        
        # 解析 JSON
        try:
            # 尝试提取 JSON（可能包含在代码块中�?
            json_str = response
            
            # 如果包含 ```json，提取其中的内容
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            
            # 解析 JSON
            result = json.loads(json_str)
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {response}")
            raise ValueError(f"Qwen 返回的不是有效的 JSON: {str(e)}") from e
    
    async def close(self):
        """关闭 HTTP 客户�?""
        await self.http_client.aclose()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退�?""
        await self.close()


# 创建全局客户端实例（可选）
_global_client: Optional[QwenClient] = None


def get_qwen_client() -> QwenClient:
    """获取全局 Qwen 客户端实�?""
    global _global_client
    if _global_client is None:
        _global_client = QwenClient()
    return _global_client

