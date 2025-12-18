"""Qwen2-VL 客户�?

调用阿里云百炼平台的 Qwen2-VL 视觉模型 API
"""

from dataclasses import dataclass
from typing import Any, Optional

import httpx

from aerotest.config.settings import get_settings
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l5.qwen2vl")


@dataclass
class BoundingBox:
    """边界�?""
    x: float
    y: float
    width: float
    height: float
    
    @property
    def center_x(self) -> float:
        """中心 X 坐标"""
        return self.x + self.width / 2
    
    @property
    def center_y(self) -> float:
        """中心 Y 坐标"""
        return self.y + self.height / 2


class Qwen2VLClient:
    """Qwen2-VL API 客户�?
    
    调用阿里云百炼平台的 Qwen2-VL 视觉模型
    
    支持的功能：
    - 图像理解：理解图片内�?
    - 元素识别：识别图片中的特定元�?
    - 坐标定位：返回元素的位置坐标
    
    Example:
        ```python
        client = Qwen2VLClient()
        
        bbox = await client.identify_element(
            image_data=screenshot,
            description="红色的购物车图标"
        )
        
        if bbox:
            print(f"找到元素: ({bbox.center_x}, {bbox.center_y})")
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
        初始�?Qwen2-VL 客户�?
        
        Args:
            api_key: API Key（默认从配置读取�?
            base_url: API Base URL（默认从配置读取�?
            model: 模型名称（默认从配置读取�?
            timeout: 超时时间（秒�?
        """
        config = get_settings()
        
        self.api_key = api_key or config.dashscope_api_key
        self.base_url = base_url or config.qwen_base_url
        self.model = model or config.qwen_vl_model
        self.timeout = timeout
        
        # 创建 HTTP 客户�?
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
        )
        
        logger.info(f"Qwen2-VL 客户端初始化完成 (model={self.model})")
    
    async def identify_element(
        self,
        image_data: bytes,
        description: str,
        return_bbox: bool = True,
    ) -> Optional[BoundingBox]:
        """
        识别图片中的元素位置
        
        Args:
            image_data: 图片数据（bytes�?
            description: 元素描述
            return_bbox: 是否返回边界�?
            
        Returns:
            边界框，如果找不到则返回 None
        """
        # 将图片编码为 base64
        import base64
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        
        # 构建消息
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": f"请在图片中找到：{description}\n\n返回JSON格式：{{\"found\": true/false, \"x\": X坐标, \"y\": Y坐标, \"width\": 宽度, \"height\": 高度}}"
                    }
                ]
            }
        ]
        
        # 调用 API
        request_data = {
            "model": self.model,
            "messages": messages,
        }
        
        logger.debug(f"调用 Qwen2-VL API: {description}")
        
        try:
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions",
                json=request_data,
            )
            
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                
                # 解析 JSON
                import json
                try:
                    data = json.loads(content)
                    
                    if data.get("found"):
                        bbox = BoundingBox(
                            x=float(data.get("x", 0)),
                            y=float(data.get("y", 0)),
                            width=float(data.get("width", 0)),
                            height=float(data.get("height", 0)),
                        )
                        
                        logger.info(
                            f"识别成功: {description} "
                            f"at ({bbox.center_x:.0f}, {bbox.center_y:.0f})"
                        )
                        
                        return bbox
                    else:
                        logger.warning(f"未找到元�? {description}")
                        return None
                
                except json.JSONDecodeError:
                    logger.error(f"JSON 解析失败: {content}")
                    return None
            
            return None
        
        except Exception as e:
            logger.error(f"Qwen2-VL API 调用失败: {str(e)}")
            return None
    
    async def understand_image(
        self,
        image_data: bytes,
        question: str,
    ) -> str:
        """
        理解图片内容
        
        Args:
            image_data: 图片数据
            question: 要问的问�?
            
        Returns:
            AI 的回�?
        """
        import base64
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": question
                    }
                ]
            }
        ]
        
        request_data = {
            "model": self.model,
            "messages": messages,
        }
        
        try:
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions",
                json=request_data,
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            
            return ""
        
        except Exception as e:
            logger.error(f"图像理解失败: {str(e)}")
            return ""
    
    async def close(self):
        """关闭 HTTP 客户�?""
        await self.http_client.aclose()

