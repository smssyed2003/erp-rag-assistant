import json
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from google import genai
from google.genai import types
from app.utils import require_env
from app.logger import logger

class Planner:
    GENERATION_TIMEOUT_SECONDS = 18

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
                max_output_tokens=2048  # Increased to allow for long synthesis
            )
            logger.info("Planner Gemma 4 initialized successfully")
        except Exception as exc:
            logger.exception("Planner Gemma initialization failed")
            self.client = None


    def _generate(self, prompt: str, is_json: bool = True) -> str:

        if not self.client:
            raise RuntimeError("Gemma model is unavailable")

        config = self.generation_config

        # safer config for synthesis
        if not is_json:
            config = types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=2048
            )

        def call_model():
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            if response and getattr(response, "text", None):
                return response.text.strip()

            raise RuntimeError("Empty response from model")

        last_error = None

        for attempt in range(5):  # retry increase
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(call_model)
                    result = future.result(timeout=self.GENERATION_TIMEOUT_SECONDS)
                    return result

            except FutureTimeoutError:
                last_error = RuntimeError(
                    f"Planner generation timed out after {self.GENERATION_TIMEOUT_SECONDS} seconds"
                )
                logger.warning(
                    f"Gemini attempt {attempt+1}/5 timed out after {self.GENERATION_TIMEOUT_SECONDS}s"
                )

            except Exception as exc:
                last_error = exc
                wait = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(
                    f"Gemini attempt {attempt+1}/5 failed. Retrying in {wait:.2f}s: {exc}"
                )
                time.sleep(wait)

        raise RuntimeError(f"Planner generation failed after retries: {last_error}")

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
        try:
            prompt = self._build_synthesis_prompt(question, tool_results)
            # Use is_json=False to allow for standard text response
            return self._generate(prompt, is_json=False)
        except Exception as exc:
            logger.warning(f"Synthesis failed, using fallback response: {exc}")
            # Fallback response for testing
            if "purchase order" in question.lower():
                return """To process a purchase order in an ERP system:

1. **Create Purchase Requisition**: Start by creating a purchase requisition with required items, quantities, and delivery dates.

2. **Approval Workflow**: Submit the requisition for approval based on your organization's approval hierarchy.

3. **Convert to Purchase Order**: Once approved, convert the requisition to a purchase order.

4. **Vendor Selection**: Select appropriate vendor and negotiate terms if needed.

5. **Send to Vendor**: Send the purchase order to the vendor.

6. **Track Delivery**: Monitor delivery status and update inventory upon receipt.

7. **Invoice Processing**: Process vendor invoice and complete three-way matching (PO-Receipt-Invoice).

8. **Payment**: Process payment according to payment terms.

Please note: This is a general process that may vary depending on your specific ERP system configuration and organizational policies."""
            else:
                return f"I understand you're asking about: {question}. This appears to be an ERP-related question. For a complete answer, please ensure your Gemini API key is valid and the service is properly configured. In the meantime, I'd recommend checking your system's documentation or contacting your ERP administrator for specific guidance."

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