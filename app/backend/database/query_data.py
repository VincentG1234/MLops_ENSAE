# query_data.py

import os
import argparse
import markdown2
import json
import requests

# Set the environment variable to avoid OpenMP runtime conflict
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

OLLAMA_URL = "http://localhost:11434/api/generate"

import numpy as np
# from dataclasses import dataclass
from langchain.prompts import ChatPromptTemplate
import faiss

from backend.database.vectorize import encode


# Constants

FAISS_PATH = "./backend/FAISS"

PROMPT_TEMPLATE = """
Vous êtes un assistant qui répond aux questions basées sur le contexte suivant :

{context}

--------------------------------------------

Question :
{question}

Répondez à la question en vous basant uniquement sur le contexte et l'historique fournis.
"""


def query_database_agent(query_text= None, model_embedding = None, tokenizer_embedding = None, chat_history= None):
    
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
    print( "Prompt generated:", prompt)
    
    # Generate the answer
    payload = {
        "model": "tinyllama",
        "prompt": prompt,
        "max_tokens": 250,
    }
    response = requests.post(OLLAMA_URL, json=payload, stream=True)
    print("Answer generated.")
    print("Response:", response)
    answer = format_response(response)
    print("Answer:", answer)
    return answer
   

def encode_query(query, model_embedding=None, tokenizer_embedding=None):
    """Encode une requête en utilisant un modèle d'embedding."""
    query_encoded = encode(query, model_embedding, tokenizer_embedding)
    return np.array(query_encoded, dtype=np.float32).reshape(1, -1)  # Transformer en 2D

def search_knn(index, query_vector, n, k=3):
    """Effectue une recherche KNN dans FAISS."""
    distances, indices = index.search(query_vector, k)
    return indices[0]  # Retourne les indices des passages les plus pertinents

def get_adjacent_numbers(numbers, n):
    """Prend une liste de x entiers et retourne ces entiers avec leurs voisins adjacents entre 0 et n."""
    result = set()
    
    for num in numbers:
        for i in range(-1, 2):  # Prend l'élément, son précédent et son suivant
            new_num = num + i
            if 0 <= new_num <= n-1:  # Vérifier que c'est dans les bornes
                result.add(new_num)
    
    return sorted(result)

def format_response(response):
    # Initialize a variable to store the final response
    final_response = ""

    # Process the stream of JSON objects
    for line in response.iter_lines():
        if line:
            try:
                json_object = json.loads(line)
                if json_object.get("done", False):
                    final_response = json_object["response"]
                    break
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                print("Line content is not valid JSON:", line)
    return final_response
