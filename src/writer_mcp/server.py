"""MCP Server entry point for Writer MCP."""

import asyncio
import logging
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
)

from .config import settings
from .database.connection import DatabaseConnection
from .tools.character_tools import get_character_tools
from .utils.logger import get_logger


logger = get_logger(__name__)


class WriterMCPServer:
    """Writer MCP Server implementation."""
    
    def __init__(self) -> None:
        """Initialize the server."""
        self.server = Server(settings.mcp_server_name)
        self.db: DatabaseConnection | None = None
        self._setup_handlers()
        
    def _setup_handlers(self) -> None:
        """Setup MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools."""
            tools = get_character_tools()
            return ListToolsResult(tools=tools)
            
        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            """Handle tool calls."""
            try:
                # Import tool handlers
                from .tools.character_tools import handle_tool_call
                
                result = await handle_tool_call(request, self.db)
                return CallToolResult(content=result)
                
            except Exception as e:
                logger.error(f"Error handling tool call {request.name}: {e}")
                return CallToolResult(
                    content=[{"type": "text", "text": f"Error: {str(e)}"}],
                    isError=True
                )
                
    async def initialize(self) -> None:
        """Initialize database connection and other resources."""
        try:
            self.db = DatabaseConnection()
            await self.db.connect()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
            
    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.db:
            await self.db.close()
            logger.info("Database connection closed")
            
    async def run(self) -> None:
        """Run the MCP server."""
        try:
            await self.initialize()
            
            # Run the server with stdio transport
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=settings.mcp_server_name,
                        server_version=settings.mcp_server_version,
                        capabilities={
                            "tools": {},
                        }
                    )
                )
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            await self.cleanup()


async def main() -> None:
    """Main entry point."""
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger.info(f"Starting Writer MCP Server v{settings.mcp_server_version}")
    logger.info(f"Environment: {settings.python_env}")
    
    server = WriterMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())