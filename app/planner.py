import json
import logging

from google import genai
from google.genai import types

from app.utils import require_env
from app.logger import logger


class Planner:

    def __init__(self):
        self._configure_model()

    # =====================================================
    # MODEL CONFIGURATION
    # =====================================================

    def _configure_model(self):

        try:

            api_key = require_env(
                "GEMINI_API_KEY"
            )

            self.client = genai.Client(
                api_key=api_key
            )

            # Gemma model
            self.model_name = "gemma-3-27b-it"

            self.generation_config = (
                types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=512
                )
            )

            logger.info(
                "Planner Gemma initialized successfully"
            )

        except Exception as exc:

            logger.exception(
                "Planner Gemma initialization failed"
            )

            self.client = None

    # =====================================================
    # GENERATION
    # =====================================================

    def _generate(self, prompt: str) -> str:

        if not self.client:
            raise RuntimeError(
                "Gemma model is unavailable"
            )

        try:

            response = (
                self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=self.generation_config
                )
            )

            if response.text:
                return response.text.strip()

            return ""

        except Exception as exc:

            logger.exception(
                "Planner generation failed"
            )

            raise RuntimeError(
                f"Planner generation failed: {exc}"
            )

    # =====================================================
    # JSON EXTRACTION
    # =====================================================

    def _extract_json(self, raw_text: str) -> dict:

        try:

            start = raw_text.index("{")

            end = raw_text.rindex("}") + 1

            content = raw_text[start:end]

            return json.loads(content)

        except Exception as exc:

            logger.exception(
                "Failed to parse planner JSON output"
            )

            raise ValueError(
                f"Planner output is not valid JSON: {exc}"
            )

    # =====================================================
    # PLANNING
    # =====================================================

    def plan(
        self,
        question: str,
        previous_steps: list[dict]
    ) -> dict:

        prompt = self._build_plan_prompt(
            question,
            previous_steps
        )

        output = self._generate(prompt)

        logger.info(
            f"Planner decision output: {output}"
        )

        return self._extract_json(output)

    # =====================================================
    # SYNTHESIS
    # =====================================================

    def synthesize(
        self,
        question: str,
        tool_results: list[dict]
    ) -> str:

        prompt = self._build_synthesis_prompt(
            question,
            tool_results
        )

        output = self._generate(prompt)

        logger.info(
            "Planner synthesis output generated"
        )

        return output.strip()

    # =====================================================
    # PLAN PROMPT
    # =====================================================

    def _build_plan_prompt(
        self,
        question: str,
        previous_steps: list[dict]
    ) -> str:

        steps_summary = (
            "\n".join([
                f"{idx + 1}. "
                f"{step.get('action', '')}: "
                f"{step.get('description', '')}"
                for idx, step in enumerate(
                    previous_steps
                )
            ])
            if previous_steps
            else "None"
        )

        question_json = json.dumps(question)

        return f"""
You are an AI ERP planning agent.

Select the next action.

Allowed actions:
- rag_search
- direct_answer

Return ONLY valid JSON.

Required format:

{{
  "action": "...",
  "input": {{
    "question": {question_json}
  }}
}}

Rules:
- ERP/business/process/SAP/finance/procurement questions
  → rag_search

- General knowledge/programming/AI questions
  → direct_answer

Question:
{question}

Previous steps:
{steps_summary}

Output:
"""

    # =====================================================
    # SYNTHESIS PROMPT
    # =====================================================

    def _build_synthesis_prompt(
        self,
        question: str,
        tool_results: list[dict]
    ) -> str:

        results_section = ""

        if tool_results:

            for idx, result in enumerate(
                tool_results,
                start=1
            ):

                results_section += (
                    f"Tool result {idx}:\n"
                )

                for key, value in result.items():

                    results_section += (
                        f"{key}: {value}\n"
                    )

                results_section += "\n"

        else:

            results_section = (
                "No tool results were collected.\n\n"
            )

        return f"""
You are an ERP assistant.

Use the collected tool results
to answer the user's question.

Question:
{question}

Collected Data:
{results_section}

Instructions:
- Keep answer under 120 words
- Use simple language
- Mention sources briefly if available
- Return only final answer text
"""