#!/bin/bash
# 生成数据库迁移脚本

if [ -z "$1" ]; then
    echo "Usage: $0 <migration_message>"
    exit 1
fi

poetry run alembic revision --autogenerate -m "$1"

