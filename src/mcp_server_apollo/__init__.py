"""Apollo MCP Server - Apollo 配置中心 MCP 服务."""

import argparse
import asyncio
import os

from . import server


def main():
    """包入口."""
    parser = argparse.ArgumentParser(description="Apollo MCP Server")
    parser.add_argument("--url", default=os.environ.get("APOLLO_URL"), help="Apollo Portal 地址，或 APOLLO_URL 环境变量")
    parser.add_argument("--token", default=os.environ.get("APOLLO_TOKEN"), help="Open API Token，或 APOLLO_TOKEN 环境变量")

    args = parser.parse_args()
    url = args.url
    token = args.token
    if not url or not token:
        parser.error("需要 --url 和 --token，或设置 APOLLO_URL 和 APOLLO_TOKEN 环境变量")
    asyncio.run(server.main(url, token))


__all__ = ["main", "server"]
