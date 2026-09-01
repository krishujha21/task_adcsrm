# 🧠 AI Code Explainer

> Paste any code. Understand it instantly.

🔗 **Live Demo:** [taskadcsrm.streamlit.app](https://taskadcsrm.streamlit.app)

---

## ✨ Features

- **🔍 Explain Code** — Get a step-by-step walkthrough with time/space complexity analysis.
- **✨ Improve Code** — Receive a code review that catches bugs, anti-patterns, and readability issues.
- **⚡ Optimize Code** — Get a performance-optimized rewrite with before/after complexity comparison.
- **🌐 Auto Language Detection** — Automatically detects the programming language of your snippet.
- **🎨 Dark-Themed UI** — A sleek, wide-layout Streamlit interface designed for comfortable reading.

---

## 🛠 Tech Stack

| Layer     | Technology                  |
|-----------|-----------------------------|
| Frontend  | Streamlit                   |
| Backend   | Python                      |
| LLM API   | Groq (LLaMA 3, Mixtral, Gemma) |
| Prompts   | Custom prompt engineering   |
| Config    | python-dotenv               |

---

## 📁 Project Structure

```
taskadcsrm/
├── .streamlit/
│   └── config.toml          # Dark theme configuration
├── docs/
│   └── DOCUMENTATION.md     # Architecture & extension guide
├── app.py                   # Streamlit UI (frontend)
├── groq_client.py           # Groq API handler (backend)
├── prompts.py               # LLM prompt templates
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

---

## 🚀 Setup & Run

1. **Clone the repository**
   ```bash  
   git clone https://github.com/krishujha21/taskadcsrm.git
   cd taskadcsrm
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS / Linux
   # venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
₹
4. **Configure your API key**
   ```bash
   cp .env.example .env
   ```
   Open `.env` and replace `your_groq_api_key_here` with your actual [Groq API key](https://console.groq.com/keys).

5. **Run the app**
   ```bash
   streamlit run app.py
   ```
   The app will open at `http://localhost:8501`.

---

## ☁️ Deployment

### Streamlit Community Cloud

1. Push your code to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **"New app"** and select your repository, branch, and `app.py` as the main file.
4. Under **Advanced settings → Secrets**, add:
   ```
   GROQ_API_KEY = "your_groq_api_key_here"
   ```
5. Click **Deploy**. Your app will be live in seconds.

---

## 📸 Screenshots

> *Coming soon — screenshots of the Explain, Improve, and Optimize views.*

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
