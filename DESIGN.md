
# 📄 项目设计文档：MCP Server for Novel Character Knowledge Base

## 一、项目背景

目标是搭建一个基于 FastMCP、pydanticAI、PostgreSQL 的 MCP Server，用于存储、管理和检索小说人物的性格、身份、故事背景等知识碎片。系统支持通过 AI 自动生成人物标签，支持向量化模糊检索，适配后续小说创作、查询、管理等需求。

---

## 二、技术选型

| 技术                         | 用途                   |
| -------------------------- | -------------------- |
| FastMCP                    | 构建 MCP Server        |
| pydanticAI                 | 提供 AI Prompt 调用与结构校验 |
| PostgreSQL + pgvector      | 存储知识碎片与向量数据          |
| OpenAI / Claude API        | 生成标签（可后期考虑本地模型）      |
| Python (FastAPI / FastMCP) | 后端开发语言与框架            |

---

## 三、系统架构

```
+-------------------+         +-------------------+
|   MCP Client      |  --->   |  FastMCP Server   |
+-------------------+         +-------------------+
                                    |
                                    ▼
                            +-------------------+
                            |  PostgreSQL +     |
                            |  pgvector         |
                            +-------------------+
                                    ▲
                                    |
                          +----------------------+
                          | pydanticAI / OpenAI  |
                          | AI 标签生成与向量计算 |
                          +----------------------+
```

---

## 四、核心数据结构设计

### 1. Character 表（人物信息）

| 字段          | 类型        | 说明              |
| ----------- | --------- | --------------- |
| id          | UUID      | 主键              |
| name        | TEXT      | 人物名称            |
| aliases     | TEXT\[]   | 别名              |
| tags        | TEXT\[]   | 人物标签（可 AI 自动生成） |
| created\_at | TIMESTAMP | 创建时间            |
| updated\_at | TIMESTAMP | 更新时间            |

---

### 2. CharacterFact 表（人物知识碎片）

| 字段            | 类型           | 说明              |
| ------------- | ------------ | --------------- |
| id            | UUID         | 主键              |
| character\_id | UUID         | 外键              |
| fact\_type    | TEXT         | 知识类型（性格、身份、背景等） |
| content       | TEXT         | 描述内容            |
| source        | TEXT         | 来源章节            |
| tags          | TEXT\[]      | 手工或 AI 生成标签     |
| embedding     | VECTOR(1536) | 向量数据            |
| created\_at   | TIMESTAMP    | 创建时间            |
| updated\_at   | TIMESTAMP    | 更新时间            |

---

### 3. CharacterRelation 表（可选，人物关系图）

| 字段                    | 类型           | 说明              |
| --------------------- | ------------ | --------------- |
| id                    | UUID         | 主键              |
| source\_character\_id | UUID         | 关系源人物           |
| target\_character\_id | UUID         | 关系目标人物          |
| relation\_type        | TEXT         | 关系类型（朋友、敌人、爱人等） |
| description           | TEXT         | 关系描述            |
| embedding             | VECTOR(1536) | 向量数据            |
| created\_at           | TIMESTAMP    | 创建时间            |
| updated\_at           | TIMESTAMP    | 更新时间            |

---

## 五、MCP Tools 设计

### 1. 人物管理工具

#### create_character
创建新人物

**输入参数：**
```json
{
  "name": "李青",
  "aliases": ["青帮少主", "双刀李青"],
  "description": "出身青帮，性格冷静果断，擅长双刀"
}
```

