import json
import logging
import google.generativeai as genai
from app.logger import logger
from app.utils import require_env


class Planner:
    def __init__(self):
        self._configure_model()

    def _configure_model(self):
        try:
            api_key = require_env("GEMINI_API_KEY")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                "gemini-flash-latest",
                generation_config={"temperature": 0.2}
            )
        except Exception as exc:
            logger.exception("Planner Gemini initialization failed")
            self.model = None

    def _generate(self, prompt: str) -> str:
        if not self.model:
            raise RuntimeError("Gemini model is unavailable")
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def _extract_json(self, raw_text: str) -> dict:
        try:
            start = raw_text.index("{")
            end = raw_text.rindex("}") + 1
            content = raw_text[start:end]
            return json.loads(content)
        except Exception as exc:
            logger.exception("Failed to parse planner JSON output")
            raise ValueError(f"Planner output is not valid JSON: {exc}")

    def plan(self, question: str, previous_steps: list[dict]) -> dict:
        prompt = self._build_plan_prompt(question, previous_steps)
        output = self._generate(prompt)
        logger.info(f"Planner decision output: {output}")
        return self._extract_json(output)

    def synthesize(self, question: str, tool_results: list[dict]) -> str:
        prompt = self._build_synthesis_prompt(question, tool_results)
        output = self._generate(prompt)
        logger.info("Planner synthesis output generated")
        return output.strip()

    def _build_plan_prompt(self, question: str, previous_steps: list[dict]) -> str:
        steps_summary = (
            "\n".join([
                f"{idx + 1}. {step.get('action', '')}: {step.get('description', '')}"
                for idx, step in enumerate(previous_steps)
            ])
            if previous_steps
            else "None"
        )

        return f"""
You are an AI agent planner for an ERP assistant.
Select the next action from the allowed tools.
Allowed actions: rag_search, direct_answer.
Return only strict JSON with keys:
{{"action":"...","input":{{...}}}}

IMPORTANT: Always include the "input" field.
For rag_search action, the input must be: {{"question": "{question}"}}
For direct_answer action, the input must be: {{"question": "{question}"}}

Do not add any text outside the JSON object.

Decision Rules:
- If the question is about ERP processes, finance, procurement, accounts, invoices, SAP, O2C, P2P, or business operations → use rag_search
- If the question is about general knowledge, AI, programming, definitions, or non-ERP topics → use direct_answer

Question:
{question}

Previous steps:
{steps_summary}

Tool reference:
- rag_search: retrieves ERP context and sources for business-related questions.
- direct_answer: answers general knowledge questions directly.

Output:
"""

    def _build_synthesis_prompt(self, question: str, tool_results: list[dict]) -> str:
        results_section = ""
        if tool_results:
            for idx, result in enumerate(tool_results, start=1):
                results_section += f"Tool result {idx}:\n"
                for key, value in result.items():
                    results_section += f"{key}: {value}\n"
                results_section += "\n"
        else:
            results_section = "No tool results were collected.\n\n"

        return f"""
You are an ERP assistant.
Use the collected tool results to answer the user's question clearly and concisely.
Question:
{question}

Collected data:
{results_section}

Instructions:
- Keep the answer under 120 words.
- Use plain language.
- Include a short source summary if sources exist.
- Return only the final answer text.
"""
