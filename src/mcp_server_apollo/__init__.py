"""Apollo MCP Server - Apollo 配置中心 MCP 服务."""

import argparse
import asyncio

from . import server


def main():
    """包入口."""
    parser = argparse.ArgumentParser(description="Apollo MCP Server")
    parser.add_argument("--url", required=True, help="Apollo Portal 地址，如 http://localhost:8070")
    parser.add_argument("--token", required=True, help="Open API Token")

    args = parser.parse_args()
    asyncio.run(server.main(args.url, args.token))


__all__ = ["main", "server"]
