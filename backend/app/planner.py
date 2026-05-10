import json
import logging
from google import genai
from google.genai import types
from app.utils import require_env
from app.logger import logger

class Planner:
    def __init__(self):
        self._configure_model()

    def _configure_model(self):
        try:
            api_key = require_env("GEMINI_API_KEY")
            self.client = genai.Client(api_key=api_key)
            
            # Using Gemma 4 26B A4B IT for logical routing
            self.model_name = "models/gemma-4-26b-a4b-it"

            self.generation_config = types.GenerateContentConfig(
                temperature=0.0,  # Deterministic for JSON
                max_output_tokens=2048, # Increased to allow for long synthesis
                response_mime_type="application/json" 
            )
            logger.info("Planner Gemma 4 initialized successfully")
        except Exception as exc:
            logger.exception("Planner Gemma initialization failed")
            self.client = None

    def _generate(self, prompt: str, is_json: bool = True) -> str:
        if not self.client:
            raise RuntimeError("Gemma model is unavailable")
        
        # Use a temporary config for synthesis if we want free-form text instead of JSON
        config = self.generation_config
        if not is_json:
            config = types.GenerateContentConfig(
                temperature=0.1, # Slight flexibility for natural language
                max_output_tokens=2048
            )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            return response.text.strip() if response.text else ""
        except Exception as exc:
            logger.exception("Planner generation failed")
            raise RuntimeError(f"Planner generation failed: {exc}")

    def _extract_json(self, raw_text: str) -> dict:
        try:
            # Fix: Ensure the string literals are properly closed
            clean_text = raw_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as exc:
            logger.error(f"JSON Parse Error. Raw: {raw_text}")
            raise ValueError(f"Invalid JSON from planner: {exc}")

    def plan(self, question: str, previous_steps: list[dict]) -> dict:
        prompt = self._build_plan_prompt(question, previous_steps)
        output = self._generate(prompt, is_json=True)
        return self._extract_json(output)

    def synthesize(self, question: str, tool_results: list[dict]) -> str:
        prompt = self._build_synthesis_prompt(question, tool_results)
        # Use is_json=False to allow for standard text response
        return self._generate(prompt, is_json=False)

    # =====================================================
    # REFINED PROMPTS (NO WORD LIMITS)
    # =====================================================

    def _build_plan_prompt(self, question: str, previous_steps: list[dict]) -> str:
        history = "None"
        if previous_steps:
            history = "\n".join([f"- Step {i}: {s.get('action')}" for i, s in enumerate(previous_steps)])

        return f"""
TASK: Route the user query.
USER QUERY: "{question}"
HISTORY: {history}

CLASSIFICATION CRITERIA:
- rag_search: For queries regarding ERP modules, business logic, procurement, finance, SAP, or internal company procedures.
- direct_answer: For coding help, general AI questions, greetings, or general external knowledge.

JSON OUTPUT ONLY:
{{
  "action": "rag_search" | "direct_answer",
  "reasoning": "Brief logic for choice",
  "input": {{ "question": "{question}" }}
}}
"""

    def _build_synthesis_prompt(self, question: str, tool_results: list[dict]) -> str:
        data_context = ""
        for i, res in enumerate(tool_results):
            # Capture as much detail as possible from the tool results
            data_context += f"--- DATA SOURCE {i+1} ---\n{res}\n\n"

        return f"""
ROLE: Senior ERP Process Consultant
TASK: Provide a comprehensive and professional answer based strictly on the collected data.

USER QUESTION: 
{question}

COLLECTED ERP DATA:
{data_context}

INSTRUCTIONS:
1. Provide a thorough explanation. If a process has multiple steps, list them clearly.
2. Maintain a professional, business-neutral tone.
3. If the collected data contains detailed technical steps or long policy descriptions, include them fully to ensure the user has all necessary information.
4. Do not use phrases like "Based on the search results" or "The tool returned". Speak as the expert.
5. If the data provided is insufficient to answer the question completely, explain what is missing.

FINAL RESPONSE:
"""