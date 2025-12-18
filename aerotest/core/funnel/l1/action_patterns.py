"""动作模式�?

定义各种动作的识别模式和同义�?
"""

from aerotest.core.funnel.types import ActionType

# 动作关键词映�?
ACTION_KEYWORDS = {
    ActionType.CLICK: {
        "keywords": ["点击", "�?, "选择", "单击", "双击", "�?, "tap", "click"],
        "patterns": [
            r"点击.*",
            r"�?*",
            r"选择.*",
            r".*�?*",
        ],
    },
    ActionType.INPUT: {
        "keywords": ["输入", "填写", "录入", "键入", "�?, "�?, "enter", "input", "type"],
        "patterns": [
            r"输入.*",
            r"填写.*",
            r".*输入.*",
            r".*�?*",
        ],
    },
    ActionType.SELECT: {
        "keywords": ["选择", "选中", "勾�?, "�?, "pick", "select", "choose"],
        "patterns": [
            r"选择.*",
            r"勾�?*",
            r".*�?*",
        ],
    },
    ActionType.NAVIGATE: {
        "keywords": ["打开", "访问", "跳转", "进入", "go", "navigate", "open"],
        "patterns": [
            r"打开.*",
            r"访问.*",
            r"跳转.*",
        ],
    },
    ActionType.WAIT: {
        "keywords": ["等待", "暂停", "�?, "wait", "sleep", "pause"],
        "patterns": [
            r"等待.*",
            r"暂停.*",
        ],
    },
    ActionType.HOVER: {
        "keywords": ["悬停", "移动", "hover", "mouseover"],
        "patterns": [
            r"悬停.*",
            r"移动.*�?*",
        ],
    },
    ActionType.DRAG: {
        "keywords": ["拖动", "拖拽", "�?, "drag", "拖放"],
        "patterns": [
            r"拖动.*",
            r"拖拽.*",
            r"�?*�?*",
        ],
    },
    ActionType.SCROLL: {
        "keywords": ["滚动", "滑动", "scroll", "swipe"],
        "patterns": [
            r"滚动.*",
            r"滑动.*",
        ],
    },
}

# 动作优先级（数字越大优先级越高）
ACTION_PRIORITY = {
    ActionType.CLICK: 10,
    ActionType.INPUT: 9,
    ActionType.SELECT: 8,
    ActionType.NAVIGATE: 7,
    ActionType.DRAG: 6,
    ActionType.HOVER: 5,
    ActionType.SCROLL: 4,
    ActionType.WAIT: 3,
}

# 上下文关联词（帮助消歧）
CONTEXT_HINTS = {
    "按钮": ActionType.CLICK,
    "链接": ActionType.CLICK,
    "输入�?: ActionType.INPUT,
    "文本�?: ActionType.INPUT,
    "复选框": ActionType.SELECT,
    "单选框": ActionType.SELECT,
    "下拉�?: ActionType.SELECT,
    "菜单": ActionType.CLICK,
}

