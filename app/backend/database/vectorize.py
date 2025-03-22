# Vectorize.py
# Description: Module to vectorize text data using BERT embeddings.

import numpy as np
import torch
from tqdm import tqdm

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output.last_hidden_state
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def encode(text, model, tokenizer):
    # Tokenize sentences
    encoded_input = tokenizer(text, padding=True, truncation=True, return_tensors='pt', max_length=512)

    # Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input, return_dict=True)

    # Perform pooling
    embedding = mean_pooling(model_output, encoded_input['attention_mask'])
    
    return embedding


def get_embedding_matrix(chunks, model, tokenizer):
    """Retourne une matrice d'embedding BERT pour une liste de textes."""
    
    embedding_matrix = []
    for text in tqdm(chunks, desc="Processing embeddings"):
        embedding_matrix.append(encode(text, model, tokenizer))

    return np.vstack(embedding_matrix)