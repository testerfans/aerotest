"""截图服务

提供页面和元素截图功�?
"""

import base64
from typing import Optional

from aerotest.browser.cdp.session import CDPSession
from aerotest.browser.dom.views import EnhancedDOMTreeNode
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l5.screenshot")


class ScreenshotService:
    """截图服务
    
    提供页面和元素截图功能（基于 CDP�?
    
    Example:
        ```python
        service = ScreenshotService()
        
        # 截取整个页面
        screenshot = await service.capture_screenshot(cdp_session)
        
        # 截取特定元素
        element_screenshot = await service.capture_element(
            element,
            cdp_session
        )
        ```
    """
    
    def __init__(self):
        """初始化截图服�?""
        logger.debug("截图服务初始化完�?)
    
    async def capture_screenshot(
        self,
        cdp_session: CDPSession,
        format: str = "png",
        quality: int = 90,
    ) -> bytes:
        """
        截取整个页面
        
        Args:
            cdp_session: CDP 会话
            format: 图片格式（png �?jpeg�?
            quality: 图片质量�?-100，仅 jpeg 有效�?
            
        Returns:
            截图的字节数�?
        """
        try:
            # 使用 CDP Page.captureScreenshot 命令
            result = await cdp_session.cdp_client.page.capture_screenshot(
                format=format,
                quality=quality if format == "jpeg" else None,
            )
            
            # 解码 base64
            screenshot_data = base64.b64decode(result)
            
            logger.info(f"截图完成: {len(screenshot_data)} 字节")
            
            return screenshot_data
        
        except Exception as e:
            logger.error(f"截图失败: {str(e)}")
            raise RuntimeError(f"截图失败: {str(e)}") from e
    
    async def capture_element(
        self,
        element: EnhancedDOMTreeNode,
        cdp_session: CDPSession,
        format: str = "png",
    ) -> Optional[bytes]:
        """
        截取特定元素
        
        Args:
            element: DOM 元素
            cdp_session: CDP 会话
            format: 图片格式
            
        Returns:
            截图的字节数据，如果元素没有位置信息则返�?None
        """
        if not element.bounding_box:
            logger.warning("元素没有位置信息")
            return None
        
        bbox = element.bounding_box
        
        try:
            # 使用 CDP Page.captureScreenshot 命令，带 clip 参数
            result = await cdp_session.cdp_client.page.capture_screenshot(
                format=format,
                clip={
                    "x": bbox.x,
                    "y": bbox.y,
                    "width": bbox.width,
                    "height": bbox.height,
                    "scale": 1.0,
                },
            )
            
            # 解码 base64
            screenshot_data = base64.b64decode(result)
            
            logger.info(f"元素截图完成: {len(screenshot_data)} 字节")
            
            return screenshot_data
        
        except Exception as e:
            logger.error(f"元素截图失败: {str(e)}")
            return None
    
    def encode_image_to_base64(self, image_data: bytes) -> str:
        """
        将图片数据编码为 base64 字符�?
        
        Args:
            image_data: 图片字节数据
            
        Returns:
            base64 编码的字符串
        """
        return base64.b64encode(image_data).decode("utf-8")

