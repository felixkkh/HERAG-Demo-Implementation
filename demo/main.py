from dotenv import load_dotenv
load_dotenv()

import signal

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from .chain.state import RAGState
from .chain.retrieve import retrieve

from .chain.generate import generate
from .chain.rerank import rerank
import sys


def setup_signal_handlers():
  def signal_handler(sig, frame):
    print("\nGoodbye!")
    exit(0)
  
  signal.signal(signal.SIGINT, signal_handler)
  signal.signal(signal.SIGTERM, signal_handler)


def build_graph():
  graph = StateGraph(RAGState)
  graph.add_node("retrieve", RunnableLambda(retrieve))
  graph.add_node("rerank", RunnableLambda(rerank))
  graph.add_node("generate", RunnableLambda(generate))
  graph.add_edge("retrieve", "rerank")
  graph.add_edge("rerank", "generate")
  graph.add_edge("generate", END)
  graph.set_entry_point("retrieve")
  return graph.compile()

# Singleton for the compiled chain
_app = None
def get_chain():
  global _app
  if _app is None:
    _app = build_graph()
  return _app

def run_chain(question, history=None):
  """Call the RAG chain with a question and optional history."""
  if history is None:
    history = []
  app = get_chain()
  return app.invoke({"question": question, "history": history})


def main():
  setup_signal_handlers()

  # If --import is passed, run ingest instead of chatbot
  if len(sys.argv) > 1 and sys.argv[1] == "--import":
    from .ingest import ingest
    ingest()
    return

  # Welcome message
  print("Welcome to the RAG terminal chat! Type 'exit' to quit or press Ctrl+C.")

  # In-memory chat history
  history: list[dict] = []

  while True:
    # Print user prompt
    question = input("You: ")

    # Allow to exit
    if question.strip().lower() in ["exit", "quit"]:
      print("Goodbye!")
      break
        
    # Invoke the chain
    result = run_chain(question, history)

    docs = result.get("docs", [])
    chunk_ids = []
    if docs:
      for i, doc in enumerate(docs):
        chunk_id = getattr(doc, 'metadata', {}).get('id', f"chunk_{i+1}")
        chunk_ids.append(str(chunk_id))

    # Get the answer
    answer = result["answer"]
    answer_text = getattr(answer, 'content', answer)

    # Print bot response with all chunk ids
    if chunk_ids:
      print(f"Bot: {answer_text} ({', '.join(chunk_ids)})")
    else:
      print(f"Bot: {answer_text}")

    # Update state with new history for next turn
    history = result.get("history", history)


if __name__ == "__main__":
  main()
