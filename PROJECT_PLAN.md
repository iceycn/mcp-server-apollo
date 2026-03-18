# Apollo MCP Server 项目计划

## 一、项目概述

参考 [nacos-mcp-server](https://github.com/nacos-group/nacos-mcp-server) 架构，为 Apollo 配置中心搭建 MCP (Model Context Protocol) 服务，使大语言模型能够通过配置的 Apollo 地址和 Token 对 Apollo 进行查询和操作。

## 二、参考项目分析

### 2.1 nacos-mcp-server 架构要点

| 组件 | 说明 |
|------|------|
| **技术栈** | Python 3.13+、httpx、mcp[cli] |
| **入口参数** | `--host`、`--port`、`--access_token` |
| **认证方式** | HTTP Header `AccessToken` |
| **项目结构** | `src/mcp_server_nacos/` 含 `__init__.py`、`server.py`、`nacos_tools.py` |
| **工具定义** | 继承 `types.Tool`，定义 `name`、`description`、`inputSchema`、`url` |
| **传输方式** | stdio（与 Claude Desktop 等 MCP 客户端通信） |

### 2.2 Apollo Open API 要点（摘自官方文档）

- **文档**：[Apollo 开放平台接口文档](https://www.apolloconfig.com/#/zh/portal/apollo-open-api-platform)
- **Base URL**：`http://{portal_address}/openapi/v1/`
- **认证**：HTTP Header `Authorization` = Token 值
- **Content-Type**：`application/json;charset=UTF-8`
- **Token 获取**：在 Portal 的 `http://{portal_address}/open/add-consumer.html` 创建第三方应用后生成；需在 `http://{portal_address}/open/manage.html` 给 token 绑定可操作的 Namespace 才能管理配置

### 2.3 Apollo Open API 接口详解（基于官方文档解读）

以下内容依据 [Apollo 开放平台接口文档](https://www.apolloconfig.com/#/zh/portal/apollo-open-api-platform) 整理。

#### 2.3.1 URL 路径参数说明

| 参数名 | 说明 |
|--------|------|
| env | 所管理的配置环境（如 FAT、UAT、PRO） |
| appId | 所管理的配置 AppId |
| clusterName | 所管理的配置集群名，一般传 `default` |
| namespaceName | Namespace 名称；非 properties 格式需带后缀，如 `sample.yml` |

#### 2.3.2 接口清单与请求规范

| 序号 | 接口名称 | Method | URL 路径 | 说明 |
|------|----------|--------|-----------|------|
| 1 | 获取 App 环境集群信息 | GET | `/openapi/v1/apps/{appId}/envclusters` | 无请求参数 |
| 2 | 获取 App 信息 | GET | `/openapi/v1/apps` | Query: appIds（可选，逗号分隔） |
| 3 | 获取集群详情 | GET | `/openapi/v1/envs/{env}/apps/{appId}/clusters/{clusterName}` | 无请求参数 |
| 4 | 创建集群 | POST | `/openapi/v1/envs/{env}/apps/{appId}/clusters` | Body: name, appId, dataChangeCreatedBy |
| 5 | 获取集群下所有 Namespace | GET | `/openapi/v1/envs/{env}/apps/{appId}/clusters/{clusterName}/namespaces` | 无请求参数 |
| 6 | 获取某个 Namespace | GET | `/openapi/v1/envs/{env}/apps/{appId}/clusters/{clusterName}/namespaces/{namespaceName}` | 无请求参数 |
| 7 | 创建 Namespace | POST | `/openapi/v1/apps/{appId}/appnamespaces` | Body: name, appId, format, isPublic, dataChangeCreatedBy, comment(可选) |
| 8 | 获取 Namespace 当前编辑人/锁 | GET | `.../namespaces/{namespaceName}/lock` | 无请求参数 |
| 9 | 读取配置项 | GET | `.../namespaces/{namespaceName}/items/{key}` | 无请求参数 |
| 10 | 新增配置项 | POST | `.../namespaces/{namespaceName}/items` | Body: key, value, dataChangeCreatedBy, comment(可选) |
| 11 | 修改配置项 | PUT | `.../namespaces/{namespaceName}/items/{key}` | Query: createIfNotExists(可选)；Body: key, value, dataChangeLastModifiedBy, comment(可选), dataChangeCreatedBy(createIfNotExists 时必选) |
| 12 | 删除配置项 | DELETE | `.../namespaces/{namespaceName}/items/{key}` | Query: operator（必填） |
| 13 | 发布配置 | POST | `.../namespaces/{namespaceName}/releases` | Body: releaseTitle, releasedBy, releaseComment(可选) |
| 14 | 获取当前生效发布 | GET | `.../namespaces/{namespaceName}/releases/latest` | 无请求参数 |
| 15 | 回滚发布 | PUT | `/openapi/v1/envs/{env}/releases/{releaseId}/rollback` | Query: operator（必填） |
| 16 | 分页获取配置项 | GET | `.../namespaces/{namespaceName}/items` | Query: page(默认0), size(默认50)，版本>=2.1.0 |
| 17 | 创建 App | POST | `/openapi/v1/apps/` | Body: assignAppRoleToSelf, admins(可选), app；需勾选允许创建 app |

#### 2.3.3 关键参数约束（官方文档）

- **配置项 key**：长度不超过 128 字符；非 properties 格式固定为 `content`
- **配置项 value**：长度不超过 20000 字符
- **comment**：长度不超过 256 字符
- **releaseTitle**：长度不超过 64 字符
- **releaseComment**：长度不超过 256 字符
- **Namespace format**：仅支持 `properties`、`xml`、`json`、`yml`、`yaml`
- **命名规则**：properties 文件 `name = ${部门}.${传入name}`；非 properties 为 `name = ${部门}.${传入name}.${format}`

#### 2.3.4 错误码说明（官方文档）

| 状态码 | 说明 |
|--------|------|
| 400 | 参数错误，如操作人不存在、namespace 不存在等 |
| 401 | token 非法或已过期 |
| 403 | 资源未授权，如尝试管理未授权应用的配置 |
| 404 | 资源不存在，URL 或参数错误 |
| 405 | 请求方法错误 |
| 500 | 服务端内部错误 |

## 三、Apollo MCP Server 设计方案

### 3.1 配置参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `--url` | string | 是 | Apollo Portal 地址，如 `http://localhost:8070` |
| `--token` | string | 是 | Open API Token（在 Portal 创建第三方应用后获得） |

> 说明：采用 `--url` + `--token` 作为配置参数。

### 3.2 拟实现的 MCP Tools 列表（与 2.3 接口一一对应）

#### 3.2.1 应用与集群

| Tool 名称 | 说明 | 对应接口 | 输入参数 |
|-----------|------|----------|----------|
| `list_apps` | 获取应用列表 | 3.2.2 获取 App 信息 | appIds（可选，逗号分隔） |
| `get_app_env_clusters` | 获取应用的环境与集群信息 | 3.2.1 | appId |
| `get_cluster` | 获取集群详情 | 3.2.3 | appId, env, clusterName |
| `create_cluster` | 创建集群 | 3.2.4 | appId, env, name, dataChangeCreatedBy |

#### 3.2.2 命名空间

| Tool 名称 | 说明 | 对应接口 | 输入参数 |
|-----------|------|----------|----------|
| `list_namespaces` | 获取集群下所有 Namespace 及配置项 | 3.2.5 | appId, env, clusterName |
| `get_namespace` | 获取指定 Namespace 详情 | 3.2.6 | appId, env, clusterName, namespaceName |
| `create_namespace` | 创建 Namespace | 3.2.7 | appId, name, format, isPublic, dataChangeCreatedBy, comment(可选) |
| `get_namespace_lock` | 获取 Namespace 当前编辑人/锁状态 | 3.2.8 | appId, env, clusterName, namespaceName |

#### 3.2.3 配置项

| Tool 名称 | 说明 | 对应接口 | 输入参数 |
|-----------|------|----------|----------|
| `list_items` | 分页获取配置项 | 3.2.16 | appId, env, clusterName, namespaceName, page(默认0), size(默认50) |
| `get_item` | 获取单个配置项 | 3.2.9 | appId, env, clusterName, namespaceName, key |
| `create_item` | 新增配置项 | 3.2.10 | appId, env, clusterName, namespaceName, key, value, dataChangeCreatedBy, comment(可选) |
| `update_item` | 修改配置项 | 3.2.11 | appId, env, clusterName, namespaceName, key, value, dataChangeLastModifiedBy, createIfNotExists(可选), dataChangeCreatedBy(可选) |
| `delete_item` | 删除配置项 | 3.2.12 | appId, env, clusterName, namespaceName, key, operator |

#### 3.2.4 发布与回滚

| Tool 名称 | 说明 | 对应接口 | 输入参数 |
|-----------|------|----------|----------|
| `get_latest_release` | 获取当前生效的发布 | 3.2.14 | appId, env, clusterName, namespaceName |
| `publish_release` | 发布配置 | 3.2.13 | appId, env, clusterName, namespaceName, releaseTitle, releasedBy, releaseComment(可选) |
| `rollback_release` | 回滚到指定版本 | 3.2.15 | env, releaseId, operator |

#### 3.2.5 应用创建（可选）

| Tool 名称 | 说明 | 对应接口 | 输入参数 |
|-----------|------|----------|----------|
| `create_app` | 创建 App 并授权 | 3.2.17 | assignAppRoleToSelf, app(name, appId, orgId, orgName, ownerName, ownerEmail), admins(可选) |

### 3.3 公共参数约定

**路径参数**（多数 Tool 需要）：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `appId` | 应用 ID | 必填 |
| `env` | 环境（FAT/UAT/PRO 等） | 必填 |
| `clusterName` | 集群名 | 通常为 `default` |
| `namespaceName` | 命名空间名，如 `application`、`FX.apollo`；非 properties 需带后缀如 `sample.yml` | 必填 |

**操作人参数**（官方文档要求为域账号/SSO User ID）：

| 参数 | 用途 |
|------|------|
| `dataChangeCreatedBy` | 创建人（新增配置、创建 Namespace/集群等） |
| `dataChangeLastModifiedBy` | 修改人（修改配置） |
| `releasedBy` | 发布人（发布配置） |
| `operator` | 操作人（删除配置、回滚） |

### 3.4 项目目录结构

```
apollo-mcp/
├── pyproject.toml              # 项目配置，依赖 mcp[cli]、httpx
├── README.md
├── PROJECT_PLAN.md             # 本计划文档
├── src/
│   └── mcp_server_apollo/
│       ├── __init__.py         # 入口，解析 --url、--token
│       ├── __main__.py         # python -m mcp_server_apollo
│       ├── server.py           # MCP Server 主逻辑
│       └── apollo_tools.py     # 各 Tool 定义
└── .python-version             # 3.11
```

### 3.5 依赖与构建

```toml
# pyproject.toml 参考
[project]
name = "apollo-mcp-server"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.28.1",
    "mcp[cli]>=1.6.0",
]

[project.scripts]
apollo-mcp-server = "mcp_server_apollo:main"
```

### 3.6 Claude Desktop 配置示例

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

若使用 pip 安装：

```json
{
  "mcpServers": {
    "apollo": {
      "command": "python",
      "args": [
        "-m",
        "mcp_server_apollo",
        "--url",
        "http://your-apollo-portal:8070",
        "--token",
        "your_open_api_token"
      ]
    }
  }
}
```

## 四、实现阶段建议

> 实现时所有接口定义、参数、路径均以 [Apollo 开放平台接口文档](https://www.apolloconfig.com/#/zh/portal/apollo-open-api-platform) 为准。

### Phase 1：核心只读能力（优先）
- `list_apps`
- `get_app_env_clusters`
- `list_namespaces` / `get_namespace`
- `list_items` / `get_item`
- `get_latest_release`

### Phase 2：配置写入与发布
- `create_item` / `update_item` / `delete_item`
- `publish_release` / `rollback_release`

### Phase 3：扩展能力
- `create_cluster` / `create_namespace` / `create_app`
- `get_namespace_lock` / `get_cluster` 等辅助接口

## 五、与 nacos-mcp-server 的差异

| 维度 | Nacos | Apollo |
|------|-------|--------|
| 连接配置 | host + port + token | `--url` + `--token` |
| 认证 Header | AccessToken | Authorization |
| 核心概念 | namespace / service / config | app / env / cluster / namespace / item |
| 环境 | 无显式 env | 有 env（FAT/UAT/PRO） |
| 发布流程 | 无独立发布 | 编辑 → 发布 → 可回滚 |

## 六、实现完成情况（已核对）

| 检查项 | 状态 |
|--------|------|
| 17 个 Tool 全部实现 | ✓ |
| API 路径与文档 2.3.2 一致 | ✓ |
| 认证 Header：Authorization | ✓ |
| Content-Type：application/json;charset=UTF-8 | ✓ |
| 配置参数 --url、--token | ✓ |
| 错误码 400/401/403/404 友好提示 | ✓ |
| list_items 版本>=2.1.0 说明 | ✓ |
| rollback_release 的 releaseId 来源说明 | ✓ |

## 七、待您确认事项（历史记录）

1. **配置参数**：已确认采用 `--url` + `--token`。
2. **Tool 范围**：已实现全部 17 个 Tool。
3. **命名空间格式**：已在 get_namespace、create_namespace 等 Tool 的 description 中说明。
4. **参考代码**：已从零在 `apollo-mcp` 下新建实现。
