# ERP RAG System - Complete Code Architecture Guide

**Last Updated**: May 2026  
**Version**: 1.0  
**Status**: Production Ready

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Backend Code Structure](#backend-code-structure)
4. [Frontend Code Structure](#frontend-code-structure)
5. [Data Flow](#data-flow)
6. [Code Explanations](#code-explanations)
7. [Configuration & Environment](#configuration--environment)
8. [Deployment Architecture](#deployment-architecture)

---

## Project Overview

### What is the ERP RAG System?

The **ERP RAG System** is an AI-powered assistant that helps users ask questions about ERP (Enterprise Resource Planning) systems and get intelligent, context-aware answers.

**Key Technologies**:
- **Backend**: FastAPI (Python) + Google Gemini API
- **Frontend**: Angular 17 + TypeScript + RxJS
- **AI/ML**: Retrieval-Augmented Generation (RAG) + AI Agent Architecture
- **Deployment**: Render (Backend) + Vercel (Frontend)

### How It Works (Simple Explanation)

```
User asks question
        ↓
Frontend sends to Backend
        ↓
Backend searches ERP knowledge base
        ↓
AI Agent decides best approach
        ↓
Backend retrieves relevant documents
        ↓
AI generates smart answer with sources
        ↓
Response sent back to Frontend
        ↓
User sees answer with sources
```

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                            │
│              (Angular Frontend - Port 4200)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Chat Component   │  Services  │  Styles  │ Config   │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST API
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND API                               │
│              (FastAPI - Port 8000/Production)                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  main.py (FastAPI App)                               │   │
│  │  ├─ /ask endpoint      (RAG mode)                    │   │
│  │  └─ /agent-ask endpoint (Agent mode)                 │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Agent Layer                                         │   │
│  │  ├─ agent.py      (Agent orchestration)              │   │
│  │  ├─ planner.py    (Decision making)                  │   │
│  │  └─ tool_registry.py (Tool management)               │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  RAG Engine (Core System)                            │   │
│  │  ├─ rag_engine.py (Main orchestrator)                │   │
│  │  ├─ retrieval.py  (Document retrieval)               │   │
│  │  └─ tools/        (RAG & Direct answer tools)        │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Utilities & Configuration                           │   │
│  │  ├─ memory.py     (Session management)               │   │
│  │  ├─ logger.py     (Logging system)                   │   │
│  │  ├─ utils.py      (Helper functions)                 │   │
│  │  └─ config.py     (Configuration)                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬──────────────────────────────────┘
                          │ API Calls
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              EXTERNAL SERVICES                               │
│  ├─ Google Gemini API (LLM - Language Model)                │
│  └─ ERP Knowledge Base (FAISS Vector Store)                 │
└─────────────────────────────────────────────────────────────┘
```

### Component Interactions

| Component | Purpose | Communicates With |
|-----------|---------|-------------------|
| **Frontend (Angular)** | User interface | Backend API |
| **Backend API (main.py)** | Entry point, routing | Agent, RAG Engine |
| **Agent** | Decision making | Planner, Tools |
| **Planner** | Tool selection | Tool Registry |
| **RAG Engine** | Answer generation | Retrieval, LLM |
| **Retrieval** | Document search | FAISS, BM25 |
| **Tools** | Specialized tasks | RAG Engine |
| **Memory** | Session storage | Agent, Backend |
| **Logger** | Event tracking | All components |

---

## Backend Code Structure

### `/backend` Directory Overview

```
backend/
├── app/                          # Main application code
│   ├── main.py                   # FastAPI app, endpoints, lifecycle
│   ├── agent.py                  # AI Agent orchestration
│   ├── planner.py                # Decision-making logic
│   ├── rag_engine.py             # RAG pipeline coordinator
│   ├── retrieval.py              # Document search & retrieval
│   ├── tool_registry.py          # Tool management system
│   ├── memory.py                 # Session memory management
│   ├── logger.py                 # Logging configuration
│   ├── utils.py                  # Helper utilities
│   ├── config.py                 # Configuration settings
│   ├── exceptions.py             # Custom exceptions
│   ├── tools/                    # Tool implementations
│   │   ├── base_tool.py          # Base tool class
│   │   ├── rag_tool.py           # RAG search tool
│   │   └── direct_answer_tool.py # Direct answer tool
│   └── __init__.py               # Package initialization
├── requirements.txt              # Python dependencies
├── runtime.txt                   # Python version for deployment
├── .env                          # Environment variables (gitignored)
└── .venv/                        # Virtual environment
```

### Key Backend Files Explained

#### 1. **main.py** - FastAPI Application Entry Point

**What it does**:
- Initializes the FastAPI application
- Sets up middleware (CORS, logging)
- Manages application lifecycle (startup/shutdown)
- Defines API endpoints
- Handles error responses

**Key endpoints**:
```python
POST /ask
- Body: { "question": string, "session_id": string }
- Returns: { "answer": string, "sources": array }
- Uses: RAG engine directly

POST /agent-ask
- Body: { "question": string, "session_id": string }
- Returns: { "answer": string, "sources": array, "steps": array }
- Uses: Agent with planning and tools
```

**Code Structure**:
```python
# 1. Load environment & initialize globals
rag: Optional[RAGEngine] = None
agent: Optional[Agent] = None

# 2. Startup: Initialize RAG and Agent
@lifespan
async def lifespan(app):
    # Initialize components
    # Set up logging
    yield  # Run app
    # Cleanup

# 3. Define request/response models
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    session_id: str = Field(...)

# 4. Set up endpoints
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    # Validate input
    # Call RAG engine
    # Return formatted response

@app.post("/agent-ask")
async def agent_ask_question(request: QuestionRequest):
    # Validate input
    # Call Agent
    # Return formatted response
```

**Why this approach**:
- FastAPI handles HTTP routing and validation automatically
- Lifespan manages resource initialization (RAG takes time to load)
- Request models validate input before processing
- Error handling returns proper HTTP status codes

---

#### 2. **agent.py** - AI Agent Orchestration

**What it does**:
- Orchestrates the decision-making process
- Maintains reasoning history
- Calls the planner to decide which tool to use
- Executes tools and collects results
- Synthesizes final answer

**Architecture**:
```python
class Agent:
    def __init__(self, planner, tool_registry, rag_engine, memory):
        self.planner = planner          # Decides what to do
        self.tool_registry = tool_registry  # Manages tools
        self.rag_engine = rag_engine    # Core RAG
        self.memory = memory            # Session state

    async def answer_question(question, session_id):
        # Step 1: Get memory for session
        memory_context = memory.get_context(session_id)
        
        # Step 2: Planner decides which tool to use
        action = planner.plan(question, memory_context)
        
        # Step 3: Get the tool
        tool = tool_registry.get_tool(action.tool_name)
        
        # Step 4: Execute tool
        result = await tool.execute(question, action.params)
        
        # Step 5: Store in memory (for context in future queries)
        memory.add_step(session_id, {
            'action': action,
            'result': result
        })
        
        # Step 6: Return answer
        return {
            'answer': result.answer,
            'sources': result.sources,
            'steps': memory.get_steps(session_id)
        }
```

**Why agents matter**:
- Flexible: Can use different tools based on question type
- Transparent: Shows reasoning steps to user
- Stateful: Remembers context from previous questions in same session
- Extensible: New tools can be added without changing core logic

---

#### 3. **planner.py** - Decision-Making Logic

**What it does**:
- Receives a question and context
- Uses the LLM (Gemini) to decide the best approach
- Returns the selected tool and parameters

**How it works**:
```python
class Planner:
    async def plan(question: str, context: Dict) -> Action:
        # Build a prompt that explains available tools
        prompt = f"""
        You are planning AI agent. Choose the best tool:
        - rag_search: For questions needing document retrieval
        - direct_answer: For general knowledge questions
        
        Question: {question}
        Context: {context}
        
        Respond with: {{"tool": "tool_name", "params": {{...}}}}
        """
        
        # Call Gemini API
        response = gemini_api.generate(prompt)
        
        # Parse response to get action
        action = parse_response(response)
        return action
```

**Decision logic**:
- If question about ERP procedures → use `rag_search`
- If general knowledge question → use `direct_answer`
- If question needs recent info → use `rag_search`

---

#### 4. **rag_engine.py** - RAG Pipeline

**What it does**:
- Coordinates the entire RAG process
- Retrieves relevant documents
- Generates answers using LLM
- Manages the flow between retrieval and generation

**RAG Flow**:
```python
class RAGEngine:
    async def generate_answer(question: str) -> Answer:
        # Step 1: Retrieve relevant documents
        documents = retrieval.search(question, top_k=5)
        
        # Step 2: Build context from documents
        context = "\n".join([
            f"Source {i}: {doc.text}" 
            for i, doc in enumerate(documents)
        ])
        
        # Step 3: Build answer prompt
        prompt = f"""
        Using the following ERP documentation:
        {context}
        
        Answer this question: {question}
        """
        
        # Step 4: Generate answer using Gemini
        answer_text = gemini_api.generate(prompt)
        
        # Step 5: Extract sources
        sources = [doc.source for doc in documents]
        
        return Answer(
            text=answer_text,
            sources=sources,
            confidence=calculate_confidence(documents)
        )
```

**Why RAG is better than plain LLM**:
| Aspect | Plain LLM | RAG |
|--------|-----------|-----|
| Knowledge source | Trained data only | Real documents + training |
| Accuracy | Can hallucinate | Grounded in sources |
| Freshness | Static | Can use latest docs |
| Traceability | Unknown | Shows exact sources |
| ERP-specific | Generic answers | Specialized answers |

---

#### 5. **retrieval.py** - Document Search

**What it does**:
- Loads ERP documents and creates embeddings
- Performs hybrid search (vector + keyword)
- Returns most relevant documents

**Search Process**:
```python
class Retriever:
    def __init__(self):
        # Load ERP documents
        self.documents = load_erp_chunks()  # from data/erp_chunks.json
        
        # Create FAISS vector index for semantic search
        self.faiss_index = create_embeddings(documents)
        
        # Create BM25 index for keyword search
        self.bm25_index = BM25(documents)
    
    def search(question: str, top_k: int = 5) -> List[Document]:
        # Vector search (semantic similarity)
        vector_results = faiss_index.search(
            embed(question),
            k=top_k
        )
        
        # Keyword search (BM25)
        keyword_results = bm25_index.search(question, k=top_k)
        
        # Combine and deduplicate results
        combined = merge_results(vector_results, keyword_results)
        
        return combined[:top_k]
```

**Hybrid Search Advantage**:
- **Vector Search**: Finds semantically similar content (handles rephrasing)
- **Keyword Search**: Catches exact terminology
- **Combined**: Best of both worlds

Example:
- Question: "How to process a PO?"
- Vector search: Finds "Purchase Order approval procedures"
- Keyword search: Finds "PO processing workflow"
- Combined: Returns both, highly relevant

---

#### 6. **memory.py** - Session Management

**What it does**:
- Stores conversation history per session
- Maintains context across multiple questions
- Manages memory cleanup (TTL)

**How it works**:
```python
class MemoryManager:
    def __init__(self, max_sessions=1000, ttl_minutes=60):
        self.sessions = {}  # session_id -> conversation history
        self.max_sessions = 1000
        self.ttl_minutes = 60
    
    def add_step(session_id: str, step: Dict):
        # Create session if not exists
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'created': now(),
                'steps': []
            }
        
        # Add the step
        self.sessions[session_id]['steps'].append({
            'timestamp': now(),
            'action': step['action'],
            'result': step['result']
        })
    
    def get_context(session_id: str) -> str:
        # Return formatted history for planner
        if session_id not in self.sessions:
            return ""
        
        steps = self.sessions[session_id]['steps']
        return "\n".join([
            f"Q{i}: {s['action']}\nA{i}: {s['result']}"
            for i, s in enumerate(steps[-5:])  # Last 5 exchanges
        ])
```

**Why session memory**:
- User asks: "What is a PO?" → Gets answer
- User asks: "How long does it take?" → AI remembers context
- Without memory: AI wouldn't know "it" refers to PO

---

#### 7. **tool_registry.py** - Tool Management

**What it does**:
- Manages all available tools
- Provides tools to the planner
- Handles tool registration and lookup

**Architecture**:
```python
class ToolRegistry:
    def __init__(self):
        self.tools = {}  # tool_name -> tool_instance
        
        # Register available tools
        self.register('rag_search', RAGTool(rag_engine))
        self.register('direct_answer', DirectAnswerTool(gemini_api))
    
    def register(tool_name: str, tool: BaseTool):
        self.tools[tool_name] = tool
    
    def get_tool(tool_name: str) -> BaseTool:
        if tool_name not in self.tools:
            raise ToolNotFoundError(f"Tool {tool_name} not found")
        return self.tools[tool_name]
    
    def list_tools(self) -> List[str]:
        return list(self.tools.keys())
```

**Built-in Tools**:

1. **rag_search** (`tools/rag_tool.py`):
   - Purpose: Search ERP documents and generate answer
   - When used: For ERP-specific questions
   - Output: { answer, sources }

2. **direct_answer** (`tools/direct_answer_tool.py`):
   - Purpose: Answer using general knowledge
   - When used: For general questions about ERP concepts
   - Output: { answer }

---

#### 8. **logger.py** - Logging System

**What it does**:
- Provides structured logging
- Tracks correlation IDs (trace requests end-to-end)
- Logs to file and console

**Usage throughout codebase**:
```python
logger.info("RAG Engine initialized successfully")
logger.error("Failed to load embeddings", exc_info=True)
logger.debug(f"Retrieved {len(docs)} documents")
```

**Why it matters**:
- Production debugging: See what happened when errors occur
- Performance monitoring: Track API response times
- Audit trail: Record all agent decisions
- Correlation: Link frontend request to backend logs

---

#### 9. **exceptions.py** - Custom Errors

**What it does**:
- Defines custom exception classes
- Provides structured error responses
- Maps exceptions to HTTP status codes

**Exception Hierarchy**:
```python
ERPRAGException (base)
├── InitializationError  (500 - startup failed)
├── ValidationError      (400 - bad input)
├── RAGError            (500 - retrieval/generation failed)
├── ToolError           (500 - tool execution failed)
├── MemoryError         (500 - session memory issue)
└── APIError            (500 - external API call failed)
```

**Why structured exceptions**:
- Consistency: All errors follow same format
- Debugging: Know exact problem type
- Client-friendly: Return appropriate HTTP status codes
- Recovery: Different handling based on error type

---

### Backend Dependencies

**Critical dependencies** (in `requirements.txt`):

```
fastapi==0.110.0           # Web framework
uvicorn==0.27.0            # ASGI server
google-generativeai==0.3.0 # Gemini API
python-dotenv==1.0.0       # Environment variables
faiss-cpu==1.7.4           # Vector search
rank-bm25==0.2.2           # Keyword search
pydantic==2.5.0            # Data validation
```

---

## Frontend Code Structure

### `/frontend` Directory Overview

```
frontend/
├── src/
│   ├── app/
│   │   ├── app.component.ts         # Root component
│   │   ├── app.component.html       # Root template
│   │   ├── app.component.css        # Root styles
│   │   ├── app.module.ts            # Module configuration
│   │   └── services/
│   │       ├── chat.component.ts    # Chat logic (modern control flow)
│   │       ├── chat.component.html  # Chat template (built-in directives)
│   │       ├── chat.component.css   # Chat styles (responsive)
│   │       └── chat.service.ts      # Backend communication
│   ├── environments/
│   │   ├── environment.ts           # Development config
│   │   └── environment.prod.ts      # Production config
│   ├── styles.css                   # Global styles
│   ├── main.ts                      # Bootstrap entry point
│   ├── index.html                   # HTML entry point
│   └── polyfills.ts                 # Browser compatibility
├── angular.json                     # Angular CLI config
├── tsconfig.json                    # TypeScript config
├── package.json                     # NPM dependencies
├── README.md                        # Frontend documentation
└── eslint.config.js                 # Code quality rules
```

### Key Frontend Files Explained

#### 1. **app.component.ts** - Root Component

**What it does**:
- Entry point for the entire Angular application
- Provides the main layout and navigation
- Houses the app title and description

**Code**:
```typescript
import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'ERP RAG Assistant';
}
```

**Explanation**:
- `@Component`: Angular decorator that marks this as a component
- `selector`: CSS selector to embed this component (`<app-root>`)
- `templateUrl`: HTML file for this component's view
- `styleUrls`: CSS files scoped to this component
- Properties like `title` can be used in the template via `{{ title }}`

---

#### 2. **app.module.ts** - Module Configuration

**What it does**:
- Declares which components, services, and modules are part of the app
- Configures dependency injection
- Sets up imports for Angular features

**Code**:
```typescript
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { AppComponent } from './app.component';
import { ChatComponent } from './services/chat.component';

@NgModule({
  // Components this module declares
  declarations: [AppComponent, ChatComponent],
  
  // External modules this module uses
  imports: [
    BrowserModule,        // Required to run in browser
    FormsModule,          // Two-way binding (ngModel)
    HttpClientModule      // HTTP requests to backend
  ],
  
  // Services available to all components
  providers: [],
  
  // Component to bootstrap on app startup
  bootstrap: [AppComponent]
})
export class AppModule {}
```

**Why modules**:
- Organization: Group related features
- Lazy loading: Load features only when needed
- Dependency management: Control what's available where
- Testing: Easier to mock dependencies

---

#### 3. **chat.service.ts** - Backend Communication

**What it does**:
- Handles HTTP requests to the backend API
- Manages API communication
- Provides type-safe request/response handling

**Code**:
```typescript
import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';

// Response data structure
export interface ChatResponse {
  answer: string;        // AI-generated answer
  sources: string[];     // Document sources used
}

// Mark as injectable service (can be injected into components)
@Injectable({
  providedIn: 'root'  // Available globally
})
export class ChatService {
  // Use inject() function (Angular 14+ modern way)
  private http = inject(HttpClient);
  
  // Build API URL from environment config
  private API_URL = `${environment.backendUrl}/ask`;

  // Send question to backend
  askQuestion(question: string, sessionId: string): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(this.API_URL, {
      question,
      session_id: sessionId
    });
  }
}
```

**Explanation**:
- `@Injectable`: Makes this class available for dependency injection
- `inject()`: Modern way to get dependencies (replaces constructor)
- `Observable`: Returns a stream of data (handles async operations)
- `post()`: HTTP POST request with automatic JSON serialization

**Request flow**:
```
Component sends question
↓
ChatService.askQuestion()
↓
HTTP POST to backend
↓
Backend processes
↓
Returns Observable<ChatResponse>
↓
Component subscribes to Observable
↓
Response handler updates UI
```

---

#### 4. **chat.component.ts** - Chat Logic

**What it does**:
- Manages the chat interface state and logic
- Handles user input and message display
- Auto-scrolls to latest messages
- Provides modern Angular control flow

**Code Structure**:
```typescript
import { Component, ElementRef, ViewChild, AfterViewChecked, inject } 
  from '@angular/core';
import { ChatService, ChatResponse } from './chat.service';

// Define message structure
interface ChatMessage {
  role: 'user' | 'bot';    // Who sent the message
  text: string;             // Message content
  sources?: string[];       // Document sources (bot only)
  id: string;               // Unique identifier for tracking
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements AfterViewChecked {
  // State
  userInput = '';                              // Text in input box
  messages: ChatMessage[] = [];                // Chat history
  sessionId = Math.random().toString(36).substring(7);  // Unique session
  isLoading = false;                           // Loading indicator
  errorMessage = '';                           // Error display

  // Template references
  @ViewChild('chatMessages') private chatMessagesContainer!: ElementRef;
  @ViewChild('messageInput') private messageInput!: ElementRef;

  // Inject the chat service
  private chatService = inject(ChatService);

  // After every view change, scroll to bottom
  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  // Track messages for *ngFor performance
  trackByMessage(index: number, message: ChatMessage): string {
    return message.id;
  }

  // Send message to backend
  sendMessage() {
    if (!this.userInput.trim() || this.isLoading) {
      return;  // Don't send empty or if already loading
    }

    // Extract question
    const question = this.userInput.trim();
    const messageId = Date.now().toString();

    // Add user message to display
    this.messages.push({
      role: 'user',
      text: question,
      id: messageId
    });

    // Clear input
    this.userInput = '';
    this.errorMessage = '';
    this.isLoading = true;

    // Focus input field after sending
    setTimeout(() => {
      if (this.messageInput) {
        this.messageInput.nativeElement.focus();
      }
    }, 0);

    // Call backend service
    this.chatService.askQuestion(question, this.sessionId).subscribe({
      // Success: add bot response
      next: (res: ChatResponse) => {
        this.messages.push({
          role: 'bot',
          text: res.answer,
          sources: res.sources,
          id: (Date.now() + 1).toString()
        });
      },
      // Error: show error message
      error: (error) => {
        console.error('Chat error:', error);
        this.errorMessage = 'Unable to get an answer from the backend. Please check your connection and try again.';
        this.isLoading = false;
      },
      // Complete: hide loading indicator
      complete: () => {
        this.isLoading = false;
      }
    });
  }

  // Clear error message
  clearError() {
    this.errorMessage = '';
  }

  // Auto-scroll to latest message
  private scrollToBottom(): void {
    try {
      if (this.chatMessagesContainer) {
        this.chatMessagesContainer.nativeElement.scrollTop =
          this.chatMessagesContainer.nativeElement.scrollHeight;
      }
    } catch (err) {
      console.error('Scroll error:', err);
    }
  }
}
```

**Angular Lifecycle**: `AfterViewChecked`
- Called after Angular checks component's view
- Perfect for auto-scrolling (needs DOM to be rendered)

---

#### 5. **chat.component.html** - Chat Template

**What it does**:
- Defines the chat UI structure
- Uses modern Angular control flow (`@for`, `@if`)
- Binds to component properties
- Handles user interactions

**Code Structure**:
```html
<div class="chat-container">
  <!-- Header -->
  <div class="chat-header">
    <h2>ERP Assistant Chat</h2>
    <p>Ask questions about your ERP system</p>
  </div>

  <!-- Messages Area -->
  <div class="chat-messages" #chatMessages>
    <!-- Loop through all messages (modern syntax) -->
    @for (msg of messages; track trackByMessage($index, msg)) {
      <div class="message-wrapper" [ngClass]="msg.role">
        <div class="message-avatar">
          <!-- User icon for user messages -->
          @if (msg.role === 'user') {
            <span class="avatar-icon user-icon">👤</span>
          }
          <!-- Bot icon for bot messages -->
          @else {
            <span class="avatar-icon bot-icon">🤖</span>
          }
        </div>
        <div class="message-content">
          <div class="message-text">{{ msg.text }}</div>
          <!-- Show sources if present -->
          @if (msg.sources?.length) {
            <div class="message-sources">
              <strong>Sources:</strong> {{ msg.sources.join(', ') }}
            </div>
          }
        </div>
      </div>
    }

    <!-- Loading indicator while waiting for response -->
    @if (isLoading) {
      <div class="message-wrapper bot loading">
        <div class="message-avatar">
          <span class="avatar-icon bot-icon">🤖</span>
        </div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    }

    <!-- Welcome message when no messages yet -->
    @if (messages.length === 0 && !isLoading) {
      <div class="welcome-message">
        <div class="welcome-content">
          <h3>Welcome to ERP Assistant! 🤖</h3>
          <p>I'm here to help you with questions about your ERP system.</p>
          <div class="example-questions">
            <p><strong>Example questions:</strong></p>
            <ul>
              <li>How do I process a purchase order?</li>
              <li>What are the inventory management features?</li>
              <li>How to generate financial reports?</li>
            </ul>
          </div>
        </div>
      </div>
    }
  </div>

  <!-- Input Area -->
  <div class="chat-input-container">
    <form (ngSubmit)="sendMessage()" class="chat-form">
      <div class="input-wrapper">
        <!-- Text input -->
        <input
          #messageInput
          [(ngModel)]="userInput"
          name="userInput"
          type="text"
          placeholder="Type your ERP question here..."
          (keyup.enter)="sendMessage()"
          [disabled]="isLoading"
          autocomplete="off"
          maxlength="500"
        />
        <!-- Send button -->
        <button
          type="submit"
          [disabled]="!userInput.trim() || isLoading"
          class="send-button"
          aria-label="Send message">
          @if (!isLoading) {
            <span>Send</span>
          } @else {
            <span class="loading-spinner"></span>
          }
        </button>
      </div>
      <!-- Character counter -->
      <div class="input-footer">
        <small class="character-count">{{ userInput.length }}/500</small>
      </div>
    </form>
  </div>

  <!-- Error display -->
  @if (errorMessage) {
    <div class="error-banner" role="alert">
      <span class="error-icon">⚠️</span>
      <span>{{ errorMessage }}</span>
      <button (click)="clearError()" class="error-close" aria-label="Close error">×</button>
    </div>
  }
</div>
```

**Template Syntax Explained**:

| Syntax | Meaning | Example |
|--------|---------|---------|
| `{{ property }}` | Interpolation: display value | `{{ msg.text }}` |
| `[property]="value"` | Property binding | `[disabled]="isLoading"` |
| `(event)="method()"` | Event binding | `(click)="sendMessage()"` |
| `[(ngModel)]="prop"` | Two-way binding | `[(ngModel)]="userInput"` |
| `@if (condition) { ... }` | Conditional (modern) | `@if (isLoading) { ... }` |
| `@for (item of array) { ... }` | Loop (modern) | `@for (msg of messages) { ... }` |
| `track` | Performance optimization | `track trackByMessage($index, msg)` |

---

#### 6. **chat.component.css** - Responsive Styling

**What it does**:
- Styles the chat interface
- Responsive design (mobile, tablet, desktop)
- Modern animations and gradients
- Accessibility considerations

**Key CSS Classes**:

```css
/* Container: Chat bubble container */
.chat-container {
  width: 100%;
  max-width: 800px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 80vh;
  max-height: 700px;
}

/* Header: Title area with gradient */
.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  text-align: center;
}

/* Messages area: Scrollable container */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #fafbfc;
  scroll-behavior: smooth;
}

/* Message wrapper: Individual message bubble */
.message-wrapper {
  display: flex;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease-in;
}

.message-wrapper.user {
  justify-content: flex-end;  /* Align to right */
}

.message-wrapper.bot {
  justify-content: flex-start; /* Align to left */
}

/* Avatar: User/bot icon */
.avatar-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.bot-icon {
  background: linear-gradient(135deg, #e91e63 0%, #f06292 100%);
  color: white;
}

/* Message content: The actual message */
.message-content {
  max-width: 70%;
  background: white;
  padding: 12px 16px;
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.message-wrapper.user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

/* Input: Text input field */
.chat-input-container {
  border-top: 1px solid #e1e5e9;
  background: white;
  padding: 20px;
}

.input-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-wrapper input {
  flex: 1;
  padding: 14px 18px;
  border: 2px solid #e1e5e9;
  border-radius: 25px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.3s ease;
}

.input-wrapper input:focus {
  border-color: #667eea;
  background: white;
}

/* Send button */
.send-button {
  padding: 14px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 25px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 80px;
}

.send-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.send-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Loading spinner animation */
.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Error banner: Shows at bottom */
.error-banner {
  background: #ffebee;
  border-left: 4px solid #f44336;
  color: #c62828;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
}

/* Responsive: Mobile */
@media (max-width: 768px) {
  .chat-container {
    height: 90vh;
    max-height: none;
    border-radius: 0;
    box-shadow: none;
  }

  .message-content {
    max-width: 85%;  /* Wider messages on mobile */
  }

  .input-wrapper input {
    font-size: 16px;  /* Prevents iOS zoom */
  }
}
```

**Responsive Design Approach**:
- Mobile-first: Base styles work on mobile
- Media queries: Adjust for larger screens
- Flexible layout: Uses flex and percentages
- Touch-friendly: Large buttons and spacing

---

#### 7. **Environment Configuration**

**development** (`environment.ts`):
```typescript
export const environment = {
  production: false,
  backendUrl: 'https://erp-rag-assistant-1.onrender.com/'
};
```

**production** (`environment.prod.ts`):
```typescript
export const environment = {
  production: true,
  backendUrl: 'https://erp-rag-assistant-1.onrender.com/'
};
```

**How Angular uses them**:
- During development: Uses `environment.ts`
- During production build: Replaces with `environment.prod.ts`
- Build process: `ng build --configuration production`

**Why separate configs**:
- Different backend URLs per environment
- Disable debugging in production
- Different feature flags
- Analytics configuration

---

## Data Flow

### Complete Request-Response Cycle

```
1. USER INTERACTION (Frontend)
   ├─ User types question in chat input
   ├─ User presses Enter or clicks Send
   └─ Chat component captures input

2. FRONTEND PROCESSING
   ├─ sendMessage() method triggered
   ├─ Message validation (not empty, not loading)
   ├─ Create ChatMessage object
   ├─ Add message to messages array
   ├─ Update UI (message appears in chat)
   └─ Call ChatService.askQuestion()

3. HTTP REQUEST
   ├─ ChatService.askQuestion() creates HTTP POST
   ├─ URL: environment.backendUrl + "/ask"
   ├─ Body: { question, session_id }
   ├─ Returns Observable (subscription-based)
   └─ Frontend subscribes to receive updates

4. NETWORK TRANSMISSION
   ├─ Request sent over HTTPS
   ├─ Frontend waits (isLoading = true, button disabled)
   ├─ Typing indicator shown in chat
   └─ User can see request is processing

5. BACKEND RECEPTION (Backend)
   ├─ FastAPI receives POST request
   ├─ Validates input using Pydantic model
   ├─ Routes to /ask endpoint
   ├─ Set correlation ID (tracking)
   └─ Retrieve session memory

6. BACKEND PROCESSING - AGENT ROUTE
   ├─ Agent.answer_question() called
   ├─ Planner.plan() evaluates question
   ├─ Planner asks Gemini: "Which tool should I use?"
   ├─ Gemini responds: "rag_search" or "direct_answer"
   ├─ Tool selected and executed
   ├─ Result stored in session memory
   └─ Steps tracked for transparency

7. BACKEND PROCESSING - RAG RETRIEVAL
   ├─ RAGTool calls rag_engine.generate_answer()
   ├─ Retrieval.search() runs:
   │  ├─ Convert question to vector embedding
   │  ├─ Search FAISS index (semantic)
   │  ├─ Search BM25 index (keyword)
   │  ├─ Combine and rank results
   │  └─ Return top 5 documents
   └─ Build context from documents

8. BACKEND PROCESSING - GENERATION
   ├─ RAG Engine builds prompt:
   │  ├─ "Based on: [context]"
   │  ├─ "Answer: [question]"
   │  └─ "Format: clear and concise"
   ├─ Send to Gemini API
   ├─ Gemini generates answer
   ├─ Extract sources from context
   └─ Return Answer object

9. BACKEND RESPONSE
   ├─ Create response JSON:
   │  ├─ answer: "Generated response text"
   │  ├─ sources: ["doc1.pdf", "section2.md"]
   │  └─ steps: [{ action, result }, ...]
   ├─ HTTP 200 OK status
   ├─ Return as JSON
   └─ Log completion

10. NETWORK TRANSMISSION (RESPONSE)
    ├─ Response sent over HTTPS
    ├─ Frontend receives response
    ├─ Observable emits next() event
    └─ Subscription handler called

11. FRONTEND RESPONSE HANDLING
    ├─ next() handler receives ChatResponse
    ├─ Create bot ChatMessage:
    │  ├─ role: "bot"
    │  ├─ text: response.answer
    │  ├─ sources: response.sources
    │  └─ id: unique timestamp
    ├─ Add to messages array
    ├─ Update UI (message appears in chat)
    └─ Set isLoading = false

12. UI UPDATES
    ├─ Chat component detects changes
    ├─ Angular updates DOM
    ├─ New message appears in chat
    ├─ Sources displayed below answer
    ├─ Loading spinner disappears
    ├─ Button re-enabled
    ├─ ngAfterViewChecked triggers
    ├─ Auto-scroll to latest message
    └─ User sees complete answer

13. USER READS AND RESPONDS
    ├─ User sees answer with sources
    ├─ Optionally clicks sources
    ├─ May ask follow-up question
    ├─ Session ID stays same (context preserved)
    └─ Cycle repeats for next question
```

---

## Configuration & Environment

### Environment Variables

**Required**:
- `GEMINI_API_KEY`: Your Google Gemini API key

**Optional**:
- `PORT`: Backend port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)

### Configuration Files

**Backend** (`backend/config.py`):
```python
class Config:
    # Application
    APP_NAME = "ERP RAG Assistant"
    APP_VERSION = "1.0.0"
    
    # API
    API_TIMEOUT = 30
    MAX_QUESTION_LENGTH = 1000
    MAX_SOURCES = 10
    
    # Memory
    MAX_SESSIONS = 1000
    SESSION_TTL_MINUTES = 60
    
    # Retrieval
    RETRIEVAL_TOP_K = 5
    VECTOR_THRESHOLD = 0.7
    
    # Endpoints
    RAG_ENDPOINT = "/ask"
    AGENT_ENDPOINT = "/agent-ask"
```

**Frontend** (`environment.ts` and `environment.prod.ts`):
```typescript
export const environment = {
  production: false|true,
  backendUrl: 'http://localhost:8000|production-url'
};
```

---

## Deployment Architecture

### Development Setup

```
Local Machine (Developer)
│
├─ Backend: localhost:8000
│  └─ pytest for testing
│  └─ nodemon for auto-reload
│
├─ Frontend: localhost:4200
│  └─ ng serve for dev server
│  └─ Hot reload on changes
│
└─ External APIs
   └─ Google Gemini API (free tier)
```

### Production Setup

```
┌─────────────────────────────────────────────────┐
│           PRODUCTION DEPLOYMENT                  │
└─────────────────────────────────────────────────┘

Internet Users
    │
    ├─ Frontend (Vercel CDN)
    │  ├─ Global edge locations
    │  ├─ Automatic SSL
    │  ├─ Auto-scaling
    │  └─ URL: erp-rag-assistant.vercel.app
    │
    ├─ HTTP/HTTPS
    │
    └─ Backend (Render.com)
       ├─ Python 3.10 runtime
       ├─ Auto-deployment from GitHub
       ├─ Environment variables: GEMINI_API_KEY
       └─ URL: erp-rag-api.onrender.com

External Services
    └─ Google Gemini API
       └─ LLM inference
```

### Deployment Process

**Frontend** (Vercel):
1. Push code to GitHub
2. Vercel auto-detects Angular project
3. Runs: `npm run build`
4. Deploys: `dist/erp-rag-frontend/`
5. Auto-HTTPS, CDN caching
6. Automatic rollback on build failure

**Backend** (Render):
1. Push code to GitHub
2. Render detects changes
3. Installs: `pip install -r requirements.txt`
4. Runs: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. Auto-restarts on crash
6. Memory and CPU scaling

---

## Summary

### Key Takeaways

**Architecture**:
- Modern 3-tier: Frontend → Backend → External APIs
- Separation of concerns: UI, Logic, Data
- Scalable: Components independent and replaceable

**Backend (Python/FastAPI)**:
- FastAPI provides automatic routing and validation
- Agent + Planner provide flexible tool orchestration
- RAG Engine handles document retrieval and generation
- Session memory maintains context across questions
- Comprehensive logging for debugging

**Frontend (Angular)**:
- Component-based architecture for reusability
- Services handle backend communication
- Modern control flow for clean templates
- Responsive CSS for all devices
- RxJS Observables for async operations

**Data Flow**:
- Synchronous: Request-response pattern
- Asynchronous: Observables and subscriptions
- Error handling at each layer
- Session context maintained throughout

**Code Quality**:
- ESLint ensures consistent style
- Type safety with TypeScript
- Structured exceptions for debugging
- Comprehensive logging
- Production-ready error handling

---

## Next Steps for Developers

1. **Understand the RAG concept**: Read docs/ERP_AI_Assistant_Documentation.md
2. **Run locally**: Follow SETUP.md
3. **Test endpoints**: Use DEPLOYMENT.md test commands
4. **Add new tools**: Extend tool_registry.py with new tools
5. **Customize prompts**: Modify planner.py and rag_engine.py
6. **Deploy**: Follow DEPLOYMENT.md for Render + Vercel

---

**Last Updated**: May 2026  
**Maintained by**: Development Team  
**Questions?** Check existing documentation or add an issue on GitHub
