# main.py

import atexit
import logging
import os
import uuid

from fastapi import FastAPI, Request, Form, UploadFile, File, Depends, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# For database creation (doc to embeddings and chunks)
from create_database import generate_data_store
# for upload documents and convert them to MD
from file_upload import upload_doc, delete_files
# For chatbot
from query_data import query_database_agent
from user_auth import init_firebase, login_user, register_user

CHROMA_PATH = "chroma"
DATA_PATH = "uploads"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# Initialiser Firebase
init_firebase()

app = FastAPI()

# Monter le répertoire 'static' sous le chemin '/static'
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurer le répertoire des templates
templates = Jinja2Templates(directory="templates")

# Fonction à exécuter à la sortie
atexit.register(delete_files)

# Suppression des fichiers temporaires au démarrage de l'application 
@app.on_event("startup")
async def startup_event():
    logger.info("Application starting, deleting files...")
    delete_files()


# Dépendance pour obtenir l'utilisateur actuel à partir des cookies
def get_current_user(request: Request):
    user = request.cookies.get('user')
    return user



# Route d'accueil
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user: str = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("home.html", {"request": request, "user": user})


# Routes de connexion
@app.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    user = login_user(email, password)
    if user:
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="user", value=user)
        return response
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Wrong username or password"})


# Routes d'inscription
@app.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register_post(request: Request, email: str = Form(...), password: str = Form(...),
                        confirm_password: str = Form(...)):
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Unmatching passwords"})
    user = register_user(email, password)
    if user:
        return RedirectResponse(url="/login", status_code=302)
    else:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Sign up failed"})


# Téléchargement de documents
@app.get("/upload", response_class=HTMLResponse)
async def upload_get(request: Request, user: str = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("upload.html", {"request": request, "user": user})


@app.post("/upload")
async def upload_post(request: Request, file: UploadFile = File(...), user: str = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")
    message = upload_doc(file)
    return templates.TemplateResponse("upload.html", {"request": request, "message": message, "user": user})


# Chat avec le document
# Stocker les sessions de chat en mémoire
chat_sessions = {}


@app.get("/chat", response_class=HTMLResponse)
async def chat_get(request: Request, user: str = Depends(get_current_user), session_id: str = Cookie(None),
                   error: str = None):
    # Rediriger vers la page de connexion si l'utilisateur n'est pas connecté
    if not user:
        return RedirectResponse(url="/login")

    # Générer un nouvel identifiant de session si nécessaire
    if not session_id:
        session_id = str(uuid.uuid4())

    # Récupérer l'historique du chat depuis la session
    chat_history = chat_sessions.get(session_id, [])

    # Ajouter le message d'erreur (si présent) dans le contexte
    context = {
        "request": request,
        "user": user,
        "chat_history": chat_history,
        "error": error
    }

    # Créer une réponse avec un cookie pour la session
    response = templates.TemplateResponse("chat.html", context)
    response.set_cookie(key="session_id", value=session_id)
    return response


@app.post("/chat")
async def chat_post(request: Request, question: str = Form(...), user: str = Depends(get_current_user),
                    model_name: str = Form(...), session_id: str = Cookie(None)):
    # Logging
    logger.info("----------------")
    logger.info("New chat request received")
    logger.info(f"Question: {question}")
    logger.info(f"Model name: {model_name}")
    logger.info(f"Session ID: {session_id}")
    logger.info(f"User: {user}")

    # Log the raw form data for debugging
    form_data = await request.form()
    logger.info(f"Raw form data: {dict(form_data)}")

    # Ensure user and session_id are set
    if not user:
        return RedirectResponse(url="/login")
    if not session_id:
        session_id = str(uuid.uuid4())

    # Retrieve chat history
    chat_history = chat_sessions.get(session_id, [])

    # Add user question to history
    chat_history.append({
        'sender': 'user',
        'question': question
    })

    try:
        # Process the question
        result = query_database_agent(question, chat_history=chat_history, model_name=model_name)

        # Check if result is an error message or a proper response
        if isinstance(result, str):
            chat_sessions[session_id] = chat_history
            return RedirectResponse(url=f"/chat?error={result}", status_code=303)

        # Add assistant's response to history
        chat_history.append({
            'sender': 'assistant',
            'answer': result.get('answer', ''),
            'sources': result.get('sources', [])
        })

        # Save chat history
        chat_sessions[session_id] = chat_history

        # Redirect to avoid resubmitting the form on refresh
        return RedirectResponse(url="/chat", status_code=303)

    except Exception as e:
        logger.error(f"Error in chat processing: {str(e)}")
        return RedirectResponse(url="/chat?error=An error occurred while processing your request", status_code=303)


# Route de déconnexion
@app.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("user")
    return response


# Generate Chroma data base
@app.post("/generate-chroma")
async def execute_function(request: Request, user: str = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")

    # Vérifie si le répertoire "uploads" existe. S'il n'existe pas, retourne un message d'erreur à l'user pour lui dire de téléverser un document
    upload_directory = "./uploads"
    if not os.path.exists(upload_directory):
        return templates.TemplateResponse(
            "upload.html",
            {"request": request,
             "message": "There is no document uploaded. You must upload a document and then click on upload before generating the database.",
             "user": user}
        )

    # Générer la base de données
    result = generate_data_store()

    # Return the result back to the template
    return templates.TemplateResponse(
        "upload.html",
        {"request": request, "message": f"The Chroma databasis has been created with success", "user": user}
    )
