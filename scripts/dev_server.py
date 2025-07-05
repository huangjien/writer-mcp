#!/usr/bin/env python3
"""Development server script for Writer MCP."""

import asyncio
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from writer_mcp.server import main
from writer_mcp.utils.logger import setup_logging


if __name__ == "__main__":
    # Setup logging for development
    setup_logging()
    
    # Run the MCP server
    asyncio.run(main())