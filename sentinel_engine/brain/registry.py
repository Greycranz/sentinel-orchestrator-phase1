from typing import Dict, Any

class CapabilityRegistry:
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        # Pre-register known tools; RealAppBuilder is treated as a tool
        self.register_tool("app_builder", {"kind":"builder","entry":"real_app_builder:real_app_builder"})

    def register_tool(self, name: str, meta: Dict[str,Any]):
        self.tools[name] = meta

    def get_tool(self, name: str):
        return self.tools.get(name)

registry = CapabilityRegistry()
