# query_data.py

import argparse
# from dataclasses import dataclass
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import openai 
from openai import OpenAI
from dotenv import load_dotenv
import os
import markdown2

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
#---- Set OpenAI API key 
# Change environment variable name from "OPENAI_API_KEY" to the name given in 
# your .env file.
openai.api_key = os.environ['OPENAI_API_KEY']

CHROMA_PATH = "chroma"

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


def query_database_agent(query_text, chat_history=None, model_name="gpt-4o"):
    # Préparer la base de données
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Rechercher dans la base de données
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.2:
        return {'error': "Aucun résultat pertinent trouvé."}

    # Construire le contexte avec l'historique du chat
    history_text = ""
    if chat_history:
        for msg in chat_history:
            if msg['sender'] == 'user':
                history_text += f"Utilisateur : {msg['question']}\n"
            elif msg['sender'] == 'assistant':
                history_text += f"Assistant : {msg['answer']}\n"

    context_text = "\n----------------------------------------------\n\n".join(
        [doc.page_content for doc, _score in results]
    )

    # Inclure l'historique dans le prompt
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(history=history_text, context=context_text, question=query_text)

    # Initialiser l'API OpenAI avec le client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        # Appeler le modèle OpenAI
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "Vous êtes un assistant utile."},
                {"role": "user", "content": prompt}
            ]
        )
        # Récupérer le texte de la réponse
        response_text = response.choices[0].message.content.strip()
        response_html = markdown2.markdown(response_text)

        sources = [doc.metadata.get("source", None) for doc, _score in results]
        formatted_sources = format_sources(sources)

        # Return just the response and sources in the expected format
        return {
            'answer': response_html,
            'sources': [formatted_sources]
        }

    except Exception as e:
        return f"Erreur with LLM agent : {e}"

# Fonction pour formater les sources
def format_sources(sources):
    # Elimine les doublons
    sources = list(set(sources))

    # Retire uploads et .md
    sources = [source.replace('uploads\\', '').replace('.md', '') for source in sources]

    # Formate les sources
    if len(sources) > 1:
        sources = '; '.join(sources[:-1]) + ' and ' + sources[-1]
    else:
        sources = sources[0]

    return sources


if __name__ == "__main__":
    main()