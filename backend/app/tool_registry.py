"""Tool registry for managing available tools for agent execution."""

from app.tools.rag_tool import RAGTool
from app.tools.direct_answer_tool import DirectAnswerTool
from app.logger import logger


class ToolRegistry:
    """Registry for managing and accessing tools available to the agent."""
    
    def __init__(self, rag_engine):
        """
        Initialize tool registry with available tools.
        
        Args:
            rag_engine: RAGEngine instance for tool operations
        """
        self.rag_engine = rag_engine
        self.tools = {
            "rag_search": RAGTool(rag_engine),
            "direct_answer": DirectAnswerTool(rag_engine),
        }
        logger.info(f"ToolRegistry initialized with {len(self.tools)} tools: {list(self.tools.keys())}")
    
    def get(self, tool_name):
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of the tool to retrieve
            
        Returns:
            Tool instance or None if not found
        """
        tool = self.tools.get(tool_name)
        if tool is None:
            logger.warning(f"Tool '{tool_name}' not found in registry")
        return tool
    
    def list_tools(self):
        """
        List all available tool names.
        
        Returns:
            List of tool names
        """
        return list(self.tools.keys())
    
    def execute(self, tool_name, input_data):
        """
        Execute a tool with given input data.
        
        Args:
            tool_name: Name of the tool to execute
            input_data: Input data for the tool
            
        Returns:
            Tool execution result or None if tool not found
        """
        tool = self.get(tool_name)
        if tool is None:
            logger.error(f"Cannot execute unknown tool: {tool_name}")
            return None
        
        try:
            logger.debug(f"Executing tool '{tool_name}' with input: {input_data}")
            result = tool.run(input_data)
            logger.debug(f"Tool '{tool_name}' execution completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {str(e)}", exc_info=True)
            raise
