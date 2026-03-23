# Setup Guide
## Campus-Aware Intelligent AI Agent

This guide explains how each team member should set up the project locally on their own machine.

This setup guide is based on the current project state:
- GitHub repo already created
- Teammates already added as collaborators
- Project structure already created
- Mobile frontend starter project already set up
- Backend starter project already set up
- Frontend and backend already connected through the `/health` endpoint

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [Software Each Team Member Must Install](#3-software-each-team-member-must-install)
4. [Clone the Repository](#4-clone-the-repository)
5. [Git Workflow Rules](#5-git-workflow-rules)
6. [Root-Level Environment Setup](#6-root-level-environment-setup)
7. [Frontend Setup (Mobile App)](#7-frontend-setup-mobile-app)
8. [Backend Setup](#8-backend-setup)
9. [How to Find Your Laptop IP Address](#9-how-to-find-your-laptop-ip-address)
10. [How to Test the Backend](#10-how-to-test-the-backend)
11. [How to Test the Frontend–Backend Connection](#11-how-to-test-the-frontendbackend-connection)
12. [Backend Test Command](#12-backend-test-command)
13. [Common Problems and Fixes](#13-common-problems-and-fixes)
14. [Files That Must NOT Be Committed](#14-files-that-must-not-be-committed)
15. [Current Project Status](#15-current-project-status)
16. [Quick Start Summary](#16-quick-start-summary)

---

## 1. Project Overview

This project uses a **monorepo** structure, which means both frontend and backend live inside the same repository.

### Current Stack

#### Mobile Frontend
- Expo
- React Native
- TypeScript
- Expo Router
- pnpm

#### Backend
- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv

#### Development Tools
- Git + GitHub
- VS Code
- Docker Desktop
- Postman / browser testing
- Pytest

---

## 2. Repository Structure

```text
campus-aware-ai-agent/
│
├── .github/
├── .vscode/
├── backend/
├── data/
├── docs/
├── infra/
├── mobile/
├── scripts/
├── .env.example
├── .gitignore
├── docker-compose.yml
└── README.md
```

### Important Folders

| Folder | Purpose |
|--------|---------|
| `mobile/` | Expo React Native frontend |
| `backend/` | FastAPI backend |
| `docs/` | Project documentation |
| `data/` | Sample/mock data |
| `infra/` | Deployment/Docker-related files |

---

## 3. Software Each Team Member Must Install

Every teammate should install the same tools.

### 1. Git

Install Git and verify:

```bash
git --version
```

### 2. VS Code

Install [Visual Studio Code](https://code.visualstudio.com/).

Recommended extensions:
- Python
- Pylance
- Ruff
- Black Formatter
- ESLint
- Prettier
- GitLens
- Docker

### 3. Python

Install **Python 3.11 or 3.12** and verify:

```bash
python --version
```

### 4. Node.js

Install **Node.js 20 LTS** and verify:

```bash
node -v
npm -v
```

> **Important:** Use Node 20. Do not use a random newer version if Expo breaks.

### 5. pnpm

Install pnpm globally:

```bash
npm install -g pnpm
```

Verify:

```bash
pnpm -v
```

### 6. Docker Desktop

Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) and verify:

```bash
docker --version
docker compose version
```

### 7. Expo Go App

Install **Expo Go** on your phone from the Play Store or App Store.

> This is needed to run the mobile app on a real device.

---

## 4. Clone the Repository

Each teammate should clone the repo locally:

```bash
git clone https://github.com/Saiful-Codes/campus-aware-ai-agent.git
cd campus-aware-ai-agent
```

Then open the project in VS Code:

```bash
code .
```

---

## 5. Git Workflow Rules

Please follow this workflow strictly.

### Branches

| Branch | Purpose |
|--------|---------|
| `main` | Stable / demo-ready code |
| `dev` | Active shared development branch |
| `feature/<name>` | Feature work branches |

### Important Rules

- ❌ Do **not** push directly to `main`
- ❌ Do **not** push directly to `dev`
- ✅ Always create a feature branch **from** `dev`
- ✅ Always create a Pull Request **into** `dev`

### Example Workflow

**Step 1:** Get latest `dev`

```bash
git checkout dev
git pull origin dev
```

**Step 2:** Create your own feature branch

```bash
git checkout -b feature/your-task-name
```

**Step 3:** Work on your task, then commit

```bash
git add .
git commit -m "feat: short clear description"
```

**Step 4:** Push your branch

```bash
git push -u origin feature/your-task-name
```

**Step 5:** Create a Pull Request

Create a PR from `feature/your-task-name` → `dev`

---

## 6. Root-Level Environment Setup

There is a root `.env.example` file in the repo.

> ⚠️ Do **not** put real secrets into `.env.example`  
> ⚠️ Do **not** commit real `.env` files to GitHub

At the current stage, the frontend uses its own `mobile/.env` and the backend uses its own `backend/.env`, so teammates do not need a root `.env` to run the current setup.

---

## 7. Frontend Setup (Mobile App)

All frontend work happens inside the `mobile/` folder.

**Step 1:** Go into `mobile/`

```bash
cd mobile
```

**Step 2:** Install dependencies

```bash
pnpm install
```

**Step 3:** Create the frontend environment file

Inside `mobile/`, create a file named `.env` and add:

```env
EXPO_PUBLIC_API_BASE_URL=http://YOUR-LAPTOP-IP:8000
```

Example:

```env
EXPO_PUBLIC_API_BASE_URL=http://192.168.0.109:8000
```

> ⚠️ Do **not** use `localhost` or `127.0.0.1` — use your laptop's IPv4 address.  
> **Why?** Expo Go runs on your phone, and your phone cannot reach your laptop's backend through `localhost`.

**Step 4:** Start the frontend

```bash
pnpm expo start --clear
```

This will open the Expo dev server. Scan the QR code using Expo Go to open the app on your phone.

---

## 8. Backend Setup

All backend work happens inside the `backend/` folder.

**Step 1:** Go into `backend/`

```bash
cd backend
```

**Step 2:** Create a virtual environment

If `.venv` is not already present locally, create it:

```bash
python -m venv .venv
```

**Step 3:** Activate the virtual environment

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

CMD:

```cmd
.venv\Scripts\activate
```

> You should see `.venv` appear in the terminal prompt.

**Step 4:** Install backend dependencies

```bash
pip install -r requirements.txt
```

**Step 5:** Create the backend environment file

Inside `backend/`, create a file named `.env` and add:

```env
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=campus_ai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your_influx_token
INFLUXDB_ORG=your_org
INFLUXDB_BUCKET=your_bucket

OPENAI_API_KEY=your_openai_api_key
```

> Database, InfluxDB, and OpenAI values can stay as placeholders for now if not yet in use.

**Step 6:** Run the backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Keep this terminal running.

---

## 9. How to Find Your Laptop IP Address

The frontend needs your laptop's IP so the phone can reach the backend.

### On Windows

Run:

```cmd
ipconfig
```

Look for **IPv4 Address**, for example:

```
192.168.0.109
```

Use that IP in your frontend `.env`:

```env
EXPO_PUBLIC_API_BASE_URL=http://192.168.0.109:8000
```

> ⚠️ Your phone and laptop must be on the **same Wi-Fi network**.  
> If the backend works in the browser but not on the phone, check your firewall settings.

---

## 10. How to Test the Backend

Once the backend is running, test the following in your browser:

### Health Endpoint

```
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "environment": "development",
  "port": 8000
}
```

### API Docs (Swagger UI)

```
http://127.0.0.1:8000/docs
```

You can also test using your actual IP:

```
http://YOUR-LAPTOP-IP:8000/health
```

Example:

```
http://192.168.0.109:8000/health
```

---

## 11. How to Test the Frontend–Backend Connection

**Step 1:** Run the backend

```bash
cd backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Step 2:** Run the frontend

```bash
cd mobile
pnpm expo start --clear
```

**Step 3:** Open the app in Expo Go.

**Expected result:** The home screen should display something like:

```
Backend connected
Status: ok
Environment: development
Port: 8000
```

If you see this, the frontend and backend are connected successfully. ✅

---

## 12. Backend Test Command

A basic pytest test is already included. To run backend tests:

```bash
cd backend
.venv\Scripts\Activate.ps1
python -m pytest
```

Expected result:

```
1 passed
```

> **Important:** Always activate `.venv` first. Use `python -m pytest` rather than plain `pytest` if you are unsure about environment issues.

---

## 13. Common Problems and Fixes

### Problem 1: `ModuleNotFoundError: No module named 'fastapi'`

**Cause:** Virtual environment not activated.

**Fix:**

```bash
cd backend
.venv\Scripts\Activate.ps1
python -m pytest
```

---

### Problem 2: Mobile app says `Network request failed`

**Cause:** Frontend cannot reach the backend.

**Check:**
- Backend is running with `--host 0.0.0.0`
- Frontend `.env` uses the laptop IP, not `localhost`
- Phone and laptop are on the same Wi-Fi
- Firewall is not blocking port `8000`

---

### Problem 3: Expo app still uses old `.env` value

**Fix:**

```bash
pnpm expo start --clear
```

---

### Problem 4: Backend works on laptop browser but not phone browser

**Cause:** Firewall or wrong IP.

**Fix:**
- Test `http://YOUR-IP:8000/health` in the phone browser
- Allow Python / port `8000` through the firewall
- Re-run `ipconfig` to recheck the IP

---

### Problem 5: pytest fails from `(base)` environment

**Cause:** Wrong Python environment active.

**Fix:**

```bash
cd backend
.venv\Scripts\Activate.ps1
python -m pytest
```

---

## 14. Files That Must NOT Be Committed

Do not commit the following files or folders:

```
backend/.venv
backend/.env
mobile/.env
node_modules/
.expo/
__pycache__/
```

> These are already covered by `.gitignore`.

---

## 15. Current Project Status

### ✅ Complete

- GitHub repo set up
- Project structure created
- Mobile frontend starter created
- FastAPI backend starter created
- Backend `/health` endpoint working
- Backend test working
- Frontend successfully connected to backend

### 🔜 Not Yet Required

The following will be added in later phases:

- PostgreSQL integration
- InfluxDB integration
- Firebase Authentication
- AI / RAG / Text-to-SQL features

---

## 16. Quick Start Summary

If you have already installed all required software, here is the usual daily startup flow:

### Backend Terminal

```bash
cd backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Terminal

```bash
cd mobile
pnpm install
pnpm expo start --clear
```
