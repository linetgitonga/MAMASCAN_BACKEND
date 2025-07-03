import faiss
import numpy as np
import json
import requests
from django.conf import settings

class FaissIndex:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    def add(self, embeddings, texts):
        self.index.add(np.array(embeddings).astype('float32'))
        self.texts.extend(texts)

    def search(self, query_embedding, top_k=3):
        D, I = self.index.search(np.array([query_embedding]).astype('float32'), top_k)
        return [self.texts[i] for i in I[0]]

def load_data_and_build_index(json_path, azure_endpoint, azure_key, embedding_model, dim):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Flatten all records from all sheets
    texts = []
    for sheet in data.values():
        for item in sheet:
            # Concatenate all values into a single string for embedding
            text = " | ".join(f"{k}: {v}" for k, v in item.items())
            texts.append(text)
    embeddings = [get_azure_embedding(text, azure_endpoint, azure_key, embedding_model) for text in texts]
    index = FaissIndex(dim)
    index.add(embeddings, texts)
    return index



def get_azure_embedding(text, azure_endpoint, azure_key, deployment_name):
    url = f"{azure_endpoint}/openai/deployments/{deployment_name}/embeddings?api-version=2023-05-15"
    headers = {
        "Content-Type": "application/json",
        "api-key": azure_key
    }
    payload = {"input": text}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['data'][0]['embedding']