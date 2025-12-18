"""命令行工�?""

import asyncio

import click

from aerotest import __version__
from aerotest.config import get_settings
from aerotest.utils import get_logger

logger = get_logger("aerotest.cli")


@click.group()
@click.version_option(version=__version__)
def main() -> None:
    """AeroTest AI - 智能 UI 自动化测试平�?""
    pass


@main.command()
@click.option("--host", default=None, help="服务器地址")
@click.option("--port", default=None, type=int, help="服务器端�?)
@click.option("--reload", is_flag=True, help="开启热重载")
def serve(host: str | None, port: int | None, reload: bool) -> None:
    """启动 API 服务"""
    import uvicorn

    settings = get_settings()

    uvicorn.run(
        "aerotest.api.main:app",
        host=host or settings.api_host,
        port=port or settings.api_port,
        reload=reload or settings.api_reload,
    )


@main.command()
@click.argument("test_case_file")
def run(test_case_file: str) -> None:
    """运行测试用例"""
    logger.info(f"运行测试用例: {test_case_file}")

    async def execute() -> None:
        from aerotest.core.client import AeroTestClient

        client = AeroTestClient()

        # TODO: 从文件加载测试用�?
        # test_case = load_test_case(test_case_file)
        # result = await client.execute_test(test_case)

        logger.info("测试执行完成")

    asyncio.run(execute())


@main.command()
def init() -> None:
    """初始化项目配�?""
    import shutil
    from pathlib import Path

    logger.info("初始�?AeroTest AI 项目")

    # 创建 .env 文件
    env_example = Path(".env.example")
    env_file = Path(".env")

    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        logger.info("已创�?.env 文件")
    else:
        logger.info(".env 文件已存�?)

    # 创建必要的目�?
    dirs = ["logs", "data/knowledge_base", "data/reports"]
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        logger.info(f"已创建目�? {dir_path}")

    logger.info("初始化完�?)


@main.command()
def db_init() -> None:
    """初始化数据库"""
    logger.info("初始化数据库...")

    async def init_db() -> None:
        from aerotest.db.base import Base
        from aerotest.db.session import engine

        # 导入所有模�?
        from aerotest.db.models import TestCase, TestResult  # noqa

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("数据库初始化完成")

    asyncio.run(init_db())


if __name__ == "__main__":
    main()

