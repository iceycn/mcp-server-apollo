"""Apollo MCP Tools - 基于 Apollo 开放平台接口文档定义."""

from enum import Enum
from typing import Any

import mcp.types as types


class ApolloToolNames(str, Enum):
    """Apollo MCP Tool 名称枚举."""

    LIST_APPS = "list_apps"
    GET_APP_ENV_CLUSTERS = "get_app_env_clusters"
    GET_CLUSTER = "get_cluster"
    CREATE_CLUSTER = "create_cluster"
    LIST_NAMESPACES = "list_namespaces"
    GET_NAMESPACE = "get_namespace"
    CREATE_NAMESPACE = "create_namespace"
    GET_NAMESPACE_LOCK = "get_namespace_lock"
    LIST_ITEMS = "list_items"
    GET_ITEM = "get_item"
    CREATE_ITEM = "create_item"
    UPDATE_ITEM = "update_item"
    DELETE_ITEM = "delete_item"
    GET_LATEST_RELEASE = "get_latest_release"
    PUBLISH_RELEASE = "publish_release"
    ROLLBACK_RELEASE = "rollback_release"
    CREATE_APP = "create_app"


# 路径模板与参数定义（用于 server 构建请求）
TOOL_SPECS: dict[str, dict[str, Any]] = {
    ApolloToolNames.LIST_APPS: {
        "method": "GET",
        "path": "/openapi/v1/apps",
        "query": ["appIds"],
    },
    ApolloToolNames.GET_APP_ENV_CLUSTERS: {
        "method": "GET",
        "path": "/openapi/v1/apps/{appId}/envclusters",
    },
    ApolloToolNames.GET_CLUSTER: {
        "method": "GET",
        "path": "/openapi/v1/envs/{env}/apps/{appId}/clusters/{clusterName}",
    },
    ApolloToolNames.CREATE_CLUSTER: {
        "method": "POST",
        "path": "/openapi/v1/envs/{env}/apps/{appId}/clusters",
        "body": ["name", "appId", "dataChangeCreatedBy"],
    },
    ApolloToolNames.LIST_NAMESPACES: {
        "method": "GET",
        "path": "/openapi/v1/envs/{env}/apps/{appId}/clusters/{clusterName}/namespaces",
    },
    ApolloToolNames.GET_NAMESPACE: {
        "method": "GET",
        "path": "/openapi/v1/envs/{env}/apps/{appId}/clusters/{clusterName}/namespaces/{namespaceName}",
    },
    ApolloToolNames.CREATE_NAMESPACE: {
        "method": "POST",
        "path": "/openapi/v1/apps/{appId}/appnamespaces",
        "body": ["name", "appId", "format", "isPublic", "dataChangeCreatedBy", "comment"],
    },
    ApolloToolNames.GET_NAMESPACE_LOCK: {
        "method": "GET",
        "path": "/openapi/v1/envs/{env}/apps/{appId}/clusters/{clusterName}/namespaces/{namespaceName}/lock",
    },
    ApolloToolNames.LIST_ITEMS: {
        "method": "GET",
        "path": "/openapi/v1/envs/{env}/apps/{appId}/clusters/{clusterName}/namespaces/{namespaceName}/items",
        "query": ["page", "size"],
    },
    ApolloToolNames.GET_ITEM: {
        "method": "GET",
        "path": "/openapi/v1/envs/{env}/apps/{appId}/clusters/{clusterName}/namespaces/{namespaceName}/items/{key}",
    },
    ApolloToolNames.CREATE_ITEM: {
        "method": "POST",
        "path": "/openapi/v1/envs/{env}/apps/{appId}/clusters/{clusterName}/namespaces/{namespaceName}/items",
        "body": ["key", "value", "dataChangeCreatedBy", "comment"],
    },
    ApolloToolNames.UPDATE_ITEM: {
        "method": "PUT",
        "path": "/openapi/v1/envs/{env}/apps/{appId}/clusters/{clusterName}/namespaces/{namespaceName}/items/{key}",
        "query": ["createIfNotExists"],
        "body": ["key", "value", "dataChangeLastModifiedBy", "comment", "dataChangeCreatedBy"],
    },
    ApolloToolNames.DELETE_ITEM: {
        "method": "DELETE",
        "path": "/openapi/v1/envs/{env}/apps/{appId}/clusters/{clusterName}/namespaces/{namespaceName}/items/{key}",
        "query": ["operator"],
    },
    ApolloToolNames.GET_LATEST_RELEASE: {
        "method": "GET",
        "path": "/openapi/v1/envs/{env}/apps/{appId}/clusters/{clusterName}/namespaces/{namespaceName}/releases/latest",
    },
    ApolloToolNames.PUBLISH_RELEASE: {
        "method": "POST",
        "path": "/openapi/v1/envs/{env}/apps/{appId}/clusters/{clusterName}/namespaces/{namespaceName}/releases",
        "body": ["releaseTitle", "releasedBy", "releaseComment"],
    },
    ApolloToolNames.ROLLBACK_RELEASE: {
        "method": "PUT",
        "path": "/openapi/v1/envs/{env}/releases/{releaseId}/rollback",
        "query": ["operator"],
    },
    ApolloToolNames.CREATE_APP: {
        "method": "POST",
        "path": "/openapi/v1/apps/",
        "body": ["assignAppRoleToSelf", "admins", "app"],
    },
}


