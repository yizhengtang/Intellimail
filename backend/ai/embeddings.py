import os
from openai import OpenAI

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Calls the OpenAI embedding API and returns a list of 1536 floats.
#The returned vector encodes the semantic meaning of the text as coordinates in 1536-dimensional space.
def embed_text(text: str) -> list[float]:
    response = _client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding
