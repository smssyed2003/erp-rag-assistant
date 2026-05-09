# ERP AI Assistant Documentation

## 1. Project Overview

### What is this project?
This project is an ERP AI Assistant built on top of modern AI and search technologies. It combines a backend server, retrieval systems, a large language model, and an Angular frontend to help users ask ERP-related questions and get helpful, context-aware answers.

### What problem does it solve?
ERP systems carry a lot of information. People often need quick answers about ERP concepts, workflows, or documentation. This project solves that by turning ERP knowledge into a searchable AI assistant.

### Real-world use case (ERP assistant)
Imagine a user asking, "How do I approve a purchase order in ERP?" Instead of reading long manuals, the assistant finds the right content, uses an AI model to answer it clearly, and provides sources. This is useful for training, support, and decision-making in finance, logistics, procurement, and operations teams.

---

## 2. Key Concepts Explained

### What is AI?
AI stands for Artificial Intelligence. In this project, AI means using software to understand questions and generate answers like a human would.

- Simple: AI is like a smart helper that reads information and responds to questions.
- Technical: AI models learn patterns from large datasets and use that knowledge to generate text.

### What is an LLM?
LLM means Large Language Model.

- Simple: Think of it like a robotic writer that has read lots of text and can answer questions.
- Technical: An LLM uses machine learning architectures such as transformers to predict the next word in a sentence. It can complete text, translate, summarize, and answer questions.

### What is RAG (Retrieval-Augmented Generation)?
RAG stands for Retrieval-Augmented Generation.

- Simple: It is like asking a smart assistant to look up the best pages in a manual before answering.
- Technical: RAG combines two steps:
  1. Retrieve relevant documents from a knowledge base.
  2. Use an LLM to generate the final answer using those documents as context.

### Why RAG is needed instead of plain LLM
A plain LLM tries to answer from its own learned memory. That works for general knowledge, but it can miss specific facts or make things up.

- Analogy: A plain LLM is like someone who memorized a textbook. RAG is like somebody who can open the textbook and quote the exact page.
- The result: more accurate, up-to-date answers that are grounded in real ERP content.

### What is an AI Agent?
An AI Agent is a smarter wrapper around an LLM.

- Simple: It is like a helper who can decide what tools to use, then use them, and finally answer.
- Technical: An agent includes a planner, tools, and an execution loop. The planner decides the next action, tools perform tasks, and the agent synthesizes the final answer.

### Difference between RAG vs AI Agent
- RAG is a structured pattern: search first, then generate.
- AI Agent is a broader architecture: it can decide whether to search, summarize, query tools, or finish the answer.

In this project:
- The existing RAG engine remains the core retrieval and generation system.
- The AI Agent is added as a separate module to orchestrate tool use without changing the RAG logic.

---

## 3. System Architecture

### Overall flow
The system works like this:

1. User sends a question from the frontend.
2. Frontend calls the backend API.
3. Backend receives the request.
4. If using agent mode, the agent plans and calls tools.
5. The RAG tool retrieves ERP context and sources.
6. The LLM generates the final answer.
7. The backend returns the answer, sources, and agent steps.
8. Frontend displays the result.

### Responsibilities of each component
- **User**: asks the question.
- **Frontend**: sends requests and displays conversational UI.
- **Backend**: handles API requests, routes them to RAG or agent logic.
- **Agent**: decides whether to use tools, maintains reasoning step history.
- **Tools**: perform specialized work such as retrieval.
- **RAG Engine**: fetches documents and generates answers.
- **LLM**: produces natural language output.

Flow diagram:

User → Frontend → Backend → Agent → Tools → RAG → LLM → Response

---

## 4. Backend Deep Dive

### RAG Engine
The RAG engine is the heart of the ERP assistant.

#### What it does
It takes a question, finds relevant ERP content, and generates a concise answer.

#### Hybrid search (Vector + Keyword)
The engine uses a hybrid search strategy:
- **FAISS**: finds similar documents using vector embeddings.
- **BM25**: finds documents using keyword matching.

Why both?
- FAISS is good at semantic search: it finds text that means the same thing.
- BM25 is good at exact keyword matching: it finds documents with the same terms.

Combining them gives stronger retrieval than using only one method.

