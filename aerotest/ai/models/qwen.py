"""通义千问模型客户端"""

from typing import Any, Dict, List, Optional

import dashscope
from dashscope import Generation

from aerotest.config import get_settings
from aerotest.utils import get_logger

logger = get_logger("aerotest.ai.qwen")


class QwenClient:
    """通义千问 API 客户端"""

    def __init__(self):
        """初始化客户端"""
        self.settings = get_settings()
        dashscope.api_key = self.settings.dashscope_api_key

        if not self.settings.dashscope_api_key:
            logger.warning("DASHSCOPE_API_KEY 未配置")

        logger.info("Qwen 客户端初始化完成")

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        调用 Qwen 模型进行对话

        Args:
            messages: 对话消息列表
            model: 模型名称（默认使用 qwen-max）
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            模型响应文本
        """
        model = model or self.settings.qwen_max_model

        try:
            logger.debug(f"调用 Qwen 模型: {model}")

            response = Generation.call(
                model=model,
                messages=messages,
                result_format="message",
                temperature=temperature,
                max_tokens=max_tokens,
            )

            if response.status_code == 200:
                result = response.output.choices[0].message.content
                logger.debug(f"Qwen 响应成功: {result[:100]}...")
                return result
            else:
                error_msg = f"Qwen API 调用失败: {response.code} - {response.message}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

        except Exception as e:
            logger.error(f"Qwen API 调用异常: {e}")
            raise

    async def analyze_element(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用 Qwen-Plus 分析元素定位

        Args:
            context: 上下文信息，包括选择器、DOM 信息等

        Returns:
            分析结果
        """
        selector = context.get("selector", "")
        dom_info = context.get("dom_info", {})

        prompt = f"""你是一个 UI 自动化测试专家。请分析以下信息，帮助定位页面元素：

选择器描述: {selector}

DOM 信息: {dom_info}

请分析并返回以下：
1. 最可能匹配的元素
2. 置信度 (0-1)
3. 推理过程
"""

        messages = [{"role": "user", "content": prompt}]

        try:
            response = await self.chat(
                messages=messages, model=self.settings.qwen_plus_model, temperature=0.3
            )

            # TODO: 解析响应，提取结构化信息
            return {"raw_response": response, "confidence": 0.8}

        except Exception as e:
            logger.error(f"元素分析失败: {e}")
            return {"error": str(e), "confidence": 0.0}
