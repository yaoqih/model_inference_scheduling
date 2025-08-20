#!/usr/bin/env python3
"""
开发环境启动脚本
"""
import uvicorn
import sys
import os

# 添加backend目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug",
        workers=4
    )