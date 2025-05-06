
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
````

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

## Setup & Installation

You can run the Automated Student Short Answer Assessment System either locally or using Docker. Follow the instructions below based on your preferred setup.

---

### Local Installation (Windows)

#### 1. Install Prerequisites

Download and install the following tools:

- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Ollama](https://ollama.com/download/windows)
- [Node.js](https://nodejs.org/en/download)
- [PostgreSQL 17.4](https://www.postgresql.org/download/windows/)

> During PostgreSQL installation, choose a memorable password.

#### 2. Clone the Repository

```bash
git clone https://github.com/f74dragon/Automated-Students-short-answers-assessment
cd Automated-Students-short-answers-assessment
````

#### 3. Set Up Environment Variables

This project uses environment variables for configuration. Templates are provided:

* `.env.local.example` — for local development (no Docker)
* `.env.docker.example` — for Docker-based development

Copy and customize the appropriate file:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` to match your PostgreSQL and Ollama settings if different from defaults:

* PostgreSQL: `localhost:5432`
* Ollama: `http://localhost:11434`

#### 4. Create and Activate Python Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

#### 5. Configure Database

Run the configuration script and enter your PostgreSQL password twice:

```bash
configPostWin.bat
```

#### 6. Install Backend Dependencies

```bash
pip install -r backend/requirements.txt
```

#### 7. Start Backend

```bash
uvicorn backend.app.main:app --reload --port 8001
```

#### 8. Set Up Frontend

```bash
cd frontend
npm install
npm run build
npm start
```

---

### Docker Installation

#### Supported Versions

* Docker Desktop: 4.40.0
* Docker Engine: 28.0.4

> Later versions may not be compatible.

#### Installation Instructions

* **[Windows/macOS/Linux](https://www.docker.com/products/docker-desktop)** — follow official installation instructions.
* **Ubuntu (example):**

```bash
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $USER
```

> Restart your terminal or system after adding your user to the `docker` group.

#### 1. Set Up Environment Variables

```bash
cp .env.docker.example .env.docker
```

Ensure `.env.docker` contains valid values for your Docker setup. The included `docker-compose.yml` is pre-configured to read this file.

#### 2. Ollama Setup

If running inside Docker, the Ollama service is included in `docker-compose.yml`. Ensure:

* `.env.docker`: `OLLAMA_URL=http://ollama:11434`

If running Ollama locally, match your `.env.local` or `.env.docker` accordingly.

#### 3. GPU Configuration

* If your system has an **NVIDIA GPU**, use the default `docker-compose.yml`.
* If it does **not**, rename the configuration file:

```bash
mv docker-compose-no-nvidia.yml docker-compose.yml
```

#### 4. Build and Run

```bash
docker-compose up --build -d
```

Access the application at:

* Frontend: [http://localhost:3000](http://localhost:3000)
* Backend API: [http://localhost:8001](http://localhost:8001)
* Ollama API: [http://localhost:11434](http://localhost:11434)
* PostgreSQL: `localhost:5432` (if needed)

To view logs:

```bash
docker-compose logs -f
```




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

## License

Distributed under the **MIT License**.
See [`LICENSE`](LICENSE) for details.

---

## Acknowledgements

* **Dr. Mohamed Farag** – project sponsor & domain expert
* **Virginia Tech CS 4624** – course framework & support
* Open‑source communities of **FastAPI, React, Ollama, PostgreSQL**
* Teammates **Arian Assadzadeh**, **Demiana Attia**, **Sanjana Ghanta**, **Tai Phan**, **Trey Walker**

---


