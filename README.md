# You want to test the application ?

-  **Go to URL: https://gemini-chat-app.lab.sspcloud.fr**
-  **Set "test@gmail.com" as username and "azerty" as password**
-  **Click on the upload button, choose a file (PDF or TXT), upload it, then create the database**
-  **Now, you can chat with your document! Click on "chat" in the upper right corner and start chatting!**


# GitOps

**GitOps Repository: https://github.com/VincentG1234/MLops_ENSAE_gitops**

# ChatDoc - Document Chat Application

An intelligent web application that enables users to upload documents and engage in conversations about their content using advanced Large Language Model technology. Built with FastAPI, Firebase authentication, and Gemini's models.

## 🌟 Features

- **Secure Authentication**: User management through Firebase authentication
- **Document Processing**:
  - Support for multiple file formats (PDF, DOCX, TXT, MD)
  - Automatic conversion to markdown format
  - Smart chunking for optimal processing
- **Intelligent Chat Interface**:
  - Context-aware conversations about uploaded documents
  - Source attribution for answers
  - Persistent chat history
- **Vector Database**: Efficient document storage and retrieval using Chroma
- **Modern UI**: Responsive design with Bootstrap 5
- **Background Processing**: Asynchronous document processing and database generation

## 🛠️ Prerequisites

- Python 3.10 or 3.11
- Google API Key
- Firebase project credentials
- Docker (optional, for containerized deployment)
- Kubernetes cluster access (for production deployment)

## 📦 Installation for Local Development

1. **Clone the Repository**
```bash
git clone https://github.com/VincentG1234/MLops_ENSAE.git
cd Project-I-SL
```

2. **Set Up Virtual Environment**

Linux/MacOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
pip install "unstructured[md]"
```

## ⚙️ Configuration

Create a free API key with your Google account at: https://aistudio.google.com/app/apikey?hl=a

Create a .env file and add the following:

```md
API_KEY_GOOGLE=your_api_key_here
```

Contact us for the Firebase_config.json file (it's just a file giving the credentials for the Google Authentication service), then upload it in the config folder:
```md
app/config/firebase_config.json
```

## Pytest
Run the following command to execute the tests manually.
```bash
pytest
```

## 🚀 Running the Application

### Local Development
```bash
cd app
python -m uvicorn main:app --reload
```

### Access it online
Go here: https://gemini-chat-app.lab.sspcloud.fr

## 🌐 Production Deployment

Our application follows GitOps principles using ArgoCD and Kubernetes manifests to manage production infrastructure.

### CI/CD Workflow

1. **Pre‑commit checks**  
   - On every commit, `pre-commit-config.yaml` runs Black to enforce code formatting.  
2. **GitHub Actions**  
   - Linting and unit tests execute via the workflows in `.github/workflows/`.  
   - Only tagged commits (e.g., `v1.2.3`) proceed to deployment.  

### GitOps Repository

All production deployment manifests live in a dedicated repo:  
🔗 [MLops_ENSAE_gitops](https://github.com/VincentG1234/MLops_ENSAE_gitops)

#### Repository Layout

```text
MLops_ENSAE_gitops/
├── application.yaml      # ArgoCD Application definition
└── deployment/
    ├── deployment.yaml   # Kubernetes Deployment spec
    ├── service.yaml      # Kubernetes Service spec
    └── ingress.yaml      # Ingress rules
````

#### Deployment Steps
1.	**Build & Push:** Container image is built and pushed to Docker Hub.
2.	**Sync:** ArgoCD continuously watches the GitOps repo.
3.	**Apply:** On manifest changes, ArgoCD updates the cluster.
4.	**Route:** Ingress controller exposes the app to end users.

### Accessing Production
1.	Go to: https://gemini-chat-app.lab.sspcloud.fr
2.	Sign in with the shared test account:
   - Username: test@gmail.com
   - Password: azerty
3.	Upload a document and begin chatting!

⸻

### 🔧 Troubleshooting
  - Inspect logs: kubectl logs -l app=gemini-chat-app -n <namespace>
  - Check ArgoCD status: In the ArgoCD UI, ensure the Application is Synced and Healthy.
  - Validate secrets & configs: Confirm all Kubernetes Secrets and ConfigMaps are present and up‑to‑date.

Still need help? Reach out to us by WhatsApp or email.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

### MLOps Enhancement Team (Project for semester 2)
The MLOps implementation, including the GitOps deployment and production infrastructure, was developed by:
- Pierre Clayton (pierre.clayton@ensae.fr)
- Vincent Gimenes (vincent.gimenes@ensae.fr)
- Anna Mosaki (anna.mosaki@ensae.fr)

### Initial Development Team (Initial Project from semester 1)
The initial version of this project was developed as part of the Infrastructure & Systèmes Logiciels course by:
- Marion Chabrol
- Pierre Clayton
- Vincent Gimenes
- Suzie Grondin
- Anna Mosaki

## 🔗 Links

- GitHub Repository: [https://github.com/Pierre-Clayton/Project-I-SL](https://github.com/Pierre-Clayton/Project-I-SL)
