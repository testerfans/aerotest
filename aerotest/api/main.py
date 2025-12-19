"""FastAPI 应用主入口"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aerotest.config import get_settings
from aerotest.utils import get_logger

logger = get_logger("aerotest.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    logger.info("AeroTest API 启动中...")

    # 启动时的初始化逻辑
    # TODO: 初始化数据库连接池
    # TODO: 初始化 Redis 连接

    yield

    # 关闭时的清理逻辑
    logger.info("AeroTest API 关闭中...")
    # TODO: 关闭数据库连接
    # TODO: 关闭 Redis 连接


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    settings = get_settings()

    app = FastAPI(
        title="AeroTest AI",
        description="基于 AI 驱动的通用 UI 自动化测试平台",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_development else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    register_routes(app)

    return app


def register_routes(app: FastAPI) -> None:
    """注册 API 路由"""
    from aerotest.api.routes import health, test_cases

    app.include_router(health.router, prefix="/api", tags=["Health"])
    app.include_router(test_cases.router, prefix="/api/v1", tags=["Test Cases"])


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "aerotest.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )
