# query_data.py

import os
import argparse
import markdown2
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

import numpy as np
# from dataclasses import dataclass
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import faiss

from backend.database.vectorize import encode


# Constants

FAISS_PATH = "./backend/FAISS"

PROMPT_TEMPLATE = """
Vous êtes un assistant qui répond aux questions basées sur le contexte suivant :

{context}

--------------------------------------------

Historique du chat :
{history}

Question :
{question}

Répondez à la question en vous basant uniquement sur le contexte et l'historique fournis.
"""


def query_database_agent(query_text= None, model_embedding = None, tokenizer_embedding = None, tokenizer_chat= None, model_chat= None, chat_history= None):
    
    # Load the index and the chunks
    index = faiss.read_index(f"{FAISS_PATH}/index.faiss")
    with open(f"{FAISS_PATH}/chunks.json", "r") as f:
        chunks = json.load(f)
    print("Index and chunks loaded.")

    # Encode the query
    query_vector = encode_query(query_text, model_embedding, tokenizer_embedding)
    print("Query encoded.")
    
    # Search the KNN
    indices = search_knn(index, query_vector, len(chunks), k=3)
    print("KNN search done.")

     # Construire le contexte avec l'historique du chat
    history_text = ""
    if chat_history:
        for msg in chat_history:
            if msg['sender'] == 'user':
                history_text += f"Utilisateur : {msg['question']}\n"
            elif msg['sender'] == 'assistant':
                history_text += f"Assistant : {msg['answer']}\n"

    context_text = "\n----------------------------------------------\n\n".join(
        [chunks[i] for i in indices]
    )

    # Generate the prompt
    prompt = PROMPT_TEMPLATE.format(context=context_text, history=history_text, question=query_text)
    
    # Generate the answer
    payload = {
        "model": "tinyllama",
        "prompt": prompt
    }
    response = requests.post(OLLAMA_URL, json=payload)
    print("Answer generated.")
    
    return response.json()["response"]
   

def encode_query(query, model_embedding=None, tokenizer_embedding=None):
    """Encode une requête en utilisant un modèle d'embedding."""
    query_encoded = model_embedding.encode(query, model_embedding= model_embedding, tokenizer_embedding=tokenizer_embedding)
    return np.array(query_encoded, dtype=np.float32).reshape(1, -1)  # Transformer en 2D

def search_knn(index, query_vector, n, k=3):
    """Effectue une recherche KNN dans FAISS."""
    distances, indices = index.search(query_vector, k)
    return get_adjacent_numbers(indices[0], n)  # Retourne les indices des passages les plus pertinents

def get_adjacent_numbers(numbers, n):
    """Prend une liste de x entiers et retourne ces entiers avec leurs voisins adjacents entre 0 et n."""
    result = set()
    
    for num in numbers:
        for i in range(-1, 2):  # Prend l'élément, son précédent et son suivant
            new_num = num + i
            if 0 <= new_num <= n-1:  # Vérifier que c'est dans les bornes
                result.add(new_num)
    
    return sorted(result)


if __name__ == "__main__":
    main()