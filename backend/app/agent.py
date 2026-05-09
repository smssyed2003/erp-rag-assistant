from app.logger import logger
from app.planner import Planner
from app.tool_registry import ToolRegistry


class Agent:
    def __init__(self, rag_engine):
        self.rag_engine = rag_engine
        self.planner = Planner()
        self.tool_registry = ToolRegistry(rag_engine)

    def run(self, question: str, session_id: str) -> dict:
        steps = []
        tool_results = []

        for iteration in range(3):
            try:
                decision = self.planner.plan(question, steps)
            except Exception as exc:
                logger.exception("Planner failed during action decision")
                return self._fallback(question, session_id, steps, str(exc))

            action = decision.get("action", "finish")
            tool_input = decision.get("input", {})

            # Safety layer: ensure input is valid
            if action in ["rag_search", "direct_answer"]:
                if not tool_input or "question" not in tool_input:
                    logger.warning(f"Planner returned invalid input for {action}: {tool_input}. Auto-filling with question.")
                    tool_input = {"question": question}

            if action == "direct_answer":
                # Run the tool and break
                tool = self.tool_registry.get(action)
                if tool:
                    try:
                        result = tool.run(tool_input)
                        summary = self._summarize_tool_result(action, result)
                        steps.append({
                            "action": action,
                            "description": summary,
                            "result": summary
                        })
                        tool_results.append(result)
                    except Exception as exc:
                        logger.exception("Tool execution failed")
                        steps.append({
                            "action": action,
                            "description": f"Tool execution failed: {exc}"
                        })
                        return self._fallback(question, session_id, steps, str(exc))
                break
            elif action == "finish":
                logger.info("Planner chose finish action")
                break

            tool = self.tool_registry.get(action)
            if not tool:
                logger.warning(f"Unknown tool requested: {action}")
                steps.append({
                    "action": action,
                    "description": f"Unknown tool requested: {action}"
                })
                break

            logger.info(f"Executing tool {action} with input: {tool_input}")

            try:
                result = tool.run(tool_input)
            except Exception as exc:
                logger.exception("Tool execution failed")
                steps.append({
                    "action": action,
                    "description": f"Tool execution failed: {exc}"
                })
                return self._fallback(question, session_id, steps, str(exc))

            summary = self._summarize_tool_result(action, result)
            steps.append({
                "action": action,
                "description": summary,
                "result": summary
            })
            tool_results.append(result)

        try:
            answer = self.planner.synthesize(question, tool_results)
        except Exception as exc:
            logger.exception("Final answer synthesis failed")
            return self._fallback(question, session_id, steps, str(exc))

        sources = self._collect_sources(tool_results)
        return {
            "answer": answer,
            "steps": steps,
            "sources": sources,
        }

    def _collect_sources(self, tool_results: list[dict]) -> list[str]:
        sources = []
        for result in tool_results:
            sources.extend(result.get("sources", []))
        return list(dict.fromkeys(sources))

    def _summarize_tool_result(self, action: str, result: dict) -> str:
        if action == "rag_search":
            return f"Found {len(result.get('sources', []))} source(s)."
        elif action == "direct_answer":
            return "Answered directly using LLM."
        return "Tool executed successfully."

    def _fallback(self, question: str, session_id: str, steps: list[dict], error_text: str) -> dict:
        logger.warning(f"Using fallback direct RAG answer because: {error_text}")
        rag_response = self.rag_engine.query(question, session_id)
        steps.append({
            "action": "fallback",
            "description": "Fallback to direct RAG answer after planner/tool failure"
        })
        return {
            "answer": rag_response.get("answer", ""),
            "steps": steps,
            "sources": rag_response.get("sources", []),
        }
