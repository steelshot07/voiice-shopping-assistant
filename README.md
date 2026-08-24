# Voice Shopping Assistant

A smart, voice-controlled grocery shopping list app. Manage your shopping list hands-free using natural language — say what you need, and it handles the rest.

---

## 🌐 Live Demo

**👉 [voice-shopping-assistant-o0uxy51c3.vercel.app](https://voice-shopping-assistant-o0uxy51c3.vercel.app)**

> No installation needed. Works in any modern browser on desktop or mobile.

---

## 🚀 Getting Started (First-Time Users)

### 1. Create an Account
- Open the app and tap **Sign Up**
- Enter your email and a password, then tap **Create Account**
- You'll be logged in automatically

### 2. Add Items by Voice
- Tap the **microphone button** in the centre of the screen
- Speak naturally — for example:
  - *"Add 2 litres of milk"*
  - *"I need apples and bananas"*
  - *"Add a dozen eggs"*
- Release the button and your items will appear on the list

### 3. Add Items Manually
- Use the **search bar** at the top to find a product
- Tap the **+** button next to any result to add it instantly
- Or tap **Add item manually** to type a custom item

### 4. Manage Your List
- **Check off** an item by tapping the checkbox — it moves to "Completed"
- **Change quantity** with the **−** and **+** buttons on each item
- **Delete** an item with the trash icon on the right
- Tap **Mark all done** to complete your entire shop in one go

### 5. Browse by Category
- Tap the **Explore** tab (bottom navigation) to browse products by category
- Tap any product card to add it to your list

### 6. View Purchase History
- Tap the **History** tab to see everything you've previously purchased

---

## 🎙️ Voice Command Examples

| What you say | What happens |
|---|---|
| *"Add 2 litres of milk"* | Adds 2 litres of milk to your list |
| *"I need apples and bananas"* | Adds both items at once |
| *"Remove the eggs"* | Deletes eggs from your list |
| *"Change the milk to 3"* | Updates milk quantity to 3 |
| *"What's on my list?"* | Reads back your current items |
| *"Clear my entire list"* | Asks for confirmation, then clears all items |

---

## 🌟 Features

- **🗣️ Natural Language Voice Commands** — Understands a wide range of phrasings and quantities
- **🧠 Smart Disambiguation** — If a command is ambiguous, it asks you to clarify
- **🛡️ Safe Destructive Actions** — Clears and deletes always ask for confirmation
- **📱 Mobile-First Design** — Works great on any screen size
- **🌙 Dark Mode** — Easy on the eyes

---

## 🏗️ Architecture

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite, Lucide Icons, Vanilla CSS |
| Backend | FastAPI, Python, SQLAlchemy, SQLite |
| Hosting | Vercel (frontend) · Render (backend) |

The backend exposes a REST API. Voice input is processed by a structured NLP pipeline (normalisation → classification → extraction → routing) running entirely server-side in `backend/app/services/voice.py`.

---

## 🛠️ Local Development

### Prerequisites
- Node.js v18+
- Python 3.9+

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 10000 --reload
```

### Frontend

```bash
cd frontend-web
npm install
npm run dev
```

The frontend starts at `http://localhost:5173`.
