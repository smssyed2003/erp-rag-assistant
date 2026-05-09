from typing import Dict, Optional
from app.tools.base_tool import BaseTool
from app.tools.rag_tool import RAGTool
from app.tools.direct_answer_tool import DirectAnswerTool


class ToolRegistry:
    def __init__(self, rag_engine):
        self._tools: Dict[str, BaseTool] = {
            RAGTool.name: RAGTool(rag_engine),
            DirectAnswerTool.name: DirectAnswerTool(rag_engine.retriever)
        }

    def get(self, tool_name: str) -> Optional[BaseTool]:
        return self._tools.get(tool_name)

    def list_tools(self):
        return list(self._tools.keys())