### Retriever
The Retriever is responsible for fetching relevant documents.

#### How documents are fetched
1. The question is rewritten into a retrieval-friendly query.
2. The query is embedded into a vector using Gemini embeddings.
3. FAISS searches the vector index for semantically similar text.
4. BM25 searches text documents for keyword overlap.
5. The results are merged and ranked.

#### How ranking works
- The system collects top results from FAISS and BM25.
- It measures keyword overlap and sorts results.
- The best matching passages are returned as `context` and `sources`.

This ensures the answer uses relevant ERP content.

### Gemini Integration
Gemini is used in two ways:

#### Embeddings
- Questions are turned into vectors using Gemini embeddings.
- These vectors allow similarity search in FAISS.
- Embeddings capture meaning, not just exact wording.

#### Answer generation
- The RAG engine builds a prompt containing context, memory, and instructions.
- Gemini generates the final answer from this prompt.
- The model is configured with low temperature for reliable responses.

### Memory Manager
The Memory Manager keeps track of session history.

#### Why memory is needed
- It helps the assistant remember earlier exchanges.
- It allows context to flow across multiple turns.

#### How session works
- Each session ID stores recent user questions and assistant answers.
- When a new question arrives, the system includes this history in the prompt.
- This creates a simple form of conversational memory.

---

## 5. AI Agent Architecture

### What is an Agent?
An agent is a higher-level orchestrator.

- It decides what to do next.
- It can call tools such as search.
- It keeps a history of its reasoning.

### Planner (decision making)
The planner is the component that asks:
- Should I retrieve more information?
- Should I finish now?

It uses Gemini to make this decision and returns strict JSON:
```json
{ "action": "...", "input": { ... } }
```

### Tools (rag_search, etc.)
Tools are small programs the agent uses.
- `rag_search` is the main tool in this project.
- It wraps the existing RAGEngine retrieval logic.
- It returns structured output with `context` and `sources`.

### Agent loop (step-by-step reasoning)
The agent runs in a loop with a maximum of 3 iterations:
1. Planner decides the next action.
2. If action is `rag_search`, the tool is called.
3. The result is recorded as a step.
4. The planner may decide again.
5. After the loop, the final answer is synthesized.

Flow:
User Question → Planner → Tool → Result → Final Answer

This allows the system to reason through intermediate steps instead of answering directly in one shot.

---

## 6. Streaming (Real-Time Responses)

### What is streaming?
Streaming means sending partial output as it becomes available.

- Simple: the answer appears gradually, like typing on the screen.
- Technical: the server sends chunks of data instead of waiting for the full response.

### Why it improves UX
- Users see activity immediately.
- It feels faster and more interactive.
- It reduces the waiting anxiety of a long AI call.

### How it works conceptually
1. The backend receives the request.
2. The LLM begins generating text.
3. The response is sent in pieces.
4. The frontend updates the UI in real time.

This project currently focuses on agent reasoning and a simulated typing experience in the frontend.
A full `/agent-ask-stream` endpoint would add real server streaming.

---

## 7. Frontend (Angular)

### How UI interacts with backend
- The Angular app sends HTTP POST requests to backend endpoints.
- It receives JSON responses.
- It displays user messages, bot answers, sources, and agent steps.

### Chat interface
- User messages are right-aligned in a blue bubble.
- Bot responses are left-aligned with shadow and rounded cards.
- Sources are shown as tags or chips.
- Agent steps can be expanded to reveal reasoning.

### API calls
- The chat service uses `HttpClient`.
- It sends `question` and `session_id`.
- It receives `answer`, `steps`, and `sources`.

### Streaming integration (if present)
- The current UI simulates typing for the bot response.
- Real streaming would use a streaming endpoint and update the bubble as text arrives.

---

## 8. API Endpoints

### POST /ask
This endpoint uses the legacy RAG engine.

#### Request format
```json
{
  "session_id": "string",
  "question": "string"
}
```

#### Response format
```json
{
  "response": {
    "answer": "...",
    "sources": ["..."]
  }
}
```

#### Example
```json
{
  "session_id": "session123",
  "question": "What is a purchase order?"
}
```

### POST /agent-ask
This endpoint uses the new AI Agent layer.

#### Request format
```json
{
  "session_id": "string",
  "question": "string"
}
```

