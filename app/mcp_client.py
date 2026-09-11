"""FastMCP 4 client helpers."""
from typing import Any
from fastmcp import Client

def unwrap_tool_result(result: Any) -> Any:
    """Extract structured FastMCP 4 tool data without assuming `.data`."""
    structured=getattr(result,'structured_content',None)
    if structured is not None:
        if isinstance(structured,dict) and 'result' in structured: return structured['result']
        return structured
    data=getattr(result,'data',None)
    if data is not None: return data
    content=getattr(result,'content',None)
    if content:
        item=content[0]
        text=getattr(item,'text',item)
        return text
    return result

async def read_capabilities(server):
    async with Client(server) as client:
        return unwrap_tool_result(await client.call_tool('capabilities', {}))
