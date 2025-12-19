"""L5 引擎

L5 视觉识别引擎，整合所有 L5 组件
"""

from typing import Optional

from aerotest.browser.cdp.session import CDPSession
from aerotest.browser.dom.views import DOMRect, EnhancedDOMTreeNode, NodeType
from aerotest.browser.dom.views import SerializedDOMState
from aerotest.core.funnel.base import BaseFunnelLayer
from aerotest.core.funnel.l5.qwen2vl_client import Qwen2VLClient
from aerotest.core.funnel.l5.screenshot_service import ScreenshotService
from aerotest.core.funnel.types import FunnelContext, MatchResult
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l5")


class L5Engine(BaseFunnelLayer):
    """L5 视觉识别引擎
    
    使用 Qwen2-VL 进行视觉识别，处理 Canvas 和图像元素：
    1. 检查是否需要 L5
    2. 截取页面截图
    3. 调用 Qwen2-VL 识别元素
    4. 解析坐标
    5. 创建虚拟元素
    6. 返回结果
    
    Example:
        ```python
        engine = L5Engine()
        
        # 处理视觉识别任务
        context = FunnelContext(instruction="点击红色的购物车图标")
        context = await engine.process(context, dom_state, cdp_session)
        
        if context.l5_candidates:
            result = context.l5_candidates[0]
            # 使用坐标点击
            await cdp_session.click(result.element.bounding_box.x, ...)
        ```
    """
    
    def __init__(self):
        """初始化 L5 引擎"""
        super().__init__("L5")
        
        # 初始化组件
        self.screenshot_service = ScreenshotService()
        self.qwen2vl_client = Qwen2VLClient()
        
        self.logger.info("L5 引擎初始化完成")
    
    async def process(
        self,
        context: FunnelContext,
        dom_state: Optional[SerializedDOMState] = None,
        cdp_session: Optional[CDPSession] = None,
    ) -> FunnelContext:
        """
        视觉识别处理
        
        Args:
            context: 漏斗上下文
            dom_state: DOM 状态
            cdp_session: CDP 会话（必需，用于截图）
            
        Returns:
            更新后的上下文（包含 l5_candidates）
        """
        self.log_start()
        
        if not context.action_slot:
            self.logger.warning("没有槽位信息，跳过 L5")
            return context
        
        if not cdp_session:
            self.logger.warning("没有 CDP 会话，跳过 L5")
            return context
        
        # 1. 检查是否需要 L5
        # 如果前面的层已经有结果，且包含视觉相关关键词才使用 L5
        if not self._needs_visual_recognition(context.instruction):
            self.logger.info("指令不需要视觉识别，跳过 L5")
            return context
        
        instruction = context.instruction
        target_desc = context.action_slot.target or instruction
        
        self.logger.info(f"使用 L5 视觉识别: {target_desc}")
        
        # 2. 截取页面截图
        try:
            screenshot = await self.screenshot_service.capture_screenshot(cdp_session)
        except Exception as e:
            self.logger.error(f"截图失败: {str(e)}")
            return context
        
        # 3. 调用 Qwen2-VL 识别元素
        bbox = await self.qwen2vl_client.identify_element(
            image_data=screenshot,
            description=target_desc,
        )
        
        if bbox:
            # 4. 创建虚拟元素（基于坐标）
            virtual_element = EnhancedDOMTreeNode(
                backend_node_id=-1,  # 虚拟 ID
                node_type=NodeType.ELEMENT_NODE,
                node_name="VISUAL_ELEMENT",
                tag_name="visual",
                attributes={
                    "description": target_desc,
                    "detected_by": "qwen2-vl",
                },
                bounding_box=DOMRect(
                    x=bbox.x,
                    y=bbox.y,
                    width=bbox.width,
                    height=bbox.height,
                ),
                is_clickable=True,
            )
            
            # 5. 创建 MatchResult
            l5_result = MatchResult(
                element=virtual_element,
                score=0.90,  # L5 视觉识别给予高置信度
                matched_attributes={
                    "center_x": bbox.center_x,
                    "center_y": bbox.center_y,
                },
                match_reasons=[
                    f"视觉识别: {target_desc}",
                    f"位置: ({bbox.center_x:.0f}, {bbox.center_y:.0f})",
                ],
                layer="L5",
            )
            
            context.l5_candidates = [l5_result]
            
            self.logger.info(
                f"L5 处理完成: 找到元素 "
                f"at ({bbox.center_x:.0f}, {bbox.center_y:.0f})"
            )
        else:
            self.logger.warning(f"未找到视觉元素: {target_desc}")
        
        self.log_end(len(context.l5_candidates) if context.l5_candidates else 0)
        return context
    
    def _needs_visual_recognition(self, instruction: str) -> bool:
        """
        判断是否需要视觉识别
        
        Args:
            instruction: 用户指令
            
        Returns:
            是否需要视觉识别
        """
        # 包含颜色、形状等视觉特征的关键词
        visual_keywords = [
            "红色", "蓝色", "绿色", "黄色", "黑色", "白色",
            "图标", "图片", "按钮图标", "小图标",
            "圆形", "方形", "三角形",
            "canvas", "画布",
        ]
        
        return any(keyword in instruction for keyword in visual_keywords)