def get_all_tools() -> list[types.Tool]:
    """返回所有 Apollo MCP Tools."""
    return [
        types.Tool(
            name=ApolloToolNames.LIST_APPS,
            description="获取应用列表。可选 appIds 参数（逗号分隔）过滤，为空则返回所有应用。",
            inputSchema={
                "type": "object",
                "properties": {
                    "appIds": {"type": "string", "description": "appId 列表，逗号分隔，可选"},
                },
            },
        ),
        types.Tool(
            name=ApolloToolNames.GET_APP_ENV_CLUSTERS,
            description="获取应用的环境与集群信息。",
            inputSchema={
                "type": "object",
                "properties": {"appId": {"type": "string", "description": "应用 ID"}},
                "required": ["appId"],
            },
        ),
        types.Tool(
            name=ApolloToolNames.GET_CLUSTER,
            description="获取集群详情。",
            inputSchema={
                "type": "object",
                "properties": {
                    "appId": {"type": "string", "description": "应用 ID"},
                    "env": {"type": "string", "description": "环境，如 FAT、UAT、PRO"},
                    "clusterName": {"type": "string", "description": "集群名，一般 default"},
                },
                "required": ["appId", "env", "clusterName"],
            },
        ),
        types.Tool(
            name=ApolloToolNames.CREATE_CLUSTER,
            description="创建集群。需要授予第三方 APP 对目标 APP 的管理权限。",
            inputSchema={
                "type": "object",
                "properties": {
                    "appId": {"type": "string"},
                    "env": {"type": "string"},
                    "name": {"type": "string", "description": "集群名"},
                    "dataChangeCreatedBy": {"type": "string", "description": "创建人，域账号"},
                },
                "required": ["appId", "env", "name", "dataChangeCreatedBy"],
            },
        ),
        types.Tool(
            name=ApolloToolNames.LIST_NAMESPACES,
            description="获取集群下所有 Namespace 及配置项。",
            inputSchema={
                "type": "object",
                "properties": {
                    "appId": {"type": "string"},
                    "env": {"type": "string"},
                    "clusterName": {"type": "string", "description": "默认 default"},
                },
                "required": ["appId", "env", "clusterName"],
            },
        ),
        types.Tool(
            name=ApolloToolNames.GET_NAMESPACE,
            description="获取指定 Namespace 详情。",
            inputSchema={
                "type": "object",
                "properties": {
                    "appId": {"type": "string"},
                    "env": {"type": "string"},
                    "clusterName": {"type": "string"},
                    "namespaceName": {"type": "string", "description": "如 application、FX.apollo；非 properties 需带后缀如 sample.yml"},
                },
                "required": ["appId", "env", "clusterName", "namespaceName"],
            },
        ),
        types.Tool(
            name=ApolloToolNames.CREATE_NAMESPACE,
            description="创建 Namespace。format 仅支持 properties、xml、json、yml、yaml。",
            inputSchema={
                "type": "object",
                "properties": {
                    "appId": {"type": "string"},
                    "name": {"type": "string"},
                    "format": {"type": "string", "enum": ["properties", "xml", "json", "yml", "yaml"]},
                    "isPublic": {"type": "boolean"},
                    "dataChangeCreatedBy": {"type": "string"},
                    "comment": {"type": "string", "description": "可选"},
                },
                "required": ["appId", "name", "format", "isPublic", "dataChangeCreatedBy"],
            },
        ),
        types.Tool(
            name=ApolloToolNames.GET_NAMESPACE_LOCK,
            description="获取 Namespace 当前编辑人/锁状态。PRO 环境有编辑锁定规则。",
            inputSchema={
                "type": "object",
                "properties": {
                    "appId": {"type": "string"},
                    "env": {"type": "string"},
                    "clusterName": {"type": "string"},
                    "namespaceName": {"type": "string"},
                },
                "required": ["appId", "env", "clusterName", "namespaceName"],
            },
        ),
        types.Tool(
            name=ApolloToolNames.LIST_ITEMS,
            description="分页获取 Namespace 下的配置项。需 Apollo 版本>=2.1.0。",
            inputSchema={
                "type": "object",
                "properties": {
                    "appId": {"type": "string"},
                    "env": {"type": "string"},
                    "clusterName": {"type": "string"},
                    "namespaceName": {"type": "string"},
                    "page": {"type": "integer", "description": "页码，默认 0"},
                    "size": {"type": "integer", "description": "页大小，默认 50"},
                },
                "required": ["appId", "env", "clusterName", "namespaceName"],
            },
        ),
        types.Tool(
            name=ApolloToolNames.GET_ITEM,
            description="获取单个配置项。",
            inputSchema={
                "type": "object",
                "properties": {
                    "appId": {"type": "string"},
                    "env": {"type": "string"},
                    "clusterName": {"type": "string"},
                    "namespaceName": {"type": "string"},
                    "key": {"type": "string", "description": "配置 key；非 properties 格式固定为 content"},
                },
                "required": ["appId", "env", "clusterName", "namespaceName", "key"],
            },
        ),
        types.Tool(
            name=ApolloToolNames.CREATE_ITEM,
            description="新增配置项。key 长度不超过 128 字符，value 不超过 20000 字符。",
            inputSchema={
                "type": "object",
                "properties": {
                    "appId": {"type": "string"},
                    "env": {"type": "string"},
                    "clusterName": {"type": "string"},
                    "namespaceName": {"type": "string"},
                    "key": {"type": "string"},
                    "value": {"type": "string"},
                    "dataChangeCreatedBy": {"type": "string"},
                    "comment": {"type": "string", "description": "可选"},
                },
                "required": ["appId", "env", "clusterName", "namespaceName", "key", "value", "dataChangeCreatedBy"],
            },
        ),
        types.Tool(
            name=ApolloToolNames.UPDATE_ITEM,
            description="修改配置项。createIfNotExists 为 true 时不存在则创建，此时 dataChangeCreatedBy 必填。",
            inputSchema={
                "type": "object",
                "properties": {
                    "appId": {"type": "string"},
                    "env": {"type": "string"},
                    "clusterName": {"type": "string"},
                    "namespaceName": {"type": "string"},
                    "key": {"type": "string"},
                    "value": {"type": "string"},
                    "dataChangeLastModifiedBy": {"type": "string"},
                    "createIfNotExists": {"type": "boolean", "description": "可选"},
                    "dataChangeCreatedBy": {"type": "string", "description": "createIfNotExists 时必填"},
                    "comment": {"type": "string"},
                },
                "required": ["appId", "env", "clusterName", "namespaceName", "key", "value", "dataChangeLastModifiedBy"],
            },
        ),
        types.Tool(
            name=ApolloToolNames.DELETE_ITEM,
            description="删除配置项。",
            inputSchema={
                "type": "object",
                "properties": {
                    "appId": {"type": "string"},
                    "env": {"type": "string"},
                    "clusterName": {"type": "string"},
                    "namespaceName": {"type": "string"},
                    "key": {"type": "string"},
                    "operator": {"type": "string", "description": "删除操作者，域账号"},
                },
                "required": ["appId", "env", "clusterName", "namespaceName", "key", "operator"],
            },
        ),
        types.Tool(
            name=ApolloToolNames.GET_LATEST_RELEASE,
            description="获取 Namespace 当前生效的已发布配置。",
            inputSchema={
                "type": "object",
                "properties": {
                    "appId": {"type": "string"},
                    "env": {"type": "string"},
                    "clusterName": {"type": "string"},
                    "namespaceName": {"type": "string"},
                },
                "required": ["appId", "env", "clusterName", "namespaceName"],
            },
        ),
        types.Tool(
            name=ApolloToolNames.PUBLISH_RELEASE,
            description="发布配置。releaseTitle 不超过 64 字符。PRO 环境可能要求发布人与编辑人不同。",
            inputSchema={
                "type": "object",
                "properties": {
                    "appId": {"type": "string"},
                    "env": {"type": "string"},
                    "clusterName": {"type": "string"},
                    "namespaceName": {"type": "string"},
                    "releaseTitle": {"type": "string"},
                    "releasedBy": {"type": "string"},
                    "releaseComment": {"type": "string", "description": "可选"},
                },
                "required": ["appId", "env", "clusterName", "namespaceName", "releaseTitle", "releasedBy"],
            },
        ),
        types.Tool(
            name=ApolloToolNames.ROLLBACK_RELEASE,
            description="回滚到指定版本。releaseId 为发布记录 ID，从 get_latest_release 返回的 id 字段获取。",
            inputSchema={
                "type": "object",
                "properties": {
                    "env": {"type": "string"},
                    "releaseId": {"type": "integer", "description": "发布记录 ID，从 get_latest_release 返回的 id 字段获取"},
                    "operator": {"type": "string", "description": "操作者，域账号"},
                },
                "required": ["env", "releaseId", "operator"],
            },
        ),
        types.Tool(
            name=ApolloToolNames.CREATE_APP,
            description="创建 App 并授权。需在创建第三方应用时勾选允许创建 app。",
            inputSchema={
                "type": "object",
                "properties": {
                    "assignAppRoleToSelf": {"type": "boolean", "description": "是否授予自己管理权限"},
                    "admins": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "授予管理权限的用户列表，可选",
                    },
                    "app": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "appId": {"type": "string"},
                            "orgId": {"type": "string"},
                            "orgName": {"type": "string"},
                            "ownerName": {"type": "string"},
                            "ownerEmail": {"type": "string"},
                        },
                        "required": ["name", "appId", "orgId", "orgName", "ownerName", "ownerEmail"],
                    },
                },
                "required": ["assignAppRoleToSelf", "app"],
            },
        ),
    ]
