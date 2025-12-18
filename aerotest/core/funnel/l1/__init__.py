"""L1: 规则槽位�?

通过 NLP 和规则从自然语言指令中提取结构化的操作信息：
- 意图识别：识别用户想要执行的动作
- 实体提取：提取目标元素的特征
- 槽位填充：将信息组织成结构化槽位
- 同义词扩展：扩展关键词的同义�?

示例�?
    输入: "点击提交按钮"
    输出: ActionSlot(
        action=ActionType.CLICK,
        target="提交按钮",
        target_type=ElementType.BUTTON,
        keywords=["提交", "按钮", "submit", "确认"],
    )
"""

from aerotest.core.funnel.l1.l1_engine import L1Engine

__all__ = ["L1Engine"]

