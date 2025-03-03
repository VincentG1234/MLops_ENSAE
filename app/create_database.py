# create_database.py
import os

import nltk
import openai
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import sqlite3


nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
# ---- Set OpenAI API key
# Change environment variable name from "OPENAI_API_KEY" to the name given in 
# your .env file.
openai.api_key = os.environ['OPENAI_API_KEY']

CHROMA_PATH = "chroma"
DATA_PATH = "uploads"


def main():
    generate_data_store()


def generate_data_store():
    documents = load_documents()
    print("document load for generate database")

    chunks = split_text(documents)
    print("chunks done")

    save_to_chroma(chunks)
    print("chunks save to chroma")


def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.md")
    documents = loader.load()
    return documents


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks

# optional: vacuum the database to reduce
def vacuum_chroma_db(db_path):
    conn = sqlite3.connect(f"{db_path}/chroma.sqlite3")
    conn.execute("VACUUM")
    conn.close()

def save_to_chroma(chunks: list[Document]):
    try:
        db = Chroma.from_documents(
            chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH
        )
        vacuum_chroma_db(CHROMA_PATH)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
