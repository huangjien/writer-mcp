#!/usr/bin/env python3
"""启动Writer MCP服务器的脚本。"""

import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from writer_mcp.server import create_server
from writer_mcp.config import get_settings
from writer_mcp.utils.logger import get_logger

logger = get_logger(__name__)

async def main():
    """启动MCP服务器。"""
    try:
        # 加载配置
        settings = get_settings()
        logger.info(f"启动 {settings.app_name} MCP服务器...")
        logger.info(f"调试模式: {settings.debug}")
        
        # 创建并启动服务器
        server = create_server()
        
        # 运行服务器
        async with server:
            await server.run()
            
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())