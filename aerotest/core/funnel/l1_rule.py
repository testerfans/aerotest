"""L1 规则槽位层"""

import re
from typing import Any, Dict, Optional

from aerotest.core.funnel.base import BaseFunnelLayer
from aerotest.core.funnel.engine import FunnelResult
from aerotest.core.types import ElementLocatorStrategy
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l1")


class L1RuleLayer(BaseFunnelLayer):
    """L1 规则槽位层 - 基于 NLP 和规则的快速匹配"""

    def __init__(self):
        super().__init__(ElementLocatorStrategy.L1_RULE)

        # 定义动作规则模板
        self.action_patterns = {
            "input": [
                r"(输入|填写|录入)(.+?)(输入框|文本框|框)",
                r"在(.+?)(输入框|文本框|框)(输入|填写)",
            ],
            "click": [
                r"点击(.+?)(按钮|链接|图标)",
                r"(提交|确认|取消|登录|注册)",
            ],
            "select": [
                r"选择(.+?)(下拉框|选项|菜单)",
                r"在(.+?)中选择(.+?)",
            ],
        }

        # 同义词映射
        self.synonym_map = {
            "用户名": ["账号", "用户账号", "登录名", "username"],
            "密码": ["口令", "password", "密钥"],
            "登录": ["登入", "sign in", "login"],
            "注册": ["注册", "sign up", "register"],
            "提交": ["确定", "确认", "ok", "submit"],
        }

        logger.info("L1 规则槽位层初始化完成")

    def can_handle(self, selector: str) -> bool:
        """判断是否能处理该选择器"""
        # L1 层主要处理自然语言描述
        return any(
            re.search(pattern, selector, re.IGNORECASE)
            for patterns in self.action_patterns.values()
            for pattern in patterns
        )

    async def locate(
        self, selector: str, context: Dict[str, Any], dom_adapter: Any
    ) -> Optional[FunnelResult]:
        """
        通过规则匹配定位元素

        Args:
            selector: 元素选择器（自然语言）
            context: 上下文信息
            dom_adapter: DOM 适配器

        Returns:
            FunnelResult 或 None
        """
        logger.debug(f"L1 规则层处理: {selector}")

        # 解析动作和目标
        action, target = self._parse_selector(selector)
        if not action or not target:
            logger.debug("L1 无法解析选择器")
            return None

        logger.info(f"L1 解析结果: action={action}, target={target}")

        # 应用同义词映射
        normalized_target = self._normalize_target(target)

        # TODO: 基于规则在 DOM 中查找匹配元素
        # 1. 获取所有相关元素
        # 2. 根据 action 过滤元素类型
        # 3. 根据 target 匹配元素属性
        # 4. 返回最佳匹配

        # 目前返回 None，表示未找到
        return None

    def _parse_selector(self, selector: str) -> tuple[Optional[str], Optional[str]]:
        """
        解析自然语言选择器

        Args:
            selector: 自然语言选择器

        Returns:
            (action, target) 元组
        """
        for action, patterns in self.action_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, selector, re.IGNORECASE)
                if match:
                    # 提取目标文本
                    target = match.group(1) if match.lastindex >= 1 else None
                    if target:
                        target = target.strip()
                        return action, target

        return None, None

    def _normalize_target(self, target: str) -> str:
        """
        归一化目标文本（同义词映射）

        Args:
            target: 原始目标文本

        Returns:
            归一化后的文本
        """
        for key, synonyms in self.synonym_map.items():
            if target.lower() in [s.lower() for s in synonyms]:
                return key

        return target