**输出：**
```json
{
  "character_id": "uuid-string",
  "name": "李青",
  "tags": ["冷静", "果断", "武功高强", "青帮"],
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### search_characters
搜索人物

**输入参数：**
```json
{
  "query": "性格冷静的人物",
  "filters": {
    "tags": ["冷静"],
    "fact_types": ["性格"]
  },
  "limit": 10
}
```

### 2. 知识碎片管理工具

#### add_character_fact
添加人物知识碎片

**输入参数：**
```json
{
  "character_id": "uuid-string",
  "fact_type": "性格",
  "content": "李青在面对危险时总是保持冷静，从不慌乱",
  "source": "第三章：青帮风云",
  "tags": ["冷静", "勇敢"]
}
```

#### search_facts
搜索知识碎片

**输入参数：**
```json
{
  "query": "李青的武功如何？",
  "character_names": ["李青"],
  "fact_types": ["武功", "技能"],
  "similarity_threshold": 0.8
}
```

### 3. AI 辅助工具

#### generate_character_tags
AI 自动生成人物标签

**输入参数：**
```json
{
  "description": "李青出身青帮，性格冷静果断，擅长双刀，少年时与赵云青结义。"
}
```

**输出：**
```json
{
  "tags": ["冷静", "果断", "武功高强", "青帮", "义气", "双刀"],
  "confidence_scores": {
    "冷静": 0.95,
    "果断": 0.92,
    "武功高强": 0.88
  }
}
```

#### analyze_character_relationships
分析人物关系

**输入参数：**
```json
{
  "character_ids": ["uuid-1", "uuid-2"],
  "context": "根据现有的知识碎片分析两人关系"
}
```

---

## 六、数据库设计详细说明

### 1. 数据库表结构 SQL

#### Character 表
```sql
CREATE TABLE characters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    aliases TEXT[] DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_characters_name ON characters USING gin(name gin_trgm_ops);
CREATE INDEX idx_characters_tags ON characters USING gin(tags);
CREATE INDEX idx_characters_aliases ON characters USING gin(aliases);
CREATE INDEX idx_characters_created_at ON characters(created_at);
```

#### CharacterFact 表
```sql
CREATE TABLE character_facts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    fact_type TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT,
    tags TEXT[] DEFAULT '{}',
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_character_facts_character_id ON character_facts(character_id);
CREATE INDEX idx_character_facts_fact_type ON character_facts(fact_type);
CREATE INDEX idx_character_facts_tags ON character_facts USING gin(tags);
CREATE INDEX idx_character_facts_content ON character_facts USING gin(content gin_trgm_ops);
CREATE INDEX idx_character_facts_embedding ON character_facts USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

#### CharacterRelation 表
```sql
CREATE TABLE character_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    target_character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    description TEXT,
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT no_self_relation CHECK (source_character_id != target_character_id)
);

-- 索引
CREATE INDEX idx_character_relations_source ON character_relations(source_character_id);
CREATE INDEX idx_character_relations_target ON character_relations(target_character_id);
CREATE INDEX idx_character_relations_type ON character_relations(relation_type);
CREATE INDEX idx_character_relations_embedding ON character_relations USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

### 2. 数据库扩展和配置

```sql
-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有表添加更新时间触发器
CREATE TRIGGER update_characters_updated_at BEFORE UPDATE ON characters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_character_facts_updated_at BEFORE UPDATE ON character_facts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_character_relations_updated_at BEFORE UPDATE ON character_relations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 3. 性能优化策略

#### 向量检索优化
- 使用 IVFFlat 索引进行近似最近邻搜索
- 根据数据量调整 lists 参数（建议为行数的平方根）
- 定期运行 `VACUUM ANALYZE` 更新统计信息

#### 全文检索优化
- 使用 pg_trgm 扩展支持模糊匹配
- 为文本字段创建 GIN 索引
- 考虑使用 PostgreSQL 的全文搜索功能

#### 查询优化
- 使用连接池减少连接开销
- 实现查询结果缓存
- 对频繁查询的字段组合创建复合索引

---

## 七、API 设计规范

### 1. RESTful API 端点

#### 人物管理
```
GET    /api/v1/characters              # 获取人物列表
POST   /api/v1/characters              # 创建新人物
GET    /api/v1/characters/{id}         # 获取特定人物
PUT    /api/v1/characters/{id}         # 更新人物信息
DELETE /api/v1/characters/{id}         # 删除人物
GET    /api/v1/characters/search       # 搜索人物
```

#### 知识碎片管理
```
GET    /api/v1/characters/{id}/facts   # 获取人物的知识碎片
POST   /api/v1/characters/{id}/facts   # 添加知识碎片
PUT    /api/v1/facts/{id}              # 更新知识碎片
DELETE /api/v1/facts/{id}              # 删除知识碎片
GET    /api/v1/facts/search            # 搜索知识碎片
```

#### 人物关系管理
```
GET    /api/v1/characters/{id}/relations  # 获取人物关系
POST   /api/v1/relations                   # 创建人物关系
PUT    /api/v1/relations/{id}              # 更新关系
DELETE /api/v1/relations/{id}              # 删除关系
```

