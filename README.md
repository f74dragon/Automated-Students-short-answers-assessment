# Automated-Students-short-answers-assessment
Automated Students' short answers assessment for CS4624: Multimedia, Hypertext and information Access

## Setup

venv\Scripts\activate

### Environment Variables

This project requires environment variables for configuration. Example files are provided at the root of the repository:

*   `.env.local.example`: Use this template when running the backend directly on your host machine (without Docker).
*   `.env.docker.example`: Use this template when running the application stack via `docker-compose`.

**Choose ONE workflow and prepare the corresponding `.env` file:**

1.  **For Running Locally (Without Docker):**
    *   Copy the local example file to `.env.local`:
        ```bash
        cp .env.local.example .env.local
        ```
    *   Edit `.env.local` if your local PostgreSQL or Ollama setup uses different connection details than the defaults (`localhost:5432` for Postgres, `http://localhost:11434` for Ollama).

2.  **For Running with Docker:**
    *   Copy the Docker example file to `.env.docker`:
        ```bash
        cp .env.docker.example .env.docker
        ```
    *   The `docker-compose.yml` file is pre-configured to load variables from `.env.docker` into the backend container. The default values should work if you are using the included `docker-compose.yml`.

### Ollama Setup
Go to [https://ollama.com/](https://ollama.com/) to download and install Ollama if you haven't already.

*   **If running locally:** Ensure Ollama is running and accessible at the `OLLAMA_URL` specified in your `.env.local` file (default: `http://localhost:11434`).
*   **If running with Docker:** The `docker-compose.yml` file includes an Ollama service. Ensure the `OLLAMA_URL` in `.env.docker` points to the service name (default: `http://ollama:11434`).

## Running the Application

### Without Docker (Local Development)

1.  Ensure you have Python (3.x recommended) and pip installed.
2.  Set up your environment variables by creating and configuring `.env.local` as described in the Setup section.
3.  Install backend dependencies:
    ```bash
    pip install -r backend/requirements.txt
    ```
4.  Make sure you have a PostgreSQL server running locally. The database, user, and password must match the `DATABASE_URL` in your `.env.local` file.
5.  Ensure Ollama is running locally.
6.  Start the FastAPI backend server from the project root directory:
    ```bash
    uvicorn backend.app.main:app --reload --port 8001
    ```
7.  **Frontend:** Navigate to the `frontend` directory (`cd frontend`), install dependencies (`npm install`), and start the React development server (`npm start`). The frontend will typically run on `http://localhost:3000`.

### With Docker

1.  Ensure Docker and Docker Compose are installed and running.
2.  Set up your environment variables by creating `.env.docker` as described in the Setup section.
3.  From the project root directory, build and start the services:
    ```bash
    docker-compose up --build -d
    ```
    *   The `-d` flag runs the containers in detached mode (in the background). Omit it if you want to see the logs directly in your terminal.
4.  The application stack will be accessible at:
    *   Frontend: `http://localhost:3000`
    *   Backend API: `http://localhost:8001`
    *   Ollama API (if needed directly): `http://localhost:11434`
    *   PostgreSQL (if needed directly): `localhost:5432`
