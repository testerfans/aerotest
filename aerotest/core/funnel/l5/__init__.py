"""L5: 视觉识别层

使用 Qwen2-VL 进行视觉识别，处理 Canvas 和图像元素：
- 截图服务：截取页面或元素截图
- Qwen2-VL 客户端：调用视觉模型 API
- 坐标识别：识别元素位置并返回坐标
- 图像处理：处理截图和标注

典型场景：
    指令: "点击红色的购物车图标"
    处理: 1. 截取页面截图
         2. Qwen2-VL 识别红色购物车图标
         3. 返回坐标位置
         4. 点击坐标

来源: AeroTest AI 原创设计
"""

from aerotest.core.funnel.l5.l5_engine import L5Engine

__all__ = ["L5Engine"]
