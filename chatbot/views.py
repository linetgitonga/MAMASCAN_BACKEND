import os
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from .faiss_utils import load_data_and_build_index

from openai import AzureOpenAI

# Embedding model credentials (for vector search)
EMBED_ENDPOINT = os.getenv("AZURE_EMBED_ENDPOINT")
EMBED_KEY = os.getenv("AZURE_EMBED_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
EMBEDDING_API_VERSION = os.getenv("EMBEDDING_API_VERSION")

# Chat model credentials (for completions)
CHAT_ENDPOINT = os.getenv("AZURE_CHAT_ENDPOINT")
CHAT_KEY = os.getenv("AZURE_CHAT_KEY")
CHAT_DEPLOYMENT = os.getenv("CHAT_MODEL")
CHAT_API_VERSION = os.getenv("API_VERSION")

INDEX_DIM = 1536
JSON_PATH = os.path.join(os.path.dirname(__file__), "data", "clinical_data.json")

def get_azure_embedding(text):
    url = f"{EMBED_ENDPOINT}/openai/deployments/{EMBEDDING_MODEL}/embeddings?api-version={EMBEDDING_API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "api-key": EMBED_KEY
    }
    payload = {"input": text}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['data'][0]['embedding']

faiss_index = load_data_and_build_index(JSON_PATH, EMBED_ENDPOINT, EMBED_KEY, EMBEDDING_MODEL, INDEX_DIM)

# Initialize AzureOpenAI client for chat
chat_client = AzureOpenAI(
    api_version=CHAT_API_VERSION,
    azure_endpoint=CHAT_ENDPOINT,
    api_key=CHAT_KEY,
)

def generate_azure_answer(query, docs):
    system_prompt = "You are a helpful assistant."
    user_prompt = f"Context: {' '.join(docs)}\n\nQuestion: {query}\nAnswer:"
    response = chat_client.chat.completions.create(
        stream=False,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_completion_tokens=800,
        temperature=1.0,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        model=CHAT_DEPLOYMENT,
    )
    return response.choices[0].message.content.strip()

class ChatbotAPIView(APIView):
    def post(self, request):
        user_query = request.data.get("query")
        embedding = get_azure_embedding(user_query)
        docs = faiss_index.search(embedding)
        answer = generate_azure_answer(user_query, docs)
        return Response({"answer": answer})