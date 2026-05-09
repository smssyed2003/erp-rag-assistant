[1mdiff --git a/backend/.env b/backend/.env[m
[1mindex 6a407046..1d9f05ff 100644[m
[1m--- a/backend/.env[m
[1m+++ b/backend/.env[m
[36m@@ -1 +1 @@[m
[31m-GEMINI_API_KEY="AIzaSyArMfXYc1obd5I9NdzYGO34vu5VGclx5k4"[m
\ No newline at end of file[m
[32m+[m[32mGEMINI_API_KEY="AIzaSyCOUMBedgeh2Zh3OoeO0goY69UAw5OTLfg"[m
\ No newline at end of file[m
[1mdiff --git a/backend/app/__pycache__/__init__.cpython-310.pyc b/backend/app/__pycache__/__init__.cpython-310.pyc[m
[1mindex dab456b4..5355ca02 100644[m
Binary files a/backend/app/__pycache__/__init__.cpython-310.pyc and b/backend/app/__pycache__/__init__.cpython-310.pyc differ
[1mdiff --git a/backend/app/__pycache__/main.cpython-310.pyc b/backend/app/__pycache__/main.cpython-310.pyc[m
[1mindex a8a8aa9b..f38680ed 100644[m
Binary files a/backend/app/__pycache__/main.cpython-310.pyc and b/backend/app/__pycache__/main.cpython-310.pyc differ
[1mdiff --git a/backend/app/__pycache__/memory.cpython-310.pyc b/backend/app/__pycache__/memory.cpython-310.pyc[m
[1mindex 4013ab5d..05133ece 100644[m
Binary files a/backend/app/__pycache__/memory.cpython-310.pyc and b/backend/app/__pycache__/memory.cpython-310.pyc differ
[1mdiff --git a/backend/app/__pycache__/rag_engine.cpython-310.pyc b/backend/app/__pycache__/rag_engine.cpython-310.pyc[m
[1mindex 732f2b80..af740774 100644[m
Binary files a/backend/app/__pycache__/rag_engine.cpython-310.pyc and b/backend/app/__pycache__/rag_engine.cpython-310.pyc differ
[1mdiff --git a/backend/app/__pycache__/retrieval.cpython-310.pyc b/backend/app/__pycache__/retrieval.cpython-310.pyc[m
[1mindex 3eb81d11..235576de 100644[m
Binary files a/backend/app/__pycache__/retrieval.cpython-310.pyc and b/backend/app/__pycache__/retrieval.cpython-310.pyc differ
[1mdiff --git a/backend/app/__pycache__/utils.cpython-310.pyc b/backend/app/__pycache__/utils.cpython-310.pyc[m
[1mindex 1a77b2f8..ff538580 100644[m
Binary files a/backend/app/__pycache__/utils.cpython-310.pyc and b/backend/app/__pycache__/utils.cpython-310.pyc differ
[1mdiff --git a/backend/app/main.py b/backend/app/main.py[m
[1mindex 74d8bccd..f85f6d8b 100644[m
[1m--- a/backend/app/main.py[m
[1m+++ b/backend/app/main.py[m
[36m@@ -6,6 +6,7 @@[m [mfrom dotenv import load_dotenv[m
 from app.logger import logger[m
 import os[m
 from app.rag_engine import RAGEngine[m
[32m+[m[32mfrom app.agent import Agent[m
 [m
 load_dotenv()[m
 [m
[36m@@ -23,16 +24,18 @@[m [mapp.add_middleware([m
 )[m
 [m
 rag = None[m
[32m+[m[32magent = None[m
 [m
 @app.on_event("startup")[m
 def startup_event():[m
[31m-    global rag[m
[32m+[m[32m    global rag, agent[m
     logger.info("Starting ERP RAG API...")[m
 [m
     try:[m
         logger.info(f"GEMINI_API_KEY present: {bool(os.getenv('GEMINI_API_KEY'))}")[m
         rag = RAGEngine()[m
[31m-        logger.info("RAG Engine initialized successfully")[m
[32m+[m[32m        agent = Agent(rag)[m
[32m+[m[32m        logger.info("RAG Engine and Agent initialized successfully")[m
     except Exception as e:[m
         logger.exception("Failed during startup")[m
         raise e[m
[36m@@ -58,4 +61,34 @@[m [mdef ask(q: Query):[m
 [m
     except Exception as e:[m
         logger.exception("Error during /ask")[m
[31m-        return {"error": str(e)}[m
\ No newline at end of file[m
[32m+[m[32m        return {"error": str(e)}[m
[32m+[m
[32m+[m[32m@app.post("/agent-ask")[m
[32m+[m[32mdef agent_ask(q: Query):[m
[32m+[m[32m    logger.info(f"Incoming agent query | session={q.session_id} | question={q.question}")[m
[32m+[m
[32m+[m[32m    try:[m
[32m+[m[32m        if not agent:[m
[32m+[m[32m            raise RuntimeError("Agent is not initialized")[m
[32m+[m
[32m+[m[32m        response = agent.run(q.question, q.session_id)[m
[32m+[m[32m        logger.info("Agent response generated successfully")[m
[32m+[m
[32m+[m[32m        return {[m
[32m+[m[32m            "answer": response.get("answer", ""),[m
[32m+[m[32m            "steps": response.get("steps", [