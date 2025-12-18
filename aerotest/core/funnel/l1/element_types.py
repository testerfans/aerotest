"""元素类型�?

定义各种元素类型的识别模式和关键�?
"""

from aerotest.core.funnel.types import ElementType

# 元素类型关键词映�?
ELEMENT_TYPE_KEYWORDS = {
    ElementType.BUTTON: {
        "keywords": ["按钮", "按键", "button", "btn", "确认", "提交", "取消", "关闭"],
        "patterns": [
            r".*按钮$",
            r".*button$",
            r".*btn$",
        ],
        "tags": ["button", "input[type='button']", "input[type='submit']"],
    },
    ElementType.INPUT: {
        "keywords": ["输入�?, "文本�?, "input", "输入", "�?, "field"],
        "patterns": [
            r".*输入�?",
            r".*文本�?",
            r".*input$",
        ],
        "tags": ["input[type='text']", "input[type='password']", "input[type='email']"],
    },
    ElementType.TEXTAREA: {
        "keywords": ["文本�?, "多行输入", "textarea", "文本�?],
        "patterns": [
            r".*文本�?",
            r".*textarea$",
        ],
        "tags": ["textarea"],
    },
    ElementType.SELECT: {
        "keywords": ["下拉�?, "下拉菜单", "选择�?, "select", "下拉", "dropdown"],
        "patterns": [
            r".*下拉�?",
            r".*下拉菜单$",
            r".*select$",
        ],
        "tags": ["select"],
    },
    ElementType.CHECKBOX: {
        "keywords": ["复选框", "多选框", "checkbox", "勾选框"],
        "patterns": [
            r".*复选框$",
            r".*多选框$",
            r".*checkbox$",
        ],
        "tags": ["input[type='checkbox']"],
    },
    ElementType.RADIO: {
        "keywords": ["单选框", "单选按�?, "radio", "单�?],
        "patterns": [
            r".*单选框$",
            r".*单选按�?",
            r".*radio$",
        ],
        "tags": ["input[type='radio']"],
    },
    ElementType.LINK: {
        "keywords": ["链接", "超链�?, "link", "a标签", "href"],
        "patterns": [
            r".*链接$",
            r".*超链�?",
            r".*link$",
        ],
        "tags": ["a"],
    },
    ElementType.DIV: {
        "keywords": ["div", "容器", "区域", "�?],
        "patterns": [
            r".*div$",
            r".*容器$",
        ],
        "tags": ["div"],
    },
    ElementType.SPAN: {
        "keywords": ["span", "文本", "标签"],
        "patterns": [
            r".*span$",
        ],
        "tags": ["span"],
    },
    ElementType.LABEL: {
        "keywords": ["标签", "label", "文本标签"],
        "patterns": [
            r".*标签$",
            r".*label$",
        ],
        "tags": ["label"],
    },
}

# 元素属性提示（常见的属性名�?
ELEMENT_ATTRIBUTE_HINTS = {
    ElementType.BUTTON: ["type=button", "type=submit", "role=button"],
    ElementType.INPUT: ["type=text", "type=password", "type=email", "type=tel"],
    ElementType.CHECKBOX: ["type=checkbox"],
    ElementType.RADIO: ["type=radio"],
    ElementType.LINK: ["href"],
}

# 常见元素描述词和其对应的类型
COMMON_ELEMENT_NAMES = {
    # 按钮相关
    "提交": ElementType.BUTTON,
    "确认": ElementType.BUTTON,
    "取消": ElementType.BUTTON,
    "关闭": ElementType.BUTTON,
    "删除": ElementType.BUTTON,
    "保存": ElementType.BUTTON,
    "发�?: ElementType.BUTTON,
    "登录": ElementType.BUTTON,
    "注册": ElementType.BUTTON,
    "搜索": ElementType.BUTTON,
    
    # 输入框相�?
    "用户�?: ElementType.INPUT,
    "密码": ElementType.INPUT,
    "邮箱": ElementType.INPUT,
    "手机": ElementType.INPUT,
    "电话": ElementType.INPUT,
    "地址": ElementType.INPUT,
    "姓名": ElementType.INPUT,
    
    # 选择框相�?
    "下拉": ElementType.SELECT,
    "选项": ElementType.SELECT,
    
    # 复选框/单选框
    "同意": ElementType.CHECKBOX,
    "勾�?: ElementType.CHECKBOX,
    "选择": ElementType.CHECKBOX,  # 可能是多种类�?
}

# 上下文提示（前后文词汇帮助判断）
CONTEXT_PATTERNS = {
    # 如果包含这些词，更可能是某种类型
    "请输�?: ElementType.INPUT,
    "请选择": ElementType.SELECT,
    "请勾�?: ElementType.CHECKBOX,
    "打开链接": ElementType.LINK,
}

