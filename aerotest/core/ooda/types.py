"""OODA 循环数据类型

定义 OODA 循环中的所有核心数据结�?
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from aerotest.browser.dom.views import EnhancedDOMTreeNode
from aerotest.core.funnel.types import MatchResult


class ActionType(str, Enum):
    """操作类型"""

    CLICK = "click"
    INPUT = "input"
    SELECT = "select"
    CHECK = "check"
    UNCHECK = "uncheck"
    SUBMIT = "submit"
    NAVIGATE = "navigate"
    WAIT = "wait"
    SCROLL = "scroll"
    HOVER = "hover"
    ASSERT = "assert"


class ActionStatus(str, Enum):
    """操作状�?""

    PENDING = "pending"  # 待执�?
    RUNNING = "running"  # 执行�?
    SUCCESS = "success"  # 成功
    FAILED = "failed"  # 失败
    SKIPPED = "skipped"  # 跳过
    RETRY = "retry"  # 重试�?


@dataclass
class Observation:
    """观察（Observe�?
    
    从当前页面状态收集的信息
    """

    # DOM �?
    dom_tree: Optional[EnhancedDOMTreeNode] = None

    # 页面信息
    url: str = ""
    title: str = ""
    viewport_size: tuple = (1920, 1080)

    # 可见元素
    visible_elements: List[EnhancedDOMTreeNode] = field(default_factory=list)

    # 可交互元�?
    interactive_elements: List[EnhancedDOMTreeNode] = field(default_factory=list)

    # 页面截图（Base64�?
    screenshot: Optional[str] = None

    # 观察时间
    timestamp: datetime = field(default_factory=datetime.now)

    # 额外信息
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Orientation:
    """定向（Orient�?
    
    对观察到的信息进行分析和理解
    """

    # 当前步骤
    current_step: Optional["TestStep"] = None

    # 提取的槽位（L1�?
    action_slot: Optional[Any] = None  # ActionSlot from L1

    # 候选元素（L2-L5�?
    candidate_elements: List[MatchResult] = field(default_factory=list)

    # 最佳匹�?
    best_match: Optional[MatchResult] = None

    # 匹配策略
    strategy: str = ""  # L1, L2, L3, L4, L5

    # 置信�?
    confidence: float = 0.0

    # 分析时间
    timestamp: datetime = field(default_factory=datetime.now)

    # 额外信息
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    """决策（Decide�?
    
    基于分析结果做出的执行决�?
    """

    # 决策类型
    action_type: ActionType

    # 目标元素
    target_element: Optional[EnhancedDOMTreeNode] = None

    # 操作参数
    parameters: Dict[str, Any] = field(default_factory=dict)

    # 是否执行
    should_execute: bool = True

    # 决策原因
    reason: str = ""

    # 备选方�?
    fallback_decisions: List["Decision"] = field(default_factory=list)

    # 决策时间
    timestamp: datetime = field(default_factory=datetime.now)

    # 额外信息
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Action:
    """行动（Act�?
    
    实际执行的操作和结果
    """

    # 操作类型
    action_type: ActionType

    # 目标元素
    target_element: Optional[EnhancedDOMTreeNode] = None

    # 操作参数
    parameters: Dict[str, Any] = field(default_factory=dict)

    # 执行状�?
    status: ActionStatus = ActionStatus.PENDING

    # 执行结果
    result: Optional[Any] = None

    # 错误信息
    error: Optional[str] = None

    # 重试次数
    retry_count: int = 0

    # 执行耗时（毫秒）
    duration_ms: float = 0.0

    # 开始时�?
    start_time: Optional[datetime] = None

    # 结束时间
    end_time: Optional[datetime] = None

    # 额外信息
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestStep:
    """测试步骤
    
    一个完整的测试步骤，包含完整的 OODA 循环
    """

    # 步骤 ID
    step_id: str

    # 步骤描述（自然语言�?
    description: str

    # 步骤类型
    action_type: ActionType

    # 期望值（用于断言�?
    expected_value: Optional[Any] = None

    # OODA 循环数据
    observation: Optional[Observation] = None
    orientation: Optional[Orientation] = None
    decision: Optional[Decision] = None
    action: Optional[Action] = None

    # 步骤状�?
    status: ActionStatus = ActionStatus.PENDING

    # 错误信息
    error: Optional[str] = None

    # 执行耗时（毫秒）
    duration_ms: float = 0.0

    # 开始时�?
    start_time: Optional[datetime] = None

    # 结束时间
    end_time: Optional[datetime] = None

    # 额外信息
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestCase:
    """测试用例
    
    包含多个测试步骤的完整测试用�?
    """

    # 用例 ID
    case_id: str

    # 用例名称
    name: str

    # 用例描述
    description: str = ""

    # 测试步骤
    steps: List[TestStep] = field(default_factory=list)

    # 用例状�?
    status: ActionStatus = ActionStatus.PENDING

    # 执行上下�?
    context: Dict[str, Any] = field(default_factory=dict)

    # 环境配置
    environment: Dict[str, Any] = field(default_factory=dict)

    # 执行耗时（毫秒）
    duration_ms: float = 0.0

    # 开始时�?
    start_time: Optional[datetime] = None

    # 结束时间
    end_time: Optional[datetime] = None

    # 额外信息
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionContext:
    """执行上下�?
    
    用于�?OODA 循环中传递状态和依赖
    """

    # CDP Session（如果需要）
    cdp_session: Optional[Any] = None

    # Target ID
    target_id: Optional[str] = None

    # 变量存储
    variables: Dict[str, Any] = field(default_factory=dict)

    # 执行配置
    config: Dict[str, Any] = field(default_factory=dict)

    # 历史记录
    history: List[TestStep] = field(default_factory=list)

    # 额外信息
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """执行结果
    
    测试用例或步骤的执行结果
    """

    # 是否成功
    success: bool

    # 状�?
    status: ActionStatus

    # 结果数据
    data: Optional[Any] = None

    # 错误信息
    error: Optional[str] = None

    # 执行耗时（毫秒）
    duration_ms: float = 0.0

    # 步骤结果列表（用于用例）
    step_results: List["ExecutionResult"] = field(default_factory=list)

    # 统计信息
    stats: Dict[str, Any] = field(default_factory=dict)

    # 额外信息
    metadata: Dict[str, Any] = field(default_factory=dict)

