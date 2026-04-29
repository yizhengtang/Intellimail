#agents.py
#All AI agents — summarise, categorise, extract events, generate replies, score priority, detect spam, and summarise chats.
#Each agent takes clean text and an optional RAG context string, calls GPT-4o-mini, and returns structured output.
#The router (ai.py) is responsible for calling retrieve_context() and passing the result in as context.

import os
import json
import datetime
from openai import OpenAI

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Summarisation

#Builds the user message for the summarisation prompt.
#Email and context are wrapped in XML tags to clearly separate content from instructions.
#If context is empty the block is omitted — the agent works without RAG context.
def _build_summarise_prompt(email_text: str, context: str) -> str:
    prompt = f"You are a inbox summarization agent,you must read and summarise the following email in 2 to 3 sentences.\n\n<email>\n{email_text}\n</email>"
    if context:
        prompt += f"\n\nUse the following related emails as additional context:\n\n<context>\n{context}\n</context>"
    return prompt

#Summarises an email in 2 to 3 sentences using GPT-4o-mini.
#context is pre-formatted by retrieve_context() in retrieval.py and passed in by the router.
#temperature=0 keeps the output deterministic — summarisation is a factual task, not a creative one.
#max_tokens=150 is a safe ceiling for 2-3 sentences (~80 words) and prevents runaway output.
def summarize_email(email_text: str, context: str = "") -> str:
    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an email summarisation assistant. Summarise emails accurately and concisely. Do not add information that is not present in the email."},
            {"role": "user", "content": _build_summarise_prompt(email_text, context)}
        ],
        temperature=0,
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

#Chat Summarisation

#Summarises a full Teams chat thread accurately without missing or adding any information.
#Unlike email summarisation (2–3 sentences), chat summarisation must cover the full conversation flow.
#max_tokens=300 gives enough room for multi-turn conversations with several topics.
#temperature=0 keeps the output deterministic — summarisation is a factual task, not a creative one.
def summarize_chat(chat_text: str, context: str = "") -> str:
    user_message = f"Summarise the following chat conversation.\n\n<chat>\n{chat_text}\n</chat>"
    if context:
        user_message += f"\n\nUse the following related context as additional background:\n\n<context>\n{context}\n</context>"
    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional chat summarisation assistant. Summarise the chat conversation accurately and completely. Do not miss any information from the chat. Do not add any information that is not in the chat."},
            {"role": "user", "content": user_message}
        ],
        temperature=0,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

#Categorisation

#Builds the user message for the categorisation prompt.
#No context block — the category is determined from the email content alone, no RAG needed.
def _build_categorise_prompt(email_text: str) -> str:
    return f"Categorise the following email.\n\n<email>\n{email_text}\n</email>"

#Categorises an email into one of six fixed categories using GPT-4o-mini.
#RAG is not used — the category is self-contained in the email content.
#max_tokens=10 is tight on purpose — we expect exactly one word back.
#.strip().lower() normalises the response in case the model returns "Work" or "WORK".
def categorize_email(email_text: str) -> str:
    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an email categorisation assistant. Categorise the email into exactly one of these categories: work, personal, promotions, updates, urgent, spam, other. Reply with the category name only. No explanation."},
            {"role": "user", "content": _build_categorise_prompt(email_text)}
        ],
        temperature=0,
        max_tokens=10
    )
    return response.choices[0].message.content.strip().lower()

#Event Extraction

#Extracts events, meetings, dates, deadlines, and action items from an email using GPT-4o-mini.
#RAG is not used — events are explicitly stated in the email, past context does not change them.
#response_format={"type": "json_object"} guarantees valid JSON — without it, GPT sometimes wraps
#the output in markdown code fences which breaks json.loads().
#Returns a list of dicts, each with: type, date (ISO 8601 or empty string), description.
def extract_events(email_text: str) -> list[dict]:
    today = datetime.date.today().isoformat()
    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"You are an event extraction assistant. Today's date is {today}. Use this to resolve relative date references such as 'tomorrow', 'next week', or 'Friday' into exact dates. Extract all events, meetings, dates, deadlines, and action items from the email. Return a JSON object with an 'events' key containing a list of objects. Each object must have exactly these fields: type (one of: meeting, deadline, action_item, reminder), date (if no time: YYYY-MM-DD format. If a time is known: YYYY-MM-DDTHH:MM in 24-hour format. If no date at all: empty string), description (a short description of the event). Do not include seconds or timezone suffixes in the date field."},
            {"role": "user", "content": f"Extract all events from the following email.\n\n<email>\n{email_text}\n</email>"}
        ],
        temperature=0,
        max_tokens=500,
        response_format={"type": "json_object"}
    )
    try:
        result = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return []
    return result.get("events", [])

#Reply Generation

