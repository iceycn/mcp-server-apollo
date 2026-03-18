# Apollo MCP Server

Apollo 配置中心的 MCP (Model Context Protocol) 服务，使大语言模型能够通过配置的 Apollo 地址和 Token 对 Apollo 进行查询和操作。支持 **Cursor**、**Trae**、Claude Desktop 等 MCP 客户端。

[![PyPI version](https://badge.fury.io/py/apollo-mcp-server.svg)](https://pypi.org/project/apollo-mcp-server/)

> **v1.0.0 说明**：本期仅完成 Apollo 的**读取**能力，写入（新增/修改/删除配置、发布、回滚等）已实现接口但**暂未测试**，且需 Token 在 Portal 中具备相应赋权。

## 功能

基于 [Apollo 开放平台接口文档](https://www.apolloconfig.com/#/zh/portal/apollo-open-api-platform) 实现以下能力：

- **应用与集群**：list_apps、get_app_env_clusters、get_cluster、create_cluster
- **命名空间**：list_namespaces、get_namespace、create_namespace、get_namespace_lock
- **配置项**：list_items、get_item、create_item、update_item、delete_item
- **发布与回滚**：get_latest_release、publish_release、rollback_release
- **应用创建**：create_app

## 前提条件

1. Apollo Portal 已部署并可访问
2. 在 Portal 的 `http://{portal_address}/open/add-consumer.html` 创建第三方应用并获取 Token
3. 在 `http://{portal_address}/open/manage.html` 为 Token 绑定可操作的 Namespace

具体可参考官方指引: https://www.apolloconfig.com/#/zh/portal/apollo-open-api-platform

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install apollo-mcp-server
```

或使用 uvx 无需安装即可运行：

```bash
uvx apollo-mcp-server --url http://your-apollo:8070 --token your_token
```

### 开发模式（从源码安装）

```bash
pip install -e .
# 或
uv pip install -e .
```

## 配置

### 使用方式

```bash
apollo-mcp-server --url http://your-apollo-portal:8070 --token your_open_api_token
```

> `--url` 为 Apollo Portal 根地址（不含 `/openapi/v1/` 后缀），如 `http://localhost:8070`。

或

```bash
python -m mcp_server_apollo --url http://your-apollo-portal:8070 --token your_open_api_token
```

### Cursor / Trae / Claude Desktop 配置

在 `~/.cursor/mcp.json`（Cursor）、Trae 或 `claude_desktop_config.json`（Claude）中添加：

```json
{
  "mcpServers": {
    "apollo": {
      "command": "uvx",
      "args": [
        "apollo-mcp-server",
        "--url",
        "http://your-apollo-portal:8070",
        "--token",
        "your_open_api_token"
      ]
    }
  }
}
```

也可通过环境变量配置（需 apollo-mcp-server >= 1.0.0）：

```json
{
  "mcpServers": {
    "apollo": {
      "command": "uvx",
      "args": ["apollo-mcp-server"],
      "env": {
        "APOLLO_URL": "http://your-apollo-portal:8070",
        "APOLLO_TOKEN": "your_open_api_token"
      }
    }
  }
}
```

## 开发

```bash
# 安装依赖
pip install -e .

# 本地运行（无需安装，从项目目录）
PYTHONPATH=src python -m mcp_server_apollo --url http://localhost:8070 --token your_token

# 或安装后直接运行
apollo-mcp-server --url http://localhost:8070 --token your_token
```

## 许可证

Apache License 2.0
