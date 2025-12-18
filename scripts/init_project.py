"""项目初始化脚本"""

import asyncio
import shutil
from pathlib import Path


async def main():
    """初始化项目"""
    print("初始化 AeroTest AI 项目...")

    # 创建 .env 文件
    env_example = Path(".env.example")
    env_file = Path(".env")

    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✓ 已创建 .env 文件")
    else:
        print("✓ .env 文件已存在")

    # 创建必要的目录
    dirs = [
        "logs",
        "data/knowledge_base",
        "data/reports",
        "data/screenshots",
    ]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ 已创建目录: {dir_path}")

    print("\n初始化完成！")
    print("\n下一步:")
    print("1. 编辑 .env 文件，配置必要的参数")
    print("2. 运行 'poetry install' 安装依赖")
    print("3. 运行 'poetry run alembic upgrade head' 初始化数据库")
    print("4. 运行 'poetry run aerotest serve' 启动服务")


if __name__ == "__main__":
    asyncio.run(main())

