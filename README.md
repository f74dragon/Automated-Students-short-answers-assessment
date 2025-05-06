# Automated Assessment of Students’ Short Written Answers  
**Using NLP & Large Language Models (LLMs)**  

> CS 4624 Multimedia/Hypertext • Virginia Tech  
> Instructor & Client: **Dr. Mohamed Farag**

---

## Table of Contents
1. [Project Overview](#project-overview)  
2. [Key Features](#key-features)  
3. [System Architecture](#system-architecture)  
4. [Tech Stack](#tech-stack)  
5. [Prerequisites](#prerequisites)  
6. [Installation](#installation)  
   - [Local Setup](#local-setup)  
   - [Docker Setup](#docker-setup)  
7. [Running the Application](#running-the-application)  
8. [Usage Guide](#usage-guide)  
9. [Repository Structure](#repository-structure)  
10. [Contributing](#contributing)  
11. [License](#license)  
12. [Acknowledgements](#acknowledgements)  

---

## Project Overview
This project delivers a **full‑stack web platform** that automatically grades student short‑answer responses with the help of **open‑source Large Language Models**.  
It reduces instructor workload, provides rapid feedback to students, and supports flexible grading modes (rubric‑based, concept‑based, or model‑answer comparison).

---

## Key Features
- **JWT‑secured authentication** (NextAuth.js + FastAPI)  
- Upload of questions & student answers via CSV or UI forms  
- Three grading modes (Rubric • Concepts • Sample Answer)  
- **Admin panel** for:  
  - Pulling LLMs from the [Ollama](https://ollama.com/library) registry  
  - Crafting custom grading prompts  
  - Pairing prompts with models  
  - Running benchmarking tests (Mean Absolute Error)  
- **Testing Wizard** to compare multiple model/prompt pairs  
- Modular **micro‑service‑inspired** Docker architecture  
- Detailed developer & user documentation

---

## System Architecture
```text
┌─────────────────────────────┐
│           React             │
│  (NextAuth.js, Axios, CSS)  │
└───────────▲───────┬─────────┘
            │REST   │JWT
┌───────────┴───────▼─────────┐
│          FastAPI            │
│  – Auth / CRUD / LLM proxy  │
└───────────▲───────┬─────────┘
            │SQL    │HTTP
┌───────────┴───┐ ┌─▼─────────┐
│ PostgreSQL DB │ │  Ollama   │
└───────────────┘ │ Gemma3:4b │
                  │ TinyLlama │
                  └───────────┘


---

## Tech Stack

| Layer      | Technology                                     |
| ---------- | ---------------------------------------------- |
| Frontend   | **React 19**, React‑Router 7, Axios            |
| Backend    | **FastAPI**, Pydantic, SQLAlchemy              |
| Auth       | NextAuth.js (frontend) • JWT (backend)         |
| LLM Engine | **Ollama** serving Gemma 3‑4b, TinyLlama, etc. |
| Database   | **PostgreSQL 17**, Alembic migrations          |
| DevOps     | **Docker Compose**, GitHub Actions (optional)  |

---

## Prerequisites

### Local (bare‑metal)

* **Python ≥ 3.10**
* **Node.js ≥ 18** (includes `npm`)
* **PostgreSQL 17**
* **Ollama** (for on‑device LLMs)
* Git (for cloning)

### Docker

* **Docker Desktop** ≥ 4.40 (incl. Compose v2)
* **GPU** optional for faster inference (rename `docker-compose-no-nvidia.yml` if none)

---

## Installation

### Local Setup

```bash
# 1. Clone
git clone https://github.com/<your‑org>/Automated-Students-short-answers-assessment.git
cd Automated-Students-short-answers-assessment

# 2. Backend ── create venv & install
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
cp .env.example .env  # adjust values

# 3. Frontend ── install & build
cd frontend
npm install
npm run build
npm start         # dev server on http://localhost:3000

# 4. Backend ── run API
cd ../backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

> **Tip**: run `configPostWin.bat` on Windows to auto‑provision PostgreSQL roles.

### Docker Setup

```bash
# GPU system
docker compose up --build       # uses docker-compose.yml

# CPU‑only system
mv docker-compose-no-nvidia.yml docker-compose.yml
docker compose up --build
```

The UI becomes available at **[http://localhost:3000](http://localhost:3000)** once all containers are healthy.

---

## Running the Application

1. Open [http://localhost:3000](http://localhost:3000)
2. **Sign up / Log in** (first user may create an *Admin* account)
3. Create **Collections**, upload **Questions** & **Student Answers** (CSV)
4. Choose or create **Prompt–Model Pairs**
5. Click **Grade** (single or bulk) to generate scores & feedback
6. Use **Admin → Testing Wizard** to benchmark new models/prompts

---

## Usage Guide

Full step‑by‑step instructions with screenshots reside in **`docs/UserGuide.pdf`** (or see the compiled LaTeX in `/report/`). The quick flow:

| Step | Action                             |
| ---- | ---------------------------------- |
| 1    | **Login / Sign Up**                |
| 2    | **Create Collection**              |
| 3    | **Upload** questions & answers     |
| 4    | **Select Pair** (prompt + model)   |
| 5    | **Grade** → view results           |
| 6    | Optional: **Admin Panel** for LLMs |

---

## Repository Structure

```text
.
├─ backend/          # FastAPI source, models, API routes
│  ├─ app/
│  ├─ tests/
│  └─ Dockerfile
├─ frontend/         # React app (components, pages, styles)
│  ├─ src/
│  └─ Dockerfile
├─ examples/         # Sample CSVs for import & testing
├─ docs/             # PDF report, user & dev manuals
├─ docker-compose.yml
├─ docker-compose-no-nvidia.yml
├─ configPostWin.bat
└─ README.md
```

---

## Contributing

Pull requests are welcome!

1. Fork the repo & create a feature branch.
2. Follow existing **black + isort** formatting (Python) and **eslint** rules (JS).
3. Ensure all **tests pass** (`pytest` + `npm test`).
4. Open a PR describing your changes.

---

## License

Distributed under the **MIT License**.
See [`LICENSE`](LICENSE) for details.

---

## Acknowledgements

* **Dr. Mohamed Farag** – project sponsor & domain expert
* **Virginia Tech CS 4624** – course framework & support
* Open‑source communities of **FastAPI, React, Ollama, Gemma, TinyLlama**
* Teammates **Arian Assadzadeh**, **Demiana Attia**, **Sanjana Ghanta**, **Tai Phan**, **Trey Walker**

---

```
```




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
