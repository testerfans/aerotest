"""配置模块测试"""

from aerotest.config import Settings, get_settings


def test_settings_creation():
    """测试配置创建"""
    settings = Settings()
    assert settings is not None
    assert settings.app_env in ["development", "testing", "production"]


def test_get_settings():
    """测试获取配置单例"""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


def test_is_development():
    """测试开发环境判断"""
    settings = Settings(app_env="development")
    assert settings.is_development is True
    assert settings.is_production is False


def test_is_production():
    """测试生产环境判断"""
    settings = Settings(app_env="production")
    assert settings.is_development is False
    assert settings.is_production is True