#Generates a draft reply to an email using GPT-4o-mini.
#RAG is used — past emails from the same sender are retrieved to match tone and writing style.
#context is pre-formatted by retrieve_context() in retrieval.py and passed in by the router.
#temperature=0.3 allows natural language variation — a reply should feel human, not mechanically repetitive.
#Returns the draft reply as a plain string ready to be loaded into the compose form.
def generate_reply(email_text: str, context: str = "") -> str:
    user_message = f"Draft a reply to the following email.\n\n<email>\n{email_text}\n</email>"
    if context:
        user_message += f"\n\nUse the following past emails to match the tone and writing style of the replies:\n\n<context>\n{context}\n</context>"
    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an email reply assistant. Draft a professional and concise reply to the email. If context from past emails is provided, match the tone and writing style. Only reply to what was asked — do not add unnecessary content."},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

#Priority Scoring

#Scores the urgency of an email on a scale of 1 to 5 using GPT-4o-mini.
#RAG is used — past emails from the same sender help identify urgency patterns.
#Fallback score is 3 (normal) — safer than marking everything urgent or low priority.
#response_format={"type": "json_object"} guarantees valid JSON output.
def score_priority(email_text: str, context: str = "") -> dict:
    user_message = f"Score the priority of the following email.\n\n<email>\n{email_text}\n</email>"
    if context:
        user_message += f"\n\nUse the following past emails from the same sender as context:\n\n<context>\n{context}\n</context>"
    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an email priority scoring assistant. Score the urgency of the email on a scale of 1 to 5 using these criteria: 5 = urgent, immediate action required; 4 = high priority, action needed soon; 3 = normal, action needed but not time-sensitive; 2 = low priority, informational only; 1 = no action needed, promotional or newsletter. Return a JSON object with: score (integer 1–5), reason (one sentence explaining the score)."},
            {"role": "user", "content": user_message}
        ],
        temperature=0,
        max_tokens=100,
        response_format={"type": "json_object"}
    )
    result = json.loads(response.choices[0].message.content)
    return {"score": result.get("score", 3), "reason": result.get("reason", "")}

#Batch Summarisation

#Summarises multiple emails in a single GPT call — used by the chat agent for summarize_inbox.
#Receives a list of email dicts returned by get_latest_emails() in vector_store.py.
#Each dict has a "document" key (the full indexed text) and metadata keys (subject, from, date).
#One GPT call for all emails is cheaper and faster than calling summarize_email() per email.
def batch_summarize(emails: list[dict]) -> str:
    if not emails:
        return "No emails found in your knowledge base. Please sync your inbox first."

    blocks = []
    for i, email in enumerate(emails, start=1):
        subject = email.get("subject", "No subject")
        sender = email.get("from", "Unknown")
        date = email.get("date", "")
        text = email.get("document", "")
        blocks.append(f"Email {i}:\nFrom: {sender} | Date: {date} | Subject: {subject}\n{text[:500]}")

    combined = "\n\n".join(blocks)
    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an inbox summarisation assistant. Summarise each email in 1 to 2 sentences. Present them as a numbered list. Be concise and professional."},
            {"role": "user", "content": f"Summarise the following emails:\n\n{combined}"}
        ],
        temperature=0,
        max_tokens=600
    )
    return response.choices[0].message.content.strip()

#Context-Aware Answer

#Answers a user's question using retrieved email context from ChromaDB.
#Used by the chat agent for find_email and general_question intents.
#history is the recent conversation — passed so the answer can reference prior turns.
#temperature=0.3 allows natural variation — answers should feel conversational, not robotic.
def answer_with_context(message: str, context: str, history: list[dict]) -> str:
    user_message = message
    if context:
        user_message += f"\n\nRelevant emails from your inbox:\n\n{context}"
    else:
        user_message += "\n\nNo relevant emails were found in your inbox for this query."

    messages = [{"role": "system", "content": "You are a professional personal inbox assistant. Answer questions about the user's emails accurately and concisely. Only use information from the provided email context. If the context does not contain enough information to answer, say so clearly."}]
    messages += history
    messages.append({"role": "user", "content": user_message})

    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=400
    )
    return response.choices[0].message.content.strip()

#Spam Detection

#Detects whether an email is spam or unwanted promotional content using GPT-4o-mini.
#RAG is not used — spam detection is based on patterns in the current email alone.
#Fallback is_spam=False — safer to leave a spam email in the inbox than to hide a real one.
#response_format={"type": "json_object"} guarantees valid JSON output.
def is_spam(email_text: str) -> dict:
    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a spam detection assistant. Determine whether the email is spam or unwanted promotional content. Consider as spam: mass marketing, phishing attempts, unsolicited newsletters, prize or lottery scams, and bulk promotional emails. Do not consider as spam: personal emails, work emails, and relevant transactional emails. Return a JSON object with: is_spam (boolean), confidence (float between 0.0 and 1.0)."},
            {"role": "user", "content": f"Determine if the following email is spam.\n\n<email>\n{email_text}\n</email>"}
        ],
        temperature=0,
        max_tokens=50,
        response_format={"type": "json_object"}
    )
    result = json.loads(response.choices[0].message.content)
    return {"is_spam": result.get("is_spam", False), "confidence": result.get("confidence", 0.0)}
