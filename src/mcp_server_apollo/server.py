"""Apollo MCP Server - 主逻辑与 Apollo Open API 客户端."""

import json
import logging
from typing import Any

import httpx
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio

from . import apollo_tools

logger = logging.getLogger("mcp_server_apollo")
logger.setLevel(logging.INFO)

USER_AGENT = "Apollo-MCP-Server:v0.1.0"


class Result:
    """API 请求结果."""

    def __init__(self, code: int, message: str, data: Any):
        self.code = code
        self.message = message
        self.data = data

    def is_success(self) -> bool:
        return self.code == httpx.codes.OK


class ApolloClient:
    """Apollo Open API 客户端."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _headers(self) -> dict[str, str]:
        return {
            "User-Agent": USER_AGENT,
            "Authorization": self.token,
            "Content-Type": "application/json;charset=UTF-8",
        }

    def _build_path(self, path_template: str, args: dict[str, Any]) -> str:
        """用 args 填充路径中的 {key}."""
        result = path_template
        for k, v in args.items():
            if v is not None and "{" + k + "}" in result:
                result = result.replace("{" + k + "}", str(v))
        return result

    def _request(
        self,
        name: str,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> str:
        """发起 HTTP 请求."""
        url = self.base_url + path
        if params:
            # 过滤 None 值
            params = {k: v for k, v in params.items() if v is not None}

        logger.debug("%s %s params=%s body=%s", method, url, params, json_body)

        with httpx.Client(timeout=30.0) as client:
            try:
                if method == "GET":
                    response = client.get(url, headers=self._headers(), params=params)
                elif method == "POST":
                    response = client.post(url, headers=self._headers(), params=params, json=json_body or {})
                elif method == "PUT":
                    response = client.put(url, headers=self._headers(), params=params, json=json_body or {})
                elif method == "DELETE":
                    response = client.delete(url, headers=self._headers(), params=params)
                else:
                    return f"Unsupported method: {method}"

                if response.status_code == httpx.codes.OK:
                    try:
                        return json.dumps(response.json(), ensure_ascii=False, indent=2)
                    except Exception:
                        return response.text

                if response.status_code in (httpx.codes.UNAUTHORIZED, httpx.codes.FORBIDDEN):
                    return f"认证失败(401/403): token 非法或已过期，或资源未授权。请检查 token 及 Portal 赋权。"
                if response.status_code == httpx.codes.BAD_REQUEST:
                    return f"参数错误(400): {response.text}"
                if response.status_code == httpx.codes.NOT_FOUND:
                    return f"资源不存在(404): {response.text}"
                return f"请求失败({response.status_code}): {response.text}"

            except httpx.HTTPError as e:
                return f"网络错误: {e}"
            except Exception as e:
                return f"未知错误: {e}"

    def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """根据 tool 名称和参数调用 Apollo API."""
        if name not in apollo_tools.TOOL_SPECS:
            return f"未知工具: {name}"

        spec = apollo_tools.TOOL_SPECS[name]
        method = spec["method"]
        path_template = spec["path"]

        # 路径参数：从 path 中提取 {key}，用 args 填充
        path_args = {}
        for k, v in arguments.items():
            if "{" + k + "}" in path_template:
                path_args[k] = v

        path = self._build_path(path_template, arguments)

        # Query 参数
        query_keys = spec.get("query", [])
        query_params = {k: arguments.get(k) for k in query_keys if k in arguments}

        # Body 参数（POST/PUT）
        json_body = None
        if method in ("POST", "PUT") and "body" in spec:
            body_keys = spec["body"]
            body = {}
            for k in body_keys:
                if k in arguments and arguments[k] is not None:
                    body[k] = arguments[k]
            if body:
                json_body = body

        return self._request(name, method, path, params=query_params or None, json_body=json_body)


async def main(base_url: str, token: str):
    """MCP Server 入口."""
    logger.info("Starting Apollo MCP Server, url=%s", base_url)
    client = ApolloClient(base_url, token)
    server = Server("mcp-apollo")

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return apollo_tools.get_all_tools()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        try:
            result = client.call_tool(name, arguments or {})
            return [types.TextContent(type="text", text=result)]
        except Exception as e:
            logger.exception("Tool %s failed", name)
            return [types.TextContent(type="text", text=str(e))]

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="apollo",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
