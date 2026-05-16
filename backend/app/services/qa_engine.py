"""
Q&A Engine with RAG (Retrieval Augmented Generation)
"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database import QAHistory, GraphNode
from app.services.embedding_service import embedding_service
from app.services.watsonx_client import watsonx_client


class QAEngine:
    """Q&A Engine using RAG for code understanding"""

    def __init__(self):
        self.max_context_chunks = 5
        self.max_history = 10

    def _build_context(self, code_chunks: List[Dict[str, Any]]) -> str:
        """Build a formatted context string from retrieved code chunks."""
        if not code_chunks:
            return "No relevant code found."

        parts = []
        for i, chunk in enumerate(code_chunks, 1):
            parts.append(
                f"### Snippet {i} — `{chunk['file_path']}`\n"
                f"```\n{chunk['code_chunk']}\n```"
            )
        return "\n\n".join(parts)

    def _build_messages(
        self,
        question: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> List[Dict[str, str]]:
        """
        Build the chat messages list for llama-3-3-70b-instruct.
        """
        system_content = (
            "You are an expert code assistant. "
            "Your job is to answer questions about a software codebase accurately and concisely. "
            "Use only the provided code snippets as your source of truth. "
            "Always reference specific files when you cite code. "
            "If the snippets do not contain enough information to answer the question, say so clearly."
        )

        # Compose the user message
        user_parts = []

        if conversation_history:
            user_parts.append("## Recent conversation history")
            for qa in conversation_history[-3:]:
                user_parts.append(f"**Q:** {qa['question']}\n**A:** {qa['answer']}")
            user_parts.append("")

        user_parts.append("## Relevant code snippets from the repository")
        user_parts.append(context)
        user_parts.append(f"\n## Question\n{question}")

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": "\n\n".join(user_parts)},
        ]
        return messages

    def _generate_suggested_questions(
        self,
        db: Session,
        project_id: int,
    ) -> List[str]:
        fallbacks = [
            "How is the project structured?",
            "What are the main entry points?",
            "How does error handling work?",
            "What external dependencies are used?",
        ]

        nodes = (
            db.query(GraphNode)
            .filter(
                GraphNode.project_id == project_id,
                GraphNode.node_type.in_(["function", "class", "method"]),
            )
            .order_by(GraphNode.importance_score.desc())
            .limit(20)
            .all()
        )

        if len(nodes) < 4:
            return fallbacks

        suggestions = []
        seen = set()
        top_functions = [n for n in nodes if n.node_type in ("function", "method")]

        for node in nodes:
            if node.node_type == "class":
                q = f"What is the `{node.name}` class responsible for?"
            else:
                q = f"What does the `{node.name}` function do?"
            if q not in seen:
                suggestions.append(q)
                seen.add(q)

        for node in top_functions[:3]:
            q = f"Where is `{node.name}` defined and what does it return?"
            if q not in seen:
                suggestions.append(q)
                seen.add(q)

        # Pad with fallbacks if needed
        for fb in fallbacks:
            if len(suggestions) >= 8:
                break
            if fb not in seen:
                suggestions.append(fb)

        return suggestions[:8]

    def ask_question(
        self,
        db: Session,
        project_id: int,
        question: str,
        include_history: bool = True,
    ) -> Dict[str, Any]:
        """
        Answer a question about the codebase using RAG:
          1. Embed the question with granite-embedding-278m-multilingual
          2. Retrieve top-k similar code chunks via cosine similarity
          3. Generate an answer with llama-3-3-70b-instruct via chat API
        """
        try:
            # Step 1 — retrieve relevant code chunks
            code_chunks = embedding_service.search_similar_code(
                db=db,
                project_id=project_id,
                query=question,
                top_k=self.max_context_chunks,
            )

            print(f"\n{'='*80}")
            print(f"DEBUG: Question: {question}")
            print(f"DEBUG: Code chunks found: {len(code_chunks)}")
            print(f"{'='*80}\n")

            if not code_chunks:
                print("WARNING: No code chunks found — embeddings may not be generated")
                return {
                    'answer': (
                        "⚠️ No code embeddings found for this project. "
                        "Please click the '🔄 Generate Embeddings' button first to enable Q&A."
                    ),
                    'code_snippets': [],
                    'confidence': 0.0,
                    'timestamp': None,
                }

            # Step 2 — build context and retrieve conversation history
            context = self._build_context(code_chunks)

            conversation_history = None
            if include_history:
                history = (
                    db.query(QAHistory)
                    .filter(QAHistory.project_id == project_id)
                    .order_by(QAHistory.created_at.desc())
                    .limit(self.max_history)
                    .all()
                )
                conversation_history = [
                    {'question': h.question, 'answer': h.answer}
                    for h in reversed(history)
                ]

            # Step 3 — build chat messages and call llama-3-3-70b
            messages = self._build_messages(question, context, conversation_history)

            print(f"DEBUG: Context length: {len(context)}")
            print(f"DEBUG: System message (first 200 chars): {messages[0]['content'][:200]}")

            try:
                answer = watsonx_client.chat(
                    messages=messages,
                    max_tokens=1024,
                    temperature=0.3,
                )
                print(f"DEBUG: Generated answer length: {len(answer)}")
                print(f"DEBUG: Answer preview: {answer[:200]}...")

                if not answer or len(answer.strip()) < 10:
                    raise ValueError("Generated answer is too short or empty")
                if answer.strip().lower() == question.strip().lower():
                    raise ValueError("Generated answer is identical to the question")

            except Exception as gen_error:
                print(f"ERROR: Failed to generate answer: {gen_error}")
                answer = (
                    "I apologize, but I encountered an error while generating an answer.\n\n"
                    "**Possible issues:**\n"
                    "1. Watsonx.ai credentials may not be properly configured\n"
                    "2. The AI model may be unavailable\n"
                    "3. Network connectivity issues\n\n"
                    f"**Error details:** {str(gen_error)}\n\n"
                    "**Suggestion:** Please check your `.env` file and ensure "
                    "`WATSONX_API_KEY` and `WATSONX_PROJECT_ID` are set correctly."
                )

            avg_similarity = (
                sum(c['similarity'] for c in code_chunks) / len(code_chunks)
                if code_chunks else 0.0
            )

            qa_entry = QAHistory(
                project_id=project_id,
                question=question,
                answer=answer,
                context_used=context,
            )
            db.add(qa_entry)
            db.commit()

            return {
                'answer': answer,
                'code_snippets': [
                    {
                        'file_path': c['file_path'],
                        'code': c['code_chunk'],
                        'similarity': c['similarity'],
                    }
                    for c in code_chunks
                ],
                'confidence': avg_similarity,
                'timestamp': qa_entry.created_at.isoformat(),
            }

        except Exception as e:
            print(f"Error in ask_question: {e}")
            return {
                'answer': f"I encountered an error while processing your question: {str(e)}",
                'code_snippets': [],
                'confidence': 0.0,
                'timestamp': None,
            }

    def get_conversation_history(
        self,
        db: Session,
        project_id: int,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        history = (
            db.query(QAHistory)
            .filter(QAHistory.project_id == project_id)
            .order_by(QAHistory.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                'id': h.id,
                'question': h.question,
                'answer': h.answer,
                'timestamp': h.created_at.isoformat(),
            }
            for h in reversed(history)
        ]

    def get_suggested_questions(
        self,
        db: Session,
        project_id: int,
    ) -> List[str]:
        return self._generate_suggested_questions(db, project_id)


# Global engine instance
qa_engine = QAEngine()

# Made with Bob
