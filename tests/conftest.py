"""Pytest 配置文件"""
import pytest
import httpx
import asyncio
from typing import AsyncGenerator


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """创建全局 HTTP 客户端"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client

