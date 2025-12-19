"""CDP 类型定义

简化的 CDP 类型定义，移除对 cdp_use 的依�?
"""

from enum import Enum
from typing import Any


class ShadowRootType(str, Enum):
    """Shadow DOM 类型"""

    OPEN = "open"
    CLOSED = "closed"


class AXPropertyName(str, Enum):
    """AX 属性名称枚�?""

    # 交互状�?
    CHECKED = "checked"
    SELECTED = "selected"
    EXPANDED = "expanded"
    PRESSED = "pressed"
    DISABLED = "disabled"
    INVALID = "invalid"
    
    # 值相�?
    VALUEMIN = "valuemin"
    VALUEMAX = "valuemax"
    VALUENOW = "valuenow"
    VALUETEXT = "valuetext"
    
    # 键盘快捷�?
    KEYSHORTCUTS = "keyshortcuts"
    
    # 弹出菜单
    HASPOPUP = "haspopup"
    
    # 多�?
    MULTISELECTABLE = "multiselectable"
    
    # 其他
    REQUIRED = "required"
    LEVEL = "level"
    BUSY = "busy"
    LIVE = "live"
    
    # 可聚焦和可编�?
    FOCUSABLE = "focusable"
    EDITABLE = "editable"
    SETTABLE = "settable"
    
    # 隐藏
    HIDDEN = "hidden"
    
    # 自动完成
    AUTOCOMPLETE = "autocomplete"


# 类型别名
TargetID = str
SessionID = str