#### Response format
```json
{
  "answer": "...",
  "steps": [
    {
      "action": "rag_search",
      "description": "Retrieve ERP context and sources from the RAG engine"
    }
  ],
  "sources": ["..."]
}
```

#### Example
```json
{
  "session_id": "session123",
  "question": "How do I reconcile invoices in ERP?"
}
```

### POST /agent-ask-stream
This endpoint is a natural next step for real-time streaming.

#### In this project
- The endpoint is described here as a conceptual extension.
- The current backend does not include a full streaming implementation.
- A streaming version would send partial answers while the LLM is still generating.

#### Expected request format
```json
{
  "session_id": "string",
  "question": "string"
}
```

#### Expected response format
Streamed text chunks with metadata such as:
```json
{
  "type": "partial",
  "text": "..."
}
```
and final completion data.

---

## 9. Deployment

### Backend (Render)
The backend is deployed on Render as a Python FastAPI service.

#### What happens during deployment
- Render installs dependencies.
- The backend code and environment variables are loaded.
- FastAPI starts and listens for requests.

#### Why it sleeps (cold start)
Render can pause inactive services to save resources.
When a new request arrives, the app wakes up again.
This causes a delay known as a cold start.

### Frontend (Vercel)
The Angular frontend is deployed on Vercel.

#### Build and deploy process
- Vercel builds the Angular app into static files.
- It uploads the optimized static site.
- Visitors receive a fast web page that calls the backend.

---

## 10. Issues Faced & Learnings

### Python version issue
- Problem: Different Python versions can break dependency installation.
- Cause: Libraries like FAISS and Google packages require specific Python compatibility.
- Fix: Use a matching Python version in the backend environment and `runtime.txt`.
- Learning: Lock the Python runtime early to avoid surprises.

### API key issue
- Problem: Gemini API requests fail without a valid key.
- Cause: Missing or misconfigured `GEMINI_API_KEY` environment variable.
- Fix: Store the key in Render and local `.env`, and load it with `dotenv`.
- Learning: Secrets must be handled carefully and validated during startup.

### Planner input bug
- Problem: The planner could return invalid JSON or bad actions.
- Cause: LLM output is not always strictly formatted.
- Fix: Use a strict JSON prompt and parse with robust error handling.
- Learning: When using LLMs for control flow, always validate the output.

### CORS issues
- Problem: Frontend could not reach backend from the browser.
- Cause: Cross-origin requests were blocked by the browser.
- Fix: Enable CORS in FastAPI with `CORSMiddleware`.
- Learning: Modern web apps must allow cross-origin requests safely.

### ng permission issue
- Problem: Angular access or build failures can block UI deployment.
- Cause: Incorrect file paths, missing dependencies, or Angular config errors.
- Fix: Check `angular.json`, package setup, and `tsconfig`.
- Learning: Frontend and backend both need consistent environment setup.

---

## 11. Limitations

### Cold start delay
The backend may take extra time when the Render service wakes from sleep.

### LLM dependency
The system relies on Gemini. If the model is unavailable or rate-limited, answers may fail.

### Accuracy limitations
- The assistant can still provide wrong or incomplete ERP advice.
- RAG improves accuracy, but the model may hallucinate if the context is weak.

---

## 12. Future Improvements

### Multi-agent system
Add more agents for specialized tasks such as ERP process analysis, finance guidance, or policy checks.

### ERP API integrations
Connect the assistant to real ERP systems so it can answer with live data and transactions.

### Better memory
Improve session memory with state tracking, user intent, or longer context windows.

### UI enhancements
- Add chat history persistence.
- Add real streaming support.
- Add role-based answers or interactive follow-up suggestions.

---

## 13. Conclusion

### What was achieved
This project built a practical ERP AI assistant using RAG and agent architecture. It allows users to ask ERP questions and receive grounded, context-rich answers.

### What was learned
- How retrieval and generation work together.
- Why hybrid search is stronger than plain search.
- How a planner and tools make AI behavior more structured.
- How frontend and backend communicate in a modern web app.

### Why this project is valuable
It bridges ERP domain knowledge with conversational AI, making technical content easier to explore. For teams and learners, it turns static manuals into an interactive assistant that can answer questions quickly and intelligently.
