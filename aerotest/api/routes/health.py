"""健康检查路由"""

from datetime import datetime

from fastapi import APIRouter

from aerotest import __version__

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """
    健康检查接口

    Returns:
        健康状态信息
    """
    return {
        "status": "healthy",
        "version": __version__,
        "timestamp": datetime.now().isoformat(),
    }


@router.get("/ping")
async def ping() -> dict:
    """
    Ping 接口

    Returns:
        Pong 响应
    """
    return {"message": "pong"}
