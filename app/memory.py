class MemoryManager:

    def __init__(self):
        self.sessions = {}

    def get(self, session_id):
        history = self.sessions.get(session_id, [])
        return "\n".join([
            f"User: {h['q']}\nAssistant: {h['a']}"
            for h in history[-5:]
        ])

    def update(self, session_id, q, a):
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        self.sessions[session_id].append({"q": q, "a": a})