### 2. 响应格式标准

#### 成功响应
```json
{
  "success": true,
  "data": {
    // 实际数据
  },
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20
  }
}
```

#### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "输入数据验证失败",
    "details": {
      "field": "name",
      "reason": "人物名称不能为空"
    }
  }
}
```

---

## 八、开发计划与任务拆解

### 第一阶段：基础搭建（预计 1 周）

#### 1.1 项目初始化
- [x] 创建项目目录结构
- [ ] 初始化 Python 项目（pyproject.toml）
- [ ] 配置 Python 开发环境
- [ ] 设置 ruff、black 和 mypy
- [ ] 配置 Git 仓库和 .gitignore

#### 1.2 数据库环境搭建
- [ ] 安装 PostgreSQL（本地开发环境）
- [ ] 创建数据库和用户
- [ ] 安装必要的 PostgreSQL 扩展
  - [ ] uuid-ossp
  - [ ] pg_trgm
  - [ ] vector（pgvector）
- [ ] 执行数据库表创建脚本
- [ ] 验证数据库连接和基本操作

#### 1.3 基础依赖安装
- [ ] 安装 MCP SDK
- [ ] 安装数据库相关依赖（psycopg2-binary, pgvector）
- [ ] 安装向量处理库
- [ ] 安装开发工具依赖

#### 1.4 项目结构设计
```
writer-mcp/
├── src/
│   ├── writer_mcp/
│   │   ├── __init__.py
│   │   ├── server.py           # MCP 服务器入口
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py   # 数据库连接
│   │   │   ├── migrations/     # 数据库迁移文件
│   │   │   └── models/         # 数据模型
│   │   ├── tools/              # MCP 工具实现
│   │   │   └── __init__.py
│   │   ├── services/           # 业务逻辑服务
│   │   │   └── __init__.py
│   │   ├── utils/              # 工具函数
│   │   │   └── __init__.py
│   │   └── schemas/            # Pydantic 数据模型
│   │       └── __init__.py
├── tests/                      # 测试文件
├── docs/                       # 文档
├── scripts/                    # 脚本文件
├── pyproject.toml              # 项目配置和依赖
└── .env.example                # 环境变量示例
```

* [ ] 1.1 FastMCP Server 项目初始化
* [ ] 1.2 PostgreSQL + pgvector 安装与基础配置
* [ ] 1.3 建立 Character、CharacterFact、CharacterRelation 表
* [ ] 1.4 FastMCP 基础路由设计（CRUD）

### 第二阶段：核心功能开发（预计 2 周）

#### 2.1 数据模型实现（2-3 天）
- [ ] 实现 Character 模型类
  - [ ] 基础 CRUD 操作
  - [ ] 数据验证逻辑
  - [ ] 搜索功能实现
- [ ] 实现 CharacterFact 模型类
  - [ ] 知识碎片的增删改查
  - [ ] 向量嵌入生成和存储
  - [ ] 语义搜索功能
- [ ] 实现 CharacterRelation 模型类
  - [ ] 关系的创建和管理
  - [ ] 关系查询和遍历

#### 2.2 MCP 工具实现（4-5 天）
- [ ] 人物管理工具
  - [ ] `create_character` 工具
    - [ ] 输入验证
    - [ ] 数据库操作
    - [ ] 错误处理
  - [ ] `search_characters` 工具
    - [ ] 多种搜索模式（精确、模糊、标签）
    - [ ] 分页支持
    - [ ] 结果排序
- [ ] 知识碎片管理工具
  - [ ] `add_character_fact` 工具
    - [ ] 向量嵌入生成
    - [ ] 自动标签提取
    - [ ] 重复检测
  - [ ] `search_facts` 工具
    - [ ] 语义搜索实现
    - [ ] 相关性评分
    - [ ] 结果聚合

#### 2.3 向量嵌入服务（2-3 天）
- [ ] OpenAI Embeddings API 集成
  - [ ] API 客户端封装
  - [ ] 错误重试机制
  - [ ] 速率限制处理
- [ ] 向量相似度搜索
  - [ ] 余弦相似度计算
  - [ ] 批量向量查询优化
  - [ ] 搜索结果缓存

### 第三阶段：高级功能开发（预计 1.5 周）

#### 3.1 人物关系系统（3-4 天）
- [ ] 关系类型定义和管理
  - [ ] 预定义关系类型（家庭、朋友、敌对等）
  - [ ] 自定义关系类型支持
  - [ ] 关系强度和方向性
- [ ] 关系查询功能
  - [ ] 直接关系查询
  - [ ] 间接关系发现（2-3 度关系）
  - [ ] 关系路径分析
- [ ] 关系图谱数据准备
  - [ ] 图数据结构生成
  - [ ] 可视化数据格式输出

#### 3.2 AI 辅助功能（2-3 天）
- [ ] `generate_character_tags` 工具
  - [ ] 基于描述的标签生成
  - [ ] 标签去重和标准化
  - [ ] 置信度评分
- [ ] `analyze_character_relationships` 工具
  - [ ] 关系强度分析
  - [ ] 潜在关系推荐
  - [ ] 关系冲突检测

#### 3.3 性能优化（1-2 天）
- [ ] 数据库查询优化
  - [ ] 查询计划分析
  - [ ] 索引优化
  - [ ] 连接池配置
- [ ] 缓存机制实现
  - [ ] Redis 集成（可选）
  - [ ] 内存缓存策略
  - [ ] 缓存失效机制

### 第四阶段：测试与部署（预计 1 周）

#### 4.1 测试体系建设（3-4 天）
- [ ] 单元测试
  - [ ] 数据模型测试
  - [ ] 工具函数测试
  - [ ] 服务层测试
- [ ] 集成测试
  - [ ] MCP 工具端到端测试
  - [ ] 数据库集成测试
  - [ ] API 集成测试
- [ ] 性能测试
  - [ ] 向量搜索性能测试
  - [ ] 并发访问测试
  - [ ] 内存使用分析

#### 4.2 文档和部署（2-3 天）
- [ ] 用户文档编写
  - [ ] 安装指南
  - [ ] 使用教程
  - [ ] API 参考文档
- [ ] 部署准备
  - [ ] Docker 容器化
  - [ ] 环境配置文档
  - [ ] 部署脚本编写
- [ ] 发布准备
  - [ ] 版本标记
  - [ ] 发布说明
  - [ ] 示例数据准备

### 第五阶段：系统完善与优化（预计 0.5 周）

- [ ] 5.1 系统集成测试
- [ ] 5.2 性能调优和监控
- [ ] 5.3 文档完善和示例补充
- [ ] 5.4 最终验收和发布准备

---

## 九、时间表建议

**总预计开发时间：5.5 周**

### 详细时间分配

| 阶段 | 时间 | 主要任务 | 关键里程碑 |
|------|------|----------|------------|
| 第一阶段 | 1 周 | 基础搭建 | 项目框架完成，数据库可用 |
| 第二阶段 | 2 周 | 核心功能开发 | MCP 工具基本可用 |
| 第三阶段 | 1.5 周 | 高级功能开发 | AI 辅助功能完成 |
| 第四阶段 | 1 周 | 测试与部署 | 系统可部署使用 |
| 第五阶段 | 0.5 周 | 系统完善 | 最终发布版本 |

### 关键节点检查

#### 第 1 周末检查点
- [ ] 数据库连接正常
- [ ] 基础 MCP 服务器可启动
- [ ] 项目结构清晰

#### 第 3 周末检查点
- [ ] 人物和知识碎片的基本 CRUD 功能完成
- [ ] 向量搜索功能可用
- [ ] 基础 MCP 工具测试通过

#### 第 4.5 周末检查点
- [ ] 所有 MCP 工具功能完整
- [ ] AI 辅助功能可用
- [ ] 性能满足基本要求

#### 第 5.5 周末检查点
- [ ] 所有测试通过
- [ ] 文档完整
- [ ] 可部署使用

### 风险控制

#### 技术风险
- **向量数据库性能**：预留额外时间进行性能调优
- **AI API 限制**：准备备用方案（本地模型）
- **MCP 协议变更**：关注官方更新，及时适配

#### 时间风险
- **功能复杂度超预期**：优先实现核心功能，次要功能可后续迭代
- **测试时间不足**：采用 TDD 开发模式，边开发边测试
- **文档编写延期**：在开发过程中同步编写文档

---

## 十、后续可扩展方向

### 1. 高级 AI 功能

#### 1.1 智能分析功能
- **人物性格分析**：基于知识碎片分析人物性格特征
  - 使用心理学模型（如大五人格）
  - 生成性格雷达图
  - 提供性格发展建议
- **情节一致性检查**：检查人物行为是否符合设定
  - 行为模式学习
  - 异常行为检测
  - 一致性评分
- **对话风格生成**：为每个人物生成独特的对话模式
  - 语言风格分析
  - 词汇偏好学习
  - 对话模板生成

#### 1.2 创作辅助功能
- **情节生成器**：基于人物关系生成情节建议
- **冲突预测**：预测可能的人物冲突点
- **角色弧线分析**：分析人物发展轨迹

### 2. 可视化功能

#### 2.1 交互式图表
- **人物关系图谱**：
  - 力导向图布局
  - 关系强度可视化
  - 交互式节点操作
- **时间线视图**：
  - 人物发展历程
  - 重要事件标记
  - 时间轴缩放
- **知识地图**：
  - 主题聚类展示
  - 热力图显示
  - 钻取功能

#### 2.2 数据仪表板
- **统计概览**：人物数量、关系数量、知识碎片统计
- **活跃度分析**：最近更新的人物和关系
- **完整度评估**：人物设定完整度评分

### 3. 协作功能

#### 3.1 多用户系统
- **用户权限管理**：读者、编辑者、管理员角色
- **实时协作**：多人同时编辑
- **变更追踪**：记录所有修改历史

#### 3.2 版本控制
- **分支管理**：支持不同版本的人物设定
- **合并冲突解决**：智能合并建议
- **回滚功能**：快速恢复到历史版本

#### 3.3 社交功能
- **评论系统**：对人物设定进行讨论
- **标注功能**：重要信息高亮标记
- **通知系统**：变更通知和提醒

### 4. 集成与扩展

#### 4.1 外部工具集成
- **写作工具集成**：
  - Scrivener 插件
  - Notion 数据库同步
  - Google Docs 扩展
- **AI 工具集成**：
  - ChatGPT 插件
  - Claude 集成
  - 本地 LLM 支持

#### 4.2 数据导入导出
- **文本解析**：从现有作品自动提取人物信息
- **格式支持**：
  - JSON/YAML 导出
  - CSV 批量导入
  - Markdown 文档生成
- **API 接口**：提供 RESTful API 供第三方调用

### 5. 性能与扩展性

#### 5.1 性能优化
- **分布式部署**：支持多节点部署
- **缓存策略**：多级缓存优化
- **异步处理**：后台任务队列

#### 5.2 数据管理
- **数据备份**：自动备份和恢复
- **数据迁移**：版本升级数据迁移
- **数据清理**：过期数据自动清理

### 6. 商业化方向

#### 6.1 SaaS 服务
- **云端部署**：提供在线服务
- **订阅模式**：按功能和用量收费
- **企业版本**：团队协作增强功能

#### 6.2 生态建设
 - **插件市场**：第三方插件支持
 - **模板库**：预设人物模板
 - **社区建设**：用户交流平台

---

## 十一、技术选型详细说明

### 1. 核心技术栈

#### 后端框架
- **Python 3.11+**
  - 优势：简洁语法、丰富的 AI/ML 生态、与 MCP 协议兼容性好
  - 版本：Python 3.11+ 
  - 类型提示支持：mypy 静态类型检查

#### MCP 框架
- **mcp Python SDK**
  - 官方 Python SDK，稳定性和兼容性最佳
  - 支持工具注册和消息处理
  - 内置错误处理和验证

#### 数据库
- **PostgreSQL 15+**
  - 优势：成熟稳定、支持 JSON、强大的索引功能
  - **pgvector 扩展**：原生向量存储和检索
  - **pg_trgm 扩展**：模糊文本搜索

#### AI 服务
- **OpenAI API**
  - text-embedding-3-small：性价比高的嵌入模型
  - GPT-4：用于标签生成和关系分析
  - 备选：Azure OpenAI Service

### 2. 开发工具链

#### 代码质量
- **ruff**：快速的 Python 代码检查和格式化工具
- **black**：代码格式化
- **mypy**：静态类型检查
- **pre-commit**：Git hooks 管理

#### 测试框架
- **pytest**：单元测试和集成测试
- **httpx**：异步 HTTP 客户端测试
- **testcontainers**：数据库容器测试

#### 开发工具
- **uvicorn**：ASGI 服务器（如需要 web 接口）
- **poetry**：依赖管理和打包
- **watchdog**：文件变化监控和自动重启

### 3. 依赖管理

#### 核心依赖 (pyproject.toml)
```toml
[tool.poetry.dependencies]
python = "^3.11"
mcp = "^1.0.0"
psycopg2-binary = "^2.9.0"
openai = "^1.0.0"
pydantic = "^2.0.0"
python-dotenv = "^1.0.0"
numpy = "^1.24.0"
pgvector = "^0.2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
pytest-asyncio = "^0.21.0"
mypy = "^1.0.0"
ruff = "^0.1.0"
black = "^23.0.0"
pre-commit = "^3.0.0"
testcontainers = "^3.7.0"
httpx = "^0.25.0"
```

### 4. 架构模式

#### 分层架构
```
┌─────────────────┐
│   MCP Tools     │  # MCP 工具层
├─────────────────┤
│   Services      │  # 业务逻辑层
├─────────────────┤
│   Models        │  # 数据模型层
├─────────────────┤
│   Database      │  # 数据访问层
└─────────────────┘
```

#### 设计模式
- **Repository 模式**：数据访问抽象
- **Service 模式**：业务逻辑封装
- **Factory 模式**：对象创建管理
- **Strategy 模式**：搜索策略切换

### 5. 配置管理

#### 环境变量
```bash
# 数据库配置
DATABASE_URL=postgresql://user:pass@localhost:5432/writer_mcp
DATABASE_POOL_SIZE=10

