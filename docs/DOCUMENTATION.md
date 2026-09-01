# Documentation

## Architecture Overview

AI Code Explainer follows a clean three-layer architecture that separates
concerns into **UI**, **prompt engineering**, and **API communication**.

The Streamlit frontend (`app.py`) captures user input and renders results.
When a user clicks an action button, the app calls the appropriate function
in `prompts.py` to build a structured `(system_prompt, user_prompt)` pair.
That pair is then forwarded to `groq_client.py`, which sends it to the Groq
chat-completion API and returns the assistant's Markdown response. The
response is stored in Streamlit session state and rendered in an expander
widget. This design means the UI knows nothing about prompt formatting,
and the prompts module knows nothing about HTTP or the Groq SDK — each
layer is independently testable and replaceable.

---

## API Flow

```
┌─────────────┐
│  User Input  │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌────────────┐     ┌────────────────┐     ┌──────────┐
│   app.py    │────▶│ prompts.py │────▶│ groq_client.py │────▶│ Groq API │
│  (Streamlit)│     │  (tuples)  │     │   (HTTP call)  │     │  (LLM)   │
└──────┬──────┘     └────────────┘     └───────┬────────┘     └──────────┘
       │                                       │
       │           ◀─── response string ───────┘
       ▼
┌─────────────┐
│  Rendered   │
│  Markdown   │
└─────────────┘
```

**Step-by-step:**

1. The user pastes code into the `st.text_area` and clicks one of the three action buttons.
2. `app.py` calls the matching prompt function (e.g. `get_explanation_prompt`) which returns a `(system_prompt, user_prompt)` tuple.
3. If the language selector is set to *Auto Detect*, `app.py` first calls `get_autodetect_prompt` → `query_groq` to resolve the language, then passes the resolved language to the selected prompt function.
4. `app.py` passes both prompts and the chosen model ID to `query_groq`.
5. `groq_client.py` sends a chat-completion request to the Groq API with `temperature=0.4` and `max_tokens=2048`.
6. The response string (Markdown) is stored in `st.session_state` and rendered inside an `st.expander`.

---

## Prompt Engineering Decisions

### Why structured Markdown sections?

Each prompt enforces a rigid section structure (e.g. `## 📌 Overview`, `## ⏱ Time Complexity`). This guarantees predictable output that the UI can render consistently, regardless of the model used. Without structure enforcement, LLMs tend to produce free-form prose that varies wildly between runs.

### Why a separate system prompt?

The system prompt sets the LLM's *role* and *rules* (respond only in Markdown, use exact headings). The user prompt carries the *data* (language + code). Keeping them separate allows the system message to benefit from instruction-following optimizations in the chat-completion API and makes it easy to A/B test different system personas without changing the data payload.

### Why temperature 0.4?

A lower temperature produces more deterministic, factual output — ideal for code analysis. A value of 0.4 (rather than 0.0) leaves just enough creativity for the model to produce natural-sounding explanations without hallucinating logic.

### Why the autodetect prompt is minimal?

The autodetect prompt explicitly instructs the model to return *only* the language name with no extra text. This makes the response trivially parseable (just `.strip()` the result) and avoids follow-up parsing logic.

---

## How to Extend

### Add a new language

1. Open `app.py` and add the language name to the `language` selectbox list in the sidebar.
2. No changes are needed in `prompts.py` or `groq_client.py` — the language string is interpolated into prompts automatically.

### Add a new feature button

1. **Create a new prompt function** in `prompts.py`:
   ```python
   def get_security_audit_prompt(code: str, language: str) -> tuple:
       system_prompt = "You are a security auditor..."
       user_prompt = f"Language: {language}\n\nCode:\n```{language.lower()}\n{code}\n```"
       return system_prompt, user_prompt
   ```
2. **Import it** in `app.py`:
   ```python
   from prompts import get_security_audit_prompt
   ```
3. **Add a session-state key** in `app.py`:
   ```python
   if "security" not in st.session_state:
       st.session_state.security = ""
   ```
4. **Add a column + button** alongside the existing three:
   ```python
   col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
   with col4:
       if st.button("🔒 Security Audit", use_container_width=True):
           process_action(get_security_audit_prompt, "security")
   ```
5. **Add a results expander**:
   ```python
   if st.session_state.security:
       with st.expander("🔒 Security Audit", expanded=True):
           st.markdown(st.session_state.security)
   ```

---

## Environment Variables Reference

| Variable       | Required | Description                                         | Example                        |
|----------------|----------|-----------------------------------------------------|--------------------------------|
| `GROQ_API_KEY` | **Yes**  | API key from [console.groq.com](https://console.groq.com/keys) | `gsk_abc123...`                |
