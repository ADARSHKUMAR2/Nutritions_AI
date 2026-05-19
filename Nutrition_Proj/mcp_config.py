import os
from agents.mcp import MCPServerStreamableHttp

def get_exa_search_mcp() -> MCPServerStreamableHttp:
    """Initializes and configures the EXA Search MCP."""
    return MCPServerStreamableHttp(
        name="Exa Search MCP",
        params={
            "url": f"https://mcp.exa.ai/mcp?{os.environ.get('EXA_API_KEY')}",
            "timeout": 90,
        },
        client_session_timeout_seconds=90,
        cache_tools_list=True,
        max_retry_attempts=1,
    )