#agents.py
#All AI agents — summarise, categorise, extract events, generate replies, score priority, and detect spam.
#Each agent takes clean email text and an optional RAG context string, calls GPT-4o-mini, and returns structured output.
#The router (ai.py) is responsible for calling retrieve_context() and passing the result in as context.

import os
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
