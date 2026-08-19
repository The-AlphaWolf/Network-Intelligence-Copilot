import json
from mcp.server.fastmcp import FastMCP
from backend.agents import get_cell_kpis, search_network_logs
from backend.rag import search_knowledge_base

mcp = FastMCP("NetworkIntelligenceMCP")

@mcp.tool()
def get_kpis(cell_id: str) -> str:
    """Get KPIs for a telecom cell."""
    return get_cell_kpis(cell_id)

@mcp.tool()
def search_logs(cell_id: str) -> str:
    """Search network logs for a specific cell."""
    return search_network_logs(cell_id)

@mcp.tool()
def search_kb(query: str) -> str:
    """Search the network telecom knowledge base."""
    results = search_knowledge_base(query)
    return json.dumps(results)

if __name__ == "__main__":
    mcp.run(transport='stdio')
