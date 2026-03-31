#chat.py
#Orchestrates the AI chat interface — classifies user intent and routes to the correct agent.
#ChromaDB is the ONLY knowledge base — all AI responses are grounded in indexed emails.
#Maximum 2 GPT calls per user message: one to classify intent, one to execute.

import os
import json
from openai import OpenAI
from .vector_store import get_latest_emails
from .retrieval import retrieve_context
from .agents import batch_summarize, generate_reply, answer_with_context

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Four intents cover every chat use case in this project.
#general_question is the catch-all — no valid message is left unhandled.
INTENTS = ["summarize_inbox", "find_email", "compose_reply", "general_question"]

#Classifies the user's message into one of four intents.
#Also extracts a clean search query from the conversational message — better input for RAG
#than passing the raw message (e.g. "what did Alice say?" → "emails from Alice").
#history is capped at 6 messages (3 turns) to keep token cost flat across long conversations.
#Falls back to general_question if the model returns an unrecognised intent.
def _classify_intent(message: str, history: list[dict]) -> dict:
    system = (
        "You are an inbox assistant intent classifier. "
        "Classify the user message into exactly one of these intents:\n"
        "- summarize_inbox: user wants a summary or overview of their recent emails\n"
        "- find_email: user wants to find or look up a specific email or information from emails\n"
        "- compose_reply: user wants to draft or write a reply to an email\n"
        "- general_question: any other question about the inbox or emails\n\n"
        "Return a JSON object with:\n"
        "- intent: one of the four intents above\n"
        "- query: a clean concise search query extracted from the message, useful for semantic search"
    )
    messages = [{"role": "system", "content": system}]
    messages += history[-6:]
    messages.append({"role": "user", "content": message})

    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
        max_tokens=80,
        response_format={"type": "json_object"}
    )
    result = json.loads(response.choices[0].message.content)
    intent = result.get("intent", "general_question")
    if intent not in INTENTS:
        intent = "general_question"
    return {"intent": intent, "query": result.get("query", message)}

#Fetches the 10 most recently indexed emails from ChromaDB and summarises them all in one call.
#Returns an empty-state message if the vector store has not been populated yet.
def _handle_summarize_inbox() -> str:
    emails = get_latest_emails(k=10)
    if not emails:
        return "Your inbox has not been synced yet. Please press Sync Inbox to enable AI features."
    return batch_summarize(emails)

#Retrieves the 5 most semantically relevant emails for the query and answers the question.
def _handle_find_email(query: str, history: list[dict]) -> str:
    context = retrieve_context(query, k=5)
    if not context:
        return "No relevant emails were found. Please sync your inbox first or try a different search."
    return answer_with_context(query, context, history)

#Retrieves relevant past emails for style and context, then generates a draft reply.
def _handle_compose_reply(query: str, history: list[dict]) -> str:
    context = retrieve_context(query, k=3)
    return generate_reply(query, context)

#Retrieves the 5 most relevant emails as context and answers a general inbox question.
def _handle_general_question(query: str, history: list[dict]) -> str:
    context = retrieve_context(query, k=5)
    if not context:
        return "No relevant emails were found. Please sync your inbox first or try a different question."
    return answer_with_context(query, context, history)

#Public entry point — called by the FastAPI chat endpoint.
#Accepts the user's message and the full conversation history.
#Returns the AI response as a plain string ready to display in the chat interface.
def chat_response(message: str, history: list[dict]) -> str:
    if not message.strip():
        return "Please enter a message."

    classification = _classify_intent(message, history)
    intent = classification["intent"]
    query = classification["query"]

    #History is capped here before passing to handlers so all downstream calls are consistent.
    recent_history = history[-6:]

    if intent == "summarize_inbox":
        return _handle_summarize_inbox()
    elif intent == "find_email":
        return _handle_find_email(query, recent_history)
    elif intent == "compose_reply":
        return _handle_compose_reply(query, recent_history)
    else:
        return _handle_general_question(query, recent_history)
