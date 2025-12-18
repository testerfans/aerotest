"""核心数据类型定义"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """操作类型枚举"""

    NAVIGATE = "navigate"
    CLICK = "click"
    INPUT = "input"
    SELECT = "select"
    SCROLL = "scroll"
    WAIT = "wait"
    ASSERT = "assert"
    EXTRACT = "extract"
    CUSTOM = "custom"


class TestStatus(str, Enum):
    """测试状态枚�?""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class ElementLocatorStrategy(str, Enum):
    """元素定位策略"""

    L1_RULE = "l1_rule"  # L1 规则槽位
    L2_ATTRIBUTE = "l2_attribute"  # L2 属性匹�?
    L3_SPATIAL = "l3_spatial"  # L3 空间推理
    L4_AI_REASONING = "l4_ai_reasoning"  # L4 AI 推理
    L5_VISION = "l5_vision"  # L5 视觉识别
    FALLBACK = "fallback"  # 降级策略


class TestStep(BaseModel):
    """测试步骤"""

    action: ActionType = Field(description="操作类型")
    selector: Optional[str] = Field(default=None, description="元素选择器（支持自然语言�?)
    value: Optional[Any] = Field(default=None, description="操作�?)
    expected: Optional[Any] = Field(default=None, description="期望结果（用于断言�?)
    timeout: Optional[int] = Field(default=None, description="超时时间（毫秒）")
    retry: Optional[int] = Field(default=3, description="重试次数")
    description: Optional[str] = Field(default=None, description="步骤描述")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="额外元数�?)


class TestCase(BaseModel):
    """测试用例"""

    name: str = Field(description="测试用例名称")
    description: Optional[str] = Field(default=None, description="测试用例描述")
    steps: List[TestStep] = Field(description="测试步骤列表")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签")
    priority: Optional[int] = Field(default=3, description="优先�?(1-5)")
    timeout: Optional[int] = Field(default=300000, description="整体超时时间（毫秒）")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="额外元数�?)


class StepResult(BaseModel):
    """步骤执行结果"""

    step: TestStep = Field(description="执行的步�?)
    status: TestStatus = Field(description="执行状�?)
    locator_strategy: Optional[ElementLocatorStrategy] = Field(
        default=None, description="使用的定位策�?
    )
    execution_time: float = Field(description="执行时间（秒�?)
    error_message: Optional[str] = Field(default=None, description="错误信息")
    screenshot_path: Optional[str] = Field(default=None, description="截图路径")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="额外元数�?)


class TestResult(BaseModel):
    """测试结果"""

    test_case: TestCase = Field(description="测试用例")
    status: TestStatus = Field(description="测试状�?)
    start_time: datetime = Field(description="开始时�?)
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    execution_time: float = Field(default=0.0, description="总执行时间（秒）")
    step_results: List[StepResult] = Field(default_factory=list, description="步骤结果列表")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    report_path: Optional[str] = Field(default=None, description="报告路径")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="额外元数�?)

    @property
    def passed_steps(self) -> int:
        """通过的步骤数"""
        return sum(1 for result in self.step_results if result.status == TestStatus.PASSED)

    @property
    def failed_steps(self) -> int:
        """失败的步骤数"""
        return sum(1 for result in self.step_results if result.status == TestStatus.FAILED)

    @property
    def total_steps(self) -> int:
        """总步骤数"""
        return len(self.step_results)

    @property
    def success_rate(self) -> float:
        """成功�?""
        if self.total_steps == 0:
            return 0.0
        return self.passed_steps / self.total_steps * 100

