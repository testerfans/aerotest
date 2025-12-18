"""L4: AI 推理�?

使用 Qwen-Max/Plus 进行语义理解和复杂逻辑推理�?
- Qwen 客户端：调用阿里云百�?API
- Prompt 构建：构建高质量�?prompt
- 上下文提取：�?DOM 中提取相关上下文
- 结果解析：解�?AI 返回的结�?

典型场景�?
    指令: "选择最便宜的商�?
    处理: 1. 提取所有商品元�?
         2. Qwen 提取价格信息
         3. Qwen 比较并选择最便宜
         4. 返回目标元素 �?

来源: AeroTest AI 原创设计
"""

from aerotest.core.funnel.l4.l4_engine import L4Engine

__all__ = ["L4Engine"]

