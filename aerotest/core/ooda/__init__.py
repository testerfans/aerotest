"""OODA 循环模块

实现完整的 OODA (Observe-Orient-Decide-Act) 循环
用于 UI 自动化测试的智能执行
"""

from aerotest.core.ooda.case_executor import CaseExecutor
from aerotest.core.ooda.ooda_engine import OODAEngine
from aerotest.core.ooda.types import (
    Action,
    ActionStatus,
    ActionType,
    Decision,
    ExecutionContext,
    ExecutionResult,
    Observation,
    Orientation,
    TestCase,
    TestStep,
)

__all__ = [
    # OODA 引擎
    "OODAEngine",
    "CaseExecutor",
    # 数据类型
    "Action",
    "ActionType",
    "ActionStatus",
    "Decision",
    "ExecutionContext",
    "ExecutionResult",
    "Observation",
    "Orientation",
    "TestCase",
    "TestStep",
]
