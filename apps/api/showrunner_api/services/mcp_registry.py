from typing import Any, Protocol


class MCPRegistry(Protocol):
    async def call(self, connector_name: str, method: str, params: dict[str, Any]) -> Any:
        """Call a registered MCP connector."""


class EmptyMCPRegistry:
    async def call(self, connector_name: str, method: str, params: dict[str, Any]) -> Any:
        raise NotImplementedError("No MCP connectors are registered in Sprint 001")