# OpenAI 配置
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# 应用配置
PYTHON_ENV=development
LOG_LEVEL=info
CACHE_TTL=3600
```

#### 配置文件结构
```python
# src/writer_mcp/config.py
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str
    database_pool_size: int = 10
    
    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_embedding_model: str = "text-embedding-3-small"
    
    python_env: str = "development"
    log_level: str = "info"
    cache_ttl: int = 3600
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

#### 配置验证
- 使用 Pydantic 进行配置验证
- 启动时检查必需的环境变量
- 提供默认值和错误提示

---

## 十二、总结

### 项目价值

本项目旨在为小说创作者提供一个智能化的人物知识库管理系统，通过 MCP 协议与 AI 写作工具无缝集成。主要价值包括：

1. **提升创作效率**：快速检索人物信息，避免设定冲突
2. **增强创作质量**：AI 辅助分析，提供专业建议
3. **简化管理流程**：自动化标签生成，智能关系分析
4. **支持协作创作**：多人共享知识库，版本控制

### 技术亮点

1. **向量语义搜索**：基于 pgvector 的高性能语义检索
2. **AI 深度集成**：多种 AI 功能增强用户体验
3. **MCP 协议支持**：与主流 AI 工具无缝集成
4. **可扩展架构**：模块化设计，易于功能扩展

### 成功指标

#### 功能指标
- [ ] 支持 1000+ 人物管理
- [ ] 向量搜索响应时间 < 100ms
- [ ] AI 标签生成准确率 > 85%
- [ ] 系统可用性 > 99%

#### 用户体验指标
- [ ] 工具响应时间 < 2s
- [ ] 搜索结果相关性 > 90%
- [ ] 用户满意度 > 4.5/5

### 风险与挑战

#### 技术风险
- **向量数据库性能**：大规模数据下的查询优化
- **AI API 依赖**：服务稳定性和成本控制
- **数据一致性**：并发操作下的数据完整性

#### 应对策略
- **性能监控**：实时监控关键指标
- **降级方案**：AI 服务不可用时的备用策略
- **数据备份**：定期备份和恢复测试

### 下一步行动

1. **立即开始**：按照开发计划启动项目
2. **持续迭代**：根据用户反馈不断优化
3. **社区建设**：建立用户社区，收集需求
4. **生态扩展**：与更多写作工具集成

---

**文档版本**：v1.0  
**最后更新**：2024年12月  
**维护者**：项目开发团队  

> 本设计文档将随着项目进展持续更新，欢迎提出建议和改进意见。

