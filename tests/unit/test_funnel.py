"""漏斗引擎测试"""

import pytest

from aerotest.core.funnel.engine import FunnelEngine, FunnelResult
from aerotest.core.types import ElementLocatorStrategy


@pytest.fixture
def mock_dom_adapter():
    """模拟 DOM 适配器"""

    class MockDomAdapter:
        async def find_clickable_elements(self):
            return []

    return MockDomAdapter()


def test_funnel_result_creation():
    """测试漏斗结果创建"""
    result = FunnelResult(
        strategy=ElementLocatorStrategy.L1_RULE, element=None, confidence=0.8
    )

    assert result.strategy == ElementLocatorStrategy.L1_RULE
    assert result.confidence == 0.8
    assert not result.is_success()


def test_funnel_result_success():
    """测试漏斗结果成功状态"""
    result = FunnelResult(
        strategy=ElementLocatorStrategy.L2_ATTRIBUTE,
        element={"xpath": "//div[@id='test']"},
        confidence=0.9,
    )

    assert result.is_success()


@pytest.mark.asyncio
async def test_funnel_engine_creation(mock_dom_adapter):
    """测试漏斗引擎创建"""
    engine = FunnelEngine(mock_dom_adapter)
    assert engine is not None
    assert engine.dom_adapter is mock_dom_adapter


@pytest.mark.asyncio
async def test_funnel_engine_locate_element(mock_dom_adapter):
    """测试元素定位（目前返回失败结果）"""
    engine = FunnelEngine(mock_dom_adapter)
    result = await engine.locate_element("登录按钮")

    assert isinstance(result, FunnelResult)
    # 由于还没有实现具体的层，应该返回失败结果
    assert result.strategy == ElementLocatorStrategy.FALLBACK

