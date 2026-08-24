# Voice Shopping Assistant

A smart, voice-controlled grocery shopping list application. Manage your shopping list hands-free using natural language commands, supported by a powerful NLP-style backend pipeline and a beautiful, mobile-first dark mode interface.

## 🌟 Features

- **🗣️ Natural Language Voice Commands:** Say things like *"Add a couple of apples and half a dozen eggs"* and the assistant will accurately parse quantities, units, and products.
- **🎨 Premium Dark Theme UI:** A fully responsive, PWA-ready web interface designed with Tailwind-inspired tokens and beautiful SVG icons (Lucide).
- **🧠 Intelligent Disambiguation:** If a voice command is ambiguous (e.g., "Add milk" when multiple milk products exist), the system prompts the user to select the correct item.
- **🛡️ Safe Destructive Actions:** Commands like "clear my list" require explicit user confirmation to prevent accidental deletion.
- **⚡ Fast Modern Stack:** Built with React/Vite on the frontend and FastAPI on the backend.

---

## 🏗️ Architecture

The project is split into two main components:

1. **`backend/` (FastAPI + Python)**
   - Provides REST APIs for authentication, products, and shopping list management.
   - Houses the `voice.py` service, which runs a structured rule-based NLP pipeline (normalization → classification → extraction → routing).
   - Uses SQLite for the database.

2. **`frontend-web/` (React + Vite + TypeScript)**
   - A Progressive Web App (PWA) with a responsive mobile-first design.
   - Manages voice recording, state management, and real-time user feedback.

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v18+)
- Python (3.9+)

### 1. Backend Setup

Open a terminal and navigate to the `backend` folder:

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server (runs on http://localhost:10000)
uvicorn app.main:app --host 0.0.0.0 --port 10000 --reload
```

### 2. Frontend Setup

Open a separate terminal and navigate to the `frontend-web` folder:

```bash
cd frontend-web

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will usually start at `http://localhost:5173`.

---

## 🎙️ Example Voice Commands

The assistant understands a variety of natural phrases:

- **Adding items:** *"I need 2 liters of milk"* or *"Add apples and bananas to my list"*
- **Removing items:** *"I don't need apples anymore"* or *"Remove the milk"*
- **Updating quantity:** *"Change the eggs to 12"*
- **Checking list:** *"What's on my list?"*
- **Clearing list:** *"Clear my entire list"* (Will ask for confirmation)

---

## 🛠️ Tech Stack

- **Frontend:** React, TypeScript, Vite, Lucide React (Icons), Vanilla CSS
- **Backend:** FastAPI, Python, SQLAlchemy, SQLite
