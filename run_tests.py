#!/usr/bin/env python
"""运行测试的便捷脚本"""
import subprocess
import sys
import time
import requests
from pathlib import Path


def check_server_running():
    """检查服务器是否运行"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("Sora2API 接口测试")
    print("=" * 60)
    
    # 检查服务器是否运行
    print("\n[1/3] 检查服务器状态...")
    if not check_server_running():
        print("[ERROR] 错误: 服务器未运行!")
        print("   请先启动服务器: python main.py")
        sys.exit(1)
    print("[OK] 服务器正在运行")
    
    # 检查测试依赖
    print("\n[2/3] 检查测试依赖...")
    try:
        import pytest
        import httpx
        print("[OK] 测试依赖已安装")
    except ImportError:
        print("[ERROR] 错误: 测试依赖未安装!")
        print("   请运行: pip install -r requirements-test.txt")
        sys.exit(1)
    
    # 运行测试
    print("\n[3/3] 运行测试...")
    print("-" * 60)
    
    # 构建 pytest 命令
    test_dir = Path(__file__).parent / "tests"
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_dir),
        "-v",
        "--tb=short"
    ]
    
    # 如果提供了参数，传递给 pytest
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    # 运行测试
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()

