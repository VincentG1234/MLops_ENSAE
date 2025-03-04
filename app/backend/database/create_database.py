# create_database.py
import os

import numpy as np
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader

import json
import faiss
import sqlite3
import tiktoken
import nltk
nltk.download("punkt")
from nltk.tokenize import sent_tokenize
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
from backend.database.vectorize import get_embedding_matrix

FAISS_PATH = "./backend/FAISS"
DATA_PATH = "./backend/uploads"

def main():
    generate_data_store()

def generate_data_store():
    documents = load_documents()
    print("document load for generate database")

    chunks = split_text(documents)
    print("chunks done")

    chunks_vectorized = get_embedding_matrix(chunks, model, tokenizer)

    save_to_faiss(chunks_vectorized)
    print("chunks save to faiss")


def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.md")
    documents = loader.load()
    return documents


def split_text(texts, chunk_size=500, overlap=100):
        """Découpe un texte en chunks, d'abord par paragraphes, puis par phrases si nécessaire."""

        for text in texts:
            encoding = tiktoken.get_encoding("cl100k_base")
            paragraphs = text.split("\n\n")  # Séparer par paragraphes

            chunks = []
            current_chunk = []
            current_length = 0

            for para in paragraphs:
                tokenized_para = encoding.encode(para)
                
                # Si le paragraphe tient dans un chunk, on l'ajoute directement
                if len(tokenized_para) <= chunk_size:
                    if current_length + len(tokenized_para) > chunk_size:
                        # Sauvegarde le chunk précédent
                        chunks.append(encoding.decode(sum(current_chunk, [])))
                        current_chunk = []
                        current_length = 0

                    current_chunk.append(tokenized_para)
                    current_length += len(tokenized_para)
                else:
                    # Si le paragraphe est trop long, on le découpe en phrases
                    sentences = sent_tokenize(para)
                    for sentence in sentences:
                        tokenized_sentence = encoding.encode(sentence)
                        sentence_length = len(tokenized_sentence)

                        if current_length + sentence_length > chunk_size:
                            chunks.append(encoding.decode(sum(current_chunk, [])))

                            # Overlap avec les derniers tokens du chunk précédent
                            if chunks and overlap > 0:
                                overlap_tokens = encoding.encode(" ".join(chunks[-1].split()[-overlap:]))
                                current_chunk = [overlap_tokens]
                                current_length = len(overlap_tokens)
                            else:
                                current_chunk = []
                                current_length = 0

                        current_chunk.append(tokenized_sentence)
                        current_length += sentence_length

            if current_chunk:
                chunks.append(encoding.decode(sum(current_chunk, [])))

            return chunks

        
def save_to_faiss(chunks, chunks_vectorized):
    try:
        # 🔄 Suppression et réinitialisation de FAISS avant de stocker de nouveaux vecteurs
        dimension = chunks_vectorized.shape[1]

        # 📌 Ajouter les vecteurs dans FAISS et sauvegarder
        index = faiss.IndexFlatL2(dimension)
        index.add(chunks_vectorized)
        faiss.write_index(index, FAISS_PATH)

        json.dump(chunks, open(FAISS_PATH + "/chunks.json", "w"))

        print("✅ FAISS index et chunks stocké en dur !")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
