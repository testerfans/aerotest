"""测试用例 Schema"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from aerotest.core.types import TestStep


class TestCaseCreate(BaseModel):
    """创建测试用例请求"""

    name: str = Field(description="测试用例名称")
    description: Optional[str] = Field(default=None, description="测试用例描述")
    steps: List[TestStep] = Field(description="测试步骤列表")
    tags: Optional[List[str]] = Field(default=None, description="标签")
    priority: Optional[int] = Field(default=3, description="优先�?(1-5)")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="额外元数�?)


class TestCaseResponse(BaseModel):
    """测试用例响应"""

    id: str = Field(description="测试用例 ID")
    name: str = Field(description="测试用例名称")
    description: Optional[str] = Field(default=None, description="测试用例描述")
    steps: List[TestStep] = Field(description="测试步骤列表")
    tags: List[str] = Field(description="标签")
    priority: int = Field(description="优先�?(1-5)")
    created_at: Optional[str] = Field(default=None, description="创建时间")
    updated_at: Optional[str] = Field(default=None, description="更新时间")

