# Automated Assessment of Students’ Short Written Answers

**Using NLP & Large Language Models (LLMs)**

> CS 4624 Multimedia/Hypertext • Virginia Tech
> Instructor & Client: **Dr. Mohamed Farag**

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Tech Stack](#tech-stack)
5. [Prerequisites](#prerequisites)
6. [Setup & Installation](#setup--installation)

   * [Local Installation](#local-installation)
   * [Docker Installation](#docker-installation)
7. [Running the Application](#running-the-application)
8. [Usage Guide](#usage-guide)
9. [Repository Structure](#repository-structure)
10. [Contributing](#contributing)
11. [License](#license)
12. [Acknowledgements](#acknowledgements)

---

## Project Overview

This project delivers a **full-stack web platform** that automatically grades student short-answer responses with the help of **open-source Large Language Models**.
It reduces instructor workload, provides rapid feedback to students, and supports flexible grading modes (rubric-based, concept-based, or model-answer comparison).

---

## Key Features

* **JWT-secured authentication** (NextAuth.js + FastAPI)
* Upload of questions & student answers via CSV or UI forms
* Three grading modes (Rubric • Concepts • Sample Answer)
* **Admin panel** for:

  * Pulling LLMs from the [Ollama](https://ollama.com/library) registry
  * Crafting custom grading prompts
  * Pairing prompts with models
  * Running benchmarking tests (Mean Absolute Error)
* **Testing Wizard** to compare multiple model/prompt pairs
* Modular **micro-service-inspired** Docker architecture
* Detailed developer & user documentation

---

## System Architecture

```
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
```

---

## Tech Stack

| Layer      | Technology                                     |
| ---------- | ---------------------------------------------- |
| Frontend   | **React 19**, React-Router 7, Axios            |
| Backend    | **FastAPI**, Pydantic, SQLAlchemy              |
| Auth       | NextAuth.js (frontend) • JWT (backend)         |
| LLM Engine | **Ollama** serving Gemma 3-4b, TinyLlama, etc. |
| Database   | **PostgreSQL 17**, Alembic migrations          |
| DevOps     | **Docker Compose**, GitHub Actions (optional)  |

---

## Prerequisites

### Local (bare-metal)

* **Python ≥ 3.10**
* **Node.js ≥ 18** (includes `npm`)
* **PostgreSQL 17**
* **Ollama** (for on-device LLMs)
* Git (for cloning)

### Docker

* **Docker Desktop** ≥ 4.40 (incl. Compose v2)
* **GPU** optional for faster inference (rename `docker-compose-no-nvidia.yml` if none)

---

## Setup & Installation

You may choose to install and run the system locally, through terminal, or through Docker (with 1 or 4 images).

### Local Installation

#### GUI Workflow (Windows)

1. **Install prerequisites**:

   * Git: [https://git-scm.com/downloads/win](https://git-scm.com/downloads/win)
   * Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)
   * Ollama: [https://ollama.com/download/windows](https://ollama.com/download/windows)
   * Node.js: [https://nodejs.org/en/download](https://nodejs.org/en/download)
   * PostgreSQL 17.4: [https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)

2. **Clone the repository**:

   ```cmd
   git clone https://github.com/f74dragon/Automated-Students-short-answers-assessment
   cd Automated-Students-short-answers-assessment
   ```

3. **Configure the project**:

   ```cmd
   copy .env.local.example .env.local
   notepad .env.local  # Set DOCKERIZED=false
   python -m venv venv
   configPostWin.bat
   ```

4. **Build and launch the frontend**:

   ```cmd
   cd frontend
   npm install
   npm run build
   npm start
   ```

5. **Launch the backend** (in a new terminal):

   ```cmd
   venv\Scripts\activate
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

### Terminal-Only Workflow

#### Windows (PowerShell)

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e
winget install --id OpenJS.NodeJS.LTS -e
winget install --id PostgreSQL.PostgreSQL -e
winget install --id Ollama.Ollama -e
```

#### macOS

```bash
brew update
brew install git python@3.12 node postgresql ollama
```

#### Ubuntu / Debian

```bash
sudo apt-get update
sudo apt-get install -y git python3 python3-venv nodejs npm postgresql postgresql-contrib
curl https://ollama.ai/install.sh | sh
```

#### Verify installations and run Ollama

```bash
ollama serve
```

#### Setup project

```bash
git clone https://github.com/f74dragon/Automated-Students-short-answers-assessment
cd Automated-Students-short-answers-assessment
cp .env.local.example .env.local  # or use 'copy' on Windows
# Edit .env.local and set DOCKERIZED=false
```

#### PostgreSQL Initialization

```bash
# Windows
configPostWin.bat

# macOS / Linux
sudo -u postgres psql
CREATE ROLE "user" LOGIN PASSWORD 'mypassword';
CREATE DATABASE mydatabase OWNER "user";
\q
```

#### Backend Setup

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### Frontend Setup (second terminal)

```bash
cd frontend
npm install
npm run build
npm start
```

---

### All-in-One Docker Image

```bash
git clone https://github.com/f74dragon/Automated-Students-short-answers-assessment.git
cd Automated-Students-short-answers-assessment/LinuxDocker
# Linux/macOS
./rebuild.sh
# Windows
./rebuild.bat
```

Then visit: [http://localhost:3000](http://localhost:3000)

---

### Docker Installation (4-Image Compose)

1. Clone the repo:

   ```bash
   git clone https://github.com/f74dragon/Automated-Students-short-answers-assessment
   cd Automated-Students-short-answers-assessment
   cp .env.docker.example .env.docker
   ```

2. For non-NVIDIA systems:

   ```bash
   mv docker-compose-no-nvidia.yml docker-compose.yml
   ```

3. Build and run:

   ```bash
   docker compose up --build
   ```

| Service    | URL                                              |
| ---------- | ------------------------------------------------ |
| Frontend   | [http://localhost:3000](http://localhost:3000)   |
| Backend    | [http://localhost:8001](http://localhost:8001)   |
| Ollama     | [http://localhost:11434](http://localhost:11434) |
| PostgreSQL | `localhost:5432`                                 |

To shut down: `docker compose down -v`

---

## Running the Application

1. Open [http://localhost:3000](http://localhost:3000)
2. Sign up or log in (first user can become admin)
3. Upload questions and answers (CSV or UI)
4. Choose or define model+prompt pair
5. Click **Grade**
6. (Optional) Benchmark via Admin panel

---

## Usage Guide

See `docs/UserGuide.pdf` or the `/report/` directory. Quick steps:

| Step | Action                           |
| ---- | -------------------------------- |
| 1    | Log in or sign up                |
| 2    | Create a collection              |
| 3    | Upload questions and answers     |
| 4    | Select model/prompt pair         |
| 5    | Click "Grade" to generate scores |
| 6    | Admin access to LLMs & testing   |

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

## Acknowledgements

* **Dr. Mohamed Farag** – project sponsor & domain expert
* **Virginia Tech CS 4624** – course framework & support
* Open-source contributors of FastAPI, React, Ollama, PostgreSQL
* Teammates: **Arian Assadzadeh**, **Demiana Attia**, **Sanjana Ghanta**, **Tai Phan**, **Trey Walker**
