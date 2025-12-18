"""CDP 类型定义

定义 CDP 模块使用的数据结构和类型
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CDPConnectionConfig:
    """CDP 连接配置
    
    用于配置如何连接�?Chrome DevTools Protocol
    
    Attributes:
        host: CDP 服务器地址（通常�?localhost�?
        port: CDP 端口（Chrome 默认 9222�?
        timeout: 连接超时时间（秒�?
        max_retries: 最大重试次�?
    """
    
    host: str = "localhost"
    port: int = 9222
    timeout: float = 30.0
    max_retries: int = 3
    
    @property
    def ws_url(self) -> str:
        """获取 WebSocket URL"""
        return f"ws://{self.host}:{self.port}"
    
    @property
    def http_url(self) -> str:
        """获取 HTTP URL"""
        return f"http://{self.host}:{self.port}"


@dataclass
class TargetInfo:
    """浏览器目标信�?
    
    Target 代表一个浏览上下文（页面、iframe、worker等）
    
    Attributes:
        target_id: 目标唯一标识�?
        target_type: 目标类型（page, iframe, worker等）
        url: 当前 URL
        title: 页面标题
        attached: 是否已附加会�?
    """
    
    target_id: str
    target_type: str
    url: str = "about:blank"
    title: str = ""
    attached: bool = False
    
    @property
    def is_page(self) -> bool:
        """是否是页面类�?""
        return self.target_type == "page"
    
    @property
    def is_iframe(self) -> bool:
        """是否�?iframe"""
        return self.target_type == "iframe"


@dataclass
class PageInfo:
    """页面信息
    
    包含页面的详细信息，包括目标和会�?ID
    
    Attributes:
        target_info: 目标信息
        session_id: CDP 会话 ID
        ready_state: 页面就绪状�?
    """
    
    target_info: TargetInfo
    session_id: Optional[str] = None
    ready_state: str = "loading"
    
    @property
    def target_id(self) -> str:
        """获取目标 ID"""
        return self.target_info.target_id
    
    @property
    def url(self) -> str:
        """获取 URL"""
        return self.target_info.url
    
    @property
    def title(self) -> str:
        """获取标题"""
        return self.target_info.title
    
    @property
    def is_ready(self) -> bool:
        """页面是否就绪"""
        return self.ready_state in ("interactive", "complete")


@dataclass
class DOMFetchResult:
    """DOM 获取结果
    
    包含从浏览器获取的各�?DOM 相关数据
    
    Attributes:
        snapshot: DOM 快照
        dom_tree: DOM �?
        ax_tree: 辅助功能�?
        device_pixel_ratio: 设备像素�?
        timing: 性能计时信息
    """
    
    snapshot: dict
    dom_tree: dict
    ax_tree: dict
    device_pixel_ratio: float = 1.0
    timing: dict = field(default_factory=dict)


@dataclass
class ClickOptions:
    """点击选项
    
    Attributes:
        button: 鼠标按钮（left, right, middle�?
        click_count: 点击次数
        delay: 点击延迟（毫秒）
    """
    
    button: str = "left"
    click_count: int = 1
    delay: float = 0


@dataclass
class TypeOptions:
    """输入选项
    
    Attributes:
        delay: 按键间隔（毫秒）
        clear_first: 是否先清�?
    """
    
    delay: float = 50
    clear_first: bool = True


@dataclass
class ScreenshotOptions:
    """截图选项
    
    Attributes:
        format: 图片格式（png, jpeg�?
        quality: JPEG 质量�?-100�?
        full_page: 是否全页截图
    """
    
    format: str = "png"
    quality: int = 90
    full_page: bool = False

