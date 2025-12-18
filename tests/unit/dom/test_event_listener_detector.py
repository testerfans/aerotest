"""事件监听器检测器单元测试"""

import pytest

from aerotest.browser.dom.event_listener_detector import (
    EventListenerDetector,
    EventListenerInfo,
)


class TestEventListenerInfo:
    """测试 EventListenerInfo 数据类"""
    
    def test_create_event_listener_info(self):
        """测试创建事件监听器信息"""
        info = EventListenerInfo(
            type="click",
            use_capture=False,
            passive=True,
            once=False
        )
        
        assert info.type == "click"
        assert info.use_capture is False
        assert info.passive is True
        assert info.once is False
    
    def test_event_listener_info_repr(self):
        """测试字符串表示"""
        info = EventListenerInfo(type="click")
        assert "click" in repr(info)
        
        info_with_flags = EventListenerInfo(
            type="input",
            use_capture=True,
            passive=True
        )
        repr_str = repr(info_with_flags)
        assert "input" in repr_str
        assert "capture" in repr_str
        assert "passive" in repr_str


class TestEventListenerDetector:
    """测试事件监听器检测器"""
    
    @pytest.fixture
    def detector(self):
        """创建检测器实例"""
        return EventListenerDetector()
    
    def test_init(self, detector):
        """测试初始化"""
        assert detector is not None
        assert len(detector.INTERACTIVE_EVENTS) > 0
    
    def test_has_interactive_events_true(self, detector):
        """测试检测交互事件（有）"""
        listeners = [
            EventListenerInfo(type="click"),
            EventListenerInfo(type="hover"),  # 非交互事件
        ]
        
        result = detector.has_interactive_events(listeners)
        assert result is True
    
    def test_has_interactive_events_false(self, detector):
        """测试检测交互事件（无）"""
        listeners = [
            EventListenerInfo(type="scroll"),
            EventListenerInfo(type="resize"),
        ]
        
        result = detector.has_interactive_events(listeners)
        assert result is False
    
    def test_has_interactive_events_empty(self, detector):
        """测试空列表"""
        listeners = []
        
        result = detector.has_interactive_events(listeners)
        assert result is False
    
    def test_has_event_type_true(self, detector):
        """测试检测特定事件类型（有）"""
        listeners = [
            EventListenerInfo(type="click"),
            EventListenerInfo(type="input"),
        ]
        
        assert detector.has_event_type(listeners, "click") is True
        assert detector.has_event_type(listeners, "input") is True
    
    def test_has_event_type_false(self, detector):
        """测试检测特定事件类型（无）"""
        listeners = [
            EventListenerInfo(type="click"),
        ]
        
        assert detector.has_event_type(listeners, "submit") is False
    
    def test_filter_by_type(self, detector):
        """测试按类型过滤"""
        listeners = [
            EventListenerInfo(type="click"),
            EventListenerInfo(type="input"),
            EventListenerInfo(type="change"),
            EventListenerInfo(type="scroll"),
        ]
        
        filtered = detector.filter_by_type(listeners, ["click", "input"])
        
        assert len(filtered) == 2
        assert filtered[0].type == "click"
        assert filtered[1].type == "input"
    
    def test_filter_by_type_no_match(self, detector):
        """测试按类型过滤（无匹配）"""
        listeners = [
            EventListenerInfo(type="click"),
        ]
        
        filtered = detector.filter_by_type(listeners, ["submit"])
        
        assert len(filtered) == 0
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要 Mock CDP 客户端")
    async def test_get_event_listeners(self, detector, mocker):
        """测试获取事件监听器（需要 Mock）"""
        # Mock CDP 客户端
        mock_cdp_client = mocker.Mock()
        
        # Mock resolveNode 响应
        mock_cdp_client.send.side_effect = [
            # resolveNode 响应
            {"object": {"objectId": "obj123"}},
            # getEventListeners 响应
            {
                "listeners": [
                    {"type": "click", "useCapture": False, "passive": False, "once": False},
                    {"type": "input", "useCapture": False, "passive": True, "once": False},
                ]
            }
        ]
        
        # 调用
        listeners = await detector.get_event_listeners(
            cdp_client=mock_cdp_client,
            node_id=123,
            session_id="session_abc"
        )
        
        # 断言
        assert len(listeners) == 2
        assert listeners[0].type == "click"
        assert listeners[1].type == "input"
        assert listeners[1].passive is True


class TestEventListenerDetectorIntegration:
    """集成测试（需要真实环境）"""
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要真实 CDP 环境")
    async def test_real_cdp_detection(self):
        """测试真实 CDP 环境（跳过）"""
        # 这个测试需要真实的浏览器环境
        # 在有 CDP Session 时可以运行
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

