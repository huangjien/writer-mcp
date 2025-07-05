# Writer MCP

A Model Context Protocol (MCP) server for managing character knowledge and relationships in creative writing projects.

## Features

- Character management with rich descriptions and metadata
- Knowledge facts storage with semantic search capabilities
- Character relationship tracking and analysis
- AI-powered tag generation and relationship analysis
- Vector embeddings for semantic search
- PostgreSQL backend with connection pooling

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd writer-mcp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your database and API credentials:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/writer_mcp
TEST_DATABASE_URL=postgresql://username:password@localhost:5432/writer_mcp_test

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# Application Configuration
APP_NAME=Writer MCP
DEBUG_MODE=true

# Vector Configuration
VECTOR_DIMENSION=1536

# Search Configuration
DEFAULT_SEARCH_LIMIT=10
MAX_SEARCH_LIMIT=100

# MCP Server Configuration
MCP_SERVER_NAME=writer-mcp
MCP_SERVER_VERSION=1.0.0
```

## Usage

### 启动服务器

```bash
# 初始化数据库（首次运行）
python scripts/init_db.py

# 启动MCP服务器
python run_server.py
```

### 可用工具

1. **create_character** - 创建新角色
2. **search_characters** - 搜索角色
3. **add_character_fact** - 添加角色事实
4. **search_facts** - 搜索事实
5. **generate_character_tags** - 生成角色标签
6. **analyze_character_relationships** - 分析角色关系

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Start development server
python scripts/dev_server.py
```

## Project Structure

```
writer-mcp/
├── src/writer_mcp/          # 主要源代码
│   ├── config.py            # 配置管理
│   ├── server.py            # MCP服务器
│   ├── database/            # 数据库相关
│   ├── schemas/             # 数据模型
│   ├── services/            # 业务逻辑
│   ├── tools/               # MCP工具定义
│   └── utils/               # 工具函数
├── scripts/                 # 脚本文件
├── tests/                   # 测试文件
├── run_server.py            # 服务器启动脚本
└── main.py                  # 主入口文件
```

## License

MIT License - see LICENSE file for details.
