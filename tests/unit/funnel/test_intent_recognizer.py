"""意图识别器测试"""

import pytest

from aerotest.core.funnel.l1.intent_recognizer import IntentRecognizer
from aerotest.core.funnel.types import ActionType


class TestIntentRecognizer:
    """测试意图识别器"""
    
    @pytest.fixture
    def recognizer(self):
        """创建识别器实例"""
        return IntentRecognizer()
    
    def test_recognize_click(self, recognizer):
        """测试识别点击动作"""
        test_cases = [
            "点击提交按钮",
            "按登录",
            "选择确认",
            "单击按钮",
            "click button",
        ]
        
        for text in test_cases:
            action = recognizer.recognize(text)
            assert action == ActionType.CLICK, f"Failed: {text}"
    
    def test_recognize_input(self, recognizer):
        """测试识别输入动作"""
        test_cases = [
            "输入用户名",
            "填写密码",
            "录入信息",
            "键入文本",
            "input text",
        ]
        
        for text in test_cases:
            action = recognizer.recognize(text)
            assert action == ActionType.INPUT, f"Failed: {text}"
    
    def test_recognize_select(self, recognizer):
        """测试识别选择动作"""
        test_cases = [
            "选择选项",
            "勾选复选框",
            "选中单选框",
            "select option",
        ]
        
        for text in test_cases:
            action = recognizer.recognize(text)
            assert action == ActionType.SELECT, f"Failed: {text}"
    
    def test_recognize_navigate(self, recognizer):
        """测试识别导航动作"""
        test_cases = [
            "打开网页",
            "访问链接",
            "跳转到首页",
            "进入设置",
            "open page",
        ]
        
        for text in test_cases:
            action = recognizer.recognize(text)
            assert action == ActionType.NAVIGATE, f"Failed: {text}"
    
    def test_recognize_wait(self, recognizer):
        """测试识别等待动作"""
        test_cases = [
            "等待加载",
            "暂停2秒",
            "wait 5 seconds",
        ]
        
        for text in test_cases:
            action = recognizer.recognize(text)
            assert action == ActionType.WAIT, f"Failed: {text}"
    
    def test_context_inference(self, recognizer):
        """测试上下文推断"""
        # "选择" 可能是 CLICK 或 SELECT，但有"按钮"上下文时应该是 CLICK
        action = recognizer.recognize("选择提交按钮")
        assert action == ActionType.CLICK
        
        # 有"复选框"上下文时应该是 SELECT
        action = recognizer.recognize("选择复选框")
        assert action == ActionType.SELECT
    
    def test_empty_text(self, recognizer):
        """测试空文本"""
        action = recognizer.recognize("")
        assert action == ActionType.UNKNOWN
    
    def test_unknown_action(self, recognizer):
        """测试未知动作（默认返回 CLICK）"""
        action = recognizer.recognize("随便看看")
        # 应该返回默认的 CLICK
        assert action in [ActionType.CLICK, ActionType.UNKNOWN]
    
    def test_confidence(self, recognizer):
        """测试置信度计算"""
        # 精确匹配应该有高置信度
        confidence = recognizer.get_confidence("点击按钮", ActionType.CLICK)
        assert confidence > 0.6
        
        # 不匹配应该有低置信度
        confidence = recognizer.get_confidence("随便看看", ActionType.CLICK)
        assert confidence < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

