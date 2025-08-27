from ..model_provider import get_llm


def generate(state):
    docs = state["docs"]
    question = state["question"]
    history = state.get("history", [])
    context = "\n".join([doc.page_content for doc in docs])
    history_str = "\n".join([
        f"User: {turn['question']}\nBot: {turn['answer']}" for turn in history
    ]) if history else ""
    prompt = f"# Context:\n{context}\n# Conversation History:\n{history_str}\n# Question: {question}\nAnswer:"
    answer = get_llm().invoke(prompt)
    # Append latest turn to history
    new_history = history + [{"question": question, "answer": getattr(answer, 'content', answer)}]
    return {"answer": answer, "history": new_history}
