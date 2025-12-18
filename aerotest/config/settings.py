"""配置管理

使用 Pydantic 进行配置管理
"""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 项目信息
    project_name: str = "AeroTest AI"
    version: str = "0.1.0"

    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # 数据库配置
    database_url: str = "sqlite:///./aerotest.db"

    # AI 模型配置
    dashscope_api_key: str = Field(default="", description="阿里云百炼平台 API Key")
    model_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="阿里云百炼平台 API Base URL",
    )
    qwen_max_model: str = "qwen-max"
    qwen_plus_model: str = "qwen-plus"
    qwen_vl_model: str = "qwen-vl-max"

    # CDP 配置
    cdp_host: str = "localhost"
    cdp_port: int = 9222

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取配置实例（单例）"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
