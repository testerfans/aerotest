"""éç½®ç®¡ç

ä½¿ç¨ Pydantic è¿è¡éç½®ç®¡ç
"""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """åºç¨éç½®"""

    # é¡¹ç®ä¿¡æ¯
    project_name: str = "AeroTest AI"
    version: str = "0.1.0"

    # æ¥å¿éç½®
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # æ°æ®åºéç½®
    database_url: str = "sqlite:///./aerotest.db"

    # AI æ¨¡åéç½®
    dashscope_api_key: str = Field(default="", description="é¿éäºç¾ç¼å¹³å° API Key")
    model_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="é¿éäºç¾ç¼å¹³å° API Base URL",
    )
    qwen_max_model: str = "qwen-max"
    qwen_plus_model: str = "qwen-plus"
    qwen_vl_model: str = "qwen-vl-max"

    # CDP éç½®
    cdp_host: str = "localhost"
    cdp_port: int = 9222

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# å¨å±éç½®å®ä¾
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """è·åéç½®å®ä¾ï¼åä¾ï¼"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
