class SessionMemory:
    def __init__(self):
        self.sessions = {}

    def get(self, session_id):
        return self.sessions.get(session_id)

    def create(self, session_id):
        self.sessions[session_id] = {
            "query": "",
            "answer": None,
            "evidence": [],
            "citations": [],
            "version": 0
        }

        return self.sessions[session_id]

    def update(
        self,
        session_id,
        query=None,
        answer=None,
        evidence=None,
        citations=None
    ):
        if session_id not in self.sessions:
            self.create(session_id)

        session = self.sessions[session_id]

        if query is not None:
            session["query"] = query

        if answer is not None:
            session["answer"] = answer

        if evidence is not None:
            session["evidence"] = evidence

        if citations is not None:
            session["citations"] = citations

        session["version"] += 1

        return session