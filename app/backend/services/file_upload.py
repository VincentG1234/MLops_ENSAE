# file_upload.py
import os
import shutil
import time
import docx
# For PDF/wordfile files
import pdfplumber
from fastapi import UploadFile
import psutil


FAISS_PATH = "./backend/FAISS"
DATA_PATH = "./backend/uploads"


def convert_to_md(file_path):
    """
    Convertit un fichier en format Markdown (.md).

    Arguments:  
    file_path : str -- Chemin du fichier à convertir.

    Returns:
    None
    """
    md_content = ""

    print(file_path)
    if file_path.endswith('.pdf'):
        # Traitement du PDF
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    md_content += text + "\n\n"  # Ajoute une nouvelle ligne entre les pages
        file_path_md = file_path.replace('.pdf', '.md')

    elif file_path.endswith('.docx'):
        # Traitement du DOCX
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            md_content += para.text + "\n"  # Ajoute chaque paragraphe

        file_path_md = file_path.replace('.docx', '.md')

    elif file_path.endswith('.txt'):
        # Traitement du TXT
        with open(file_path, 'r', encoding='utf-8') as file:
            md_content = file.read()  # Lit tout le contenu

        file_path_md = file_path.replace('.txt', '.md')

    elif file_path.endswith(".md"):
        return None

    else:
        raise ValueError("File format unsupported.")

    print(file_path_md + "test!")
    # Écriture dans le fichier Markdown
    with open(file_path_md, 'w', encoding='utf-8') as md_file:
        md_file.write(md_content)

    # Supprime le fichier initial pour le stockage
    os.remove(file_path)


# Exemple d'utilisation
# convert_to_md('analyse_complexe.pdf')

# Function to handle file upload
def upload_doc(file: UploadFile):
    try:
        # Ensure upload directory exists
        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH)

        file_path = os.path.join(DATA_PATH, file.filename)

        # Save the uploaded file
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Convert the file to Markdown
        convert_to_md(file_path)

        return f"File '{file.filename}' uploaded and processed successfully."
    except Exception as e:
        return f"An error occurred: {e}"


### Deletion of temporary files ###

# Function to handle file removal
def handle_remove_readonly(func, path, exc_info):
    """
    Modifie les permissions et réessaie de supprimer le fichier.
    """
    os.chmod(path, 0o777)
    func(path)

# Supprimer les fichiers temporaires (uploads et bases de données)
def delete_files():
    """
    Supprime les fichiers temporaires et les bases de données créées.
    """
    time.sleep(2)  # Wait for the database to be closed
    try:
        if os.path.exists(FAISS_PATH):
            shutil.rmtree(FAISS_PATH, onerror=handle_remove_readonly)
            print("FAISS files deleted")
        if os.path.exists(DATA_PATH):
            shutil.rmtree(DATA_PATH, onerror=handle_remove_readonly)
            print("Data files deleted")
    except Exception as e:
        print(f"Error deleting files: {e} \n The files will be deleted on server restart.")