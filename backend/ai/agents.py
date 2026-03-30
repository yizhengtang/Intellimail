#agents.py
#All AI agents — summarise, categorise, extract events, generate replies, score priority, and detect spam.
#Each agent takes clean email text and an optional RAG context string, calls GPT-4o-mini, and returns structured output.
#The router (ai.py) is responsible for calling retrieve_context() and passing the result in as context.

import os
import json
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
    response = _client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an event extraction assistant. Extract all events, meetings, dates, deadlines, and action items from the email. Return a JSON object with an 'events' key containing a list of objects. Each object must have: type (one of: meeting, deadline, action_item, reminder), date (ISO 8601 format, or empty string if not specified), description (a short description of the event)."},
            {"role": "user", "content": f"Extract all events from the following email.\n\n<email>\n{email_text}\n</email>"}
        ],
        temperature=0,
        max_tokens=500,
        response_format={"type": "json_object"}
    )
    result = json.loads(response.choices[0].message.content)
    return result.get("events", [])
