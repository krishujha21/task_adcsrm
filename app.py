import streamlit as st
import hashlib
import json
import difflib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

from groq_client import query_groq, stream_groq
from prompts import (
    get_explanation_prompt,
    get_improvement_prompt,
    get_optimization_prompt,
    get_autodetect_prompt,
    get_chat_prompt,
    get_quiz_prompt,
    get_complexity_prompt,
)

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="AI Code Explainer",
    page_icon="🧠",
    layout="wide"
)

# ===== SESSION STATE KEYS =====
if "explanation" not in st.session_state:
    st.session_state["explanation"] = ""
if "improvement" not in st.session_state:
    st.session_state["improvement"] = ""
if "optimized" not in st.session_state:
    st.session_state["optimized"] = ""
if "improved_code_only" not in st.session_state:
    st.session_state["improved_code_only"] = ""
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "quiz" not in st.session_state:
    st.session_state["quiz"] = None
if "quiz_answers" not in st.session_state:
    st.session_state["quiz_answers"] = {}
if "quiz_submitted" not in st.session_state:
    st.session_state["quiz_submitted"] = False
if "complexity" not in st.session_state:
    st.session_state["complexity"] = None
if "code_hash" not in st.session_state:
    st.session_state["code_hash"] = ""
if "code_input" not in st.session_state:
    st.session_state["code_input"] = ""

# ===== SIDEBAR =====
with st.sidebar:
    st.title("🧠 AI Code Explainer")
    st.caption("Understand any code instantly")
    st.divider()
    
    languages = [
        "Auto Detect",
        # Systems & Low-level
        "Python", "C", "C++", "C#", "Rust", "Go",
        # JVM
        "Java", "Kotlin", "Scala", "Groovy",
        # Web Frontend
        "JavaScript", "TypeScript", "HTML", "CSS",
        # Web Frameworks (treat as JS/TS)
        "React (JSX)", "Vue", "Svelte",
        # Mobile
        "Swift", "Dart (Flutter)", "Objective-C",
        # Scripting & Shell
        "Bash", "PowerShell", "Perl", "Ruby",
        # Data & ML
        "R", "MATLAB", "Julia",
        # Database
        "SQL", "PostgreSQL", "MongoDB (Query)",
        # Functional
        "Haskell", "Elixir", "Erlang", "Clojure", "F#",
        # Other popular
        "PHP", "Lua", "Zig", "Assembly (x86)",
        # Markup & Config
        "YAML", "TOML", "JSON", "XML", "Markdown",
        # Hardware
        "VHDL", "Verilog",
    ]
    
    selected_language = st.selectbox("Language", languages)
    
    model = st.selectbox(
        "Model",
        ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "gemma2-9b-it"]
    )
    
    st.divider()
    st.markdown("<small>Powered by Groq + Streamlit</small>", unsafe_allow_html=True)

# ===== MAIN AREA =====
st.header("Paste your code below")

# --- File Upload ---
uploaded_file = st.file_uploader(
    "Upload a source code file",
    type=["py","js","ts","jsx","tsx","cpp","c","java","kt","go",
          "rs","rb","php","swift","cs","html","css","sql","sh",
          "r","lua","zig","dart","scala","hs","ex","erl",
          "yaml","toml","json","xml","md"],
    help="Supported: 35+ file types"
)

EXTENSION_MAP = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
    ".jsx": "React (JSX)", ".tsx": "React (JSX)", ".cpp": "C++",
    ".c": "C", ".java": "Java", ".kt": "Kotlin", ".go": "Go",
    ".rs": "Rust", ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
    ".cs": "C#", ".html": "HTML", ".css": "CSS", ".sql": "SQL",
    ".sh": "Bash", ".r": "R", ".lua": "Lua", ".zig": "Zig",
    ".dart": "Dart (Flutter)", ".scala": "Scala", ".hs": "Haskell",
    ".ex": "Elixir", ".erl": "Erlang", ".yaml": "YAML",
    ".toml": "TOML", ".json": "JSON", ".xml": "XML", ".md": "Markdown"
}

if uploaded_file:
    # Only update on new file upload to prevent overriding edits
    if st.session_state.get("last_uploaded_file") != uploaded_file.name:
        content = uploaded_file.getvalue().decode("utf-8")
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        detected_lang = EXTENSION_MAP.get(ext, "Auto Detect")
        st.session_state["code_input"] = content
        st.session_state["last_uploaded_file"] = uploaded_file.name
        st.success(f"✅ Loaded {uploaded_file.name} — detected as {detected_lang}")

# --- Code Input ---
code_input = st.text_area(
    "Code",
    value=st.session_state.get("code_input", ""),
    height=300,
    placeholder="# paste your code here... supports 40+ languages",
    label_visibility="collapsed"
)
st.session_state["code_input"] = code_input

# --- Detect code change via hash ---
current_hash = hashlib.md5(code_input.encode("utf-8")).hexdigest()
if current_hash != st.session_state["code_hash"]:
    st.session_state["explanation"] = ""
    st.session_state["improvement"] = ""
    st.session_state["optimized"] = ""
    st.session_state["improved_code_only"] = ""
    st.session_state["chat_history"] = []
    st.session_state["quiz"] = None
    st.session_state["quiz_answers"] = {}
    st.session_state["quiz_submitted"] = False
    st.session_state["complexity"] = None
    st.session_state["code_hash"] = current_hash

# --- Buttons Row ---
col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
btn_explain = col1.button("🔍 Explain Code", use_container_width=True)
btn_improve = col2.button("✨ Improve Code", use_container_width=True)
btn_optimize = col3.button("⚡ Optimized Version", use_container_width=True)
btn_quiz = col4.button("🧠 Take Quiz", use_container_width=True)
btn_complexity = col5.button("📊 Complexity", use_container_width=True)

if any([btn_explain, btn_improve, btn_optimize, btn_quiz, btn_complexity]):
    if not code_input.strip():
        st.warning("Please paste some code first")
        st.stop()

def resolve_language():
    """Helper to detect language if Auto Detect is selected."""
    lang = selected_language
    if lang == "Auto Detect":
        sys_p, usr_p = get_autodetect_prompt(code_input)
        detected = query_groq(sys_p, usr_p, model)
        lang = detected.strip()
    return lang

# --- FEATURE 1: Streaming Explain & Optimize ---
if btn_explain:
    lang = resolve_language()
    sys_p, usr_p = get_explanation_prompt(code_input, lang)
    with st.expander("📖 Explanation", expanded=True):
        result = st.write_stream(stream_groq(sys_p, usr_p, model))
        st.session_state["explanation"] = result
    st.success("Done!")
elif st.session_state["explanation"]:
    with st.expander("📖 Explanation", expanded=True):
        st.markdown(st.session_state["explanation"])

if btn_optimize:
    lang = resolve_language()
    sys_p, usr_p = get_optimization_prompt(code_input, lang)
    with st.expander("⚡ Optimized Version", expanded=True):
        result = st.write_stream(stream_groq(sys_p, usr_p, model))
        st.session_state["optimized"] = result
    st.success("Done!")
elif st.session_state["optimized"]:
    with st.expander("⚡ Optimized Version", expanded=True):
        st.markdown(st.session_state["optimized"])

# --- FEATURE 2: Improve Code + Diff Viewer ---
if btn_improve:
    lang = resolve_language()
    sys_p, usr_p = get_improvement_prompt(code_input, lang)
    with st.expander("✨ Improvements", expanded=True):
        result = st.write_stream(stream_groq(sys_p, usr_p, model))
        st.session_state["improvement"] = result
    
    if "## IMPROVED_CODE_ONLY" in result:
        parts = result.split("## IMPROVED_CODE_ONLY")
        if len(parts) > 1:
            st.session_state["improved_code_only"] = parts[1].strip()
    st.success("Done!")
elif st.session_state["improvement"]:
    with st.expander("✨ Improvements", expanded=True):
        st.markdown(st.session_state["improvement"])

if st.session_state["improved_code_only"]:
    with st.expander("🔀 Side-by-Side Diff Viewer", expanded=True):
        col1_diff, col2_diff = st.columns(2)
        lang_tag = selected_language.lower().split()[0] if selected_language != "Auto Detect" else "python"
        with col1_diff:
            st.markdown("**Original Code**")
            st.code(code_input, language=lang_tag)
        with col2_diff:
            st.markdown("**Improved Code**")
            st.code(st.session_state["improved_code_only"], language=lang_tag)
        
        orig_lines = code_input.splitlines()
        impr_lines = st.session_state["improved_code_only"].splitlines()
        diff = list(difflib.unified_diff(orig_lines, impr_lines, lineterm=""))
        added = len([l for l in diff if l.startswith("+") and not l.startswith("+++")])
        removed = len([l for l in diff if l.startswith("-") and not l.startswith("---")])
        st.caption(f"+ {added} lines added · - {removed} lines removed")

# --- FEATURE 3: Complexity Visualizer ---
if btn_complexity:
    lang = resolve_language()
    sys_p, usr_p = get_complexity_prompt(code_input, lang)
    with st.spinner("Analyzing complexity..."):
        raw = query_groq(sys_p, usr_p, model)
    try:
        data = json.loads(raw)
        st.session_state["complexity"] = data
    except Exception as e:
        st.error(f"Complexity analysis failed. Try again. Error: {e}")

if st.session_state["complexity"]:
    with st.expander("📊 Complexity Analysis", expanded=True):
        data = st.session_state["complexity"]
        
        COMPLEXITY_LABELS = [
            "O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n²)", "O(2^n)", "O(n!)"
        ]
        COMPLEXITY_COLORS = [
            "#00C851", "#33b5e5", "#ffbb33", "#FF8800", "#ff4444", "#CC0000", "#880000"
        ]
        
        col1_comp, col2_comp = st.columns(2)
        
        with col1_comp:
            st.markdown(f"### ⏱ Time: `{data.get('time_complexity', 'Unknown')}`")
            st.caption(data.get("time_explanation", ""))
            
            fig, ax = plt.subplots(figsize=(5, 1.2))
            fig.patch.set_facecolor('#0F0F0F')
            ax.set_facecolor('#1A1A1A')
            for i, (label, color) in enumerate(zip(COMPLEXITY_LABELS, COMPLEXITY_COLORS)):
                ax.barh(0, 1, left=i, color=color, edgecolor='none', height=0.6)
            rank = data.get("time_rank", 1)
            ax.barh(0, 1.2, left=rank-1, color='white', edgecolor='none', height=0.8, alpha=0.3)
            ax.set_xlim(0, 7)
            ax.set_yticks([])
            ax.set_xticks(range(7))
            ax.set_xticklabels(COMPLEXITY_LABELS, fontsize=7, color='white', rotation=20)
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_visible(False)
            st.pyplot(fig)
            plt.close()
        
        with col2_comp:
            st.markdown(f"### 💾 Space: `{data.get('space_complexity', 'Unknown')}`")
            st.caption(data.get("space_explanation", ""))
            
            fig, ax = plt.subplots(figsize=(5, 1.2))
            fig.patch.set_facecolor('#0F0F0F')
            ax.set_facecolor('#1A1A1A')
            for i, (label, color) in enumerate(zip(COMPLEXITY_LABELS, COMPLEXITY_COLORS)):
                ax.barh(0, 1, left=i, color=color, edgecolor='none', height=0.6)
            rank = data.get("space_rank", 1)
            ax.barh(0, 1.2, left=rank-1, color='white', edgecolor='none', height=0.8, alpha=0.3)
            ax.set_xlim(0, 7)
            ax.set_yticks([])
            ax.set_xticks(range(7))
            ax.set_xticklabels(COMPLEXITY_LABELS, fontsize=7, color='white', rotation=20)
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_visible(False)
            st.pyplot(fig)
            plt.close()

# --- FEATURE 5: Code Quiz ---
if btn_quiz:
    lang = resolve_language()
    sys_p, usr_p = get_quiz_prompt(code_input, lang)
    with st.spinner("Generating quiz..."):
        raw = query_groq(sys_p, usr_p, model)
    try:
        quiz_data = json.loads(raw)
        st.session_state["quiz"] = quiz_data.get("questions", [])
        st.session_state["quiz_answers"] = {}
        st.session_state["quiz_submitted"] = False
    except Exception as e:
        st.error(f"Quiz generation failed. Try again. Error: {e}")

if st.session_state["quiz"]:
    questions = st.session_state["quiz"]
    with st.expander("🧠 Code Quiz", expanded=True):
        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}: {q['question']}**")
            answer = st.radio(
                f"Select answer for Q{i+1}",
                q["options"],
                key=f"quiz_q_{i}",
                label_visibility="collapsed"
            )
            st.session_state["quiz_answers"][i] = answer
        
        if st.button("Submit Quiz", key="submit_quiz"):
            st.session_state["quiz_submitted"] = True
        
        if st.session_state.get("quiz_submitted"):
            score = 0
            for i, q in enumerate(questions):
                user_ans = st.session_state["quiz_answers"].get(i, "")
                is_correct = user_ans.startswith(q["correct"])
                if is_correct:
                    score += 1
                    st.success(f"Q{i+1}: ✅ {q.get('explanation', '')}")
                else:
                    st.error(f"Q{i+1}: ❌ Correct: {q['correct']}. {q.get('explanation', '')}")
            
            st.markdown(f"### 🎯 Score: {score}/4")
            if score == 4:
                st.balloons()

# --- FEATURE 4: Chat with your Code ---
# Only show if there's an explanation available
if st.session_state["explanation"]:
    st.divider()
    st.markdown("### 💬 Chat with your Code")
    st.caption("Ask follow-up questions about this code")

    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_q = st.chat_input("Ask about this code... e.g. 'Why is this O(n²)?'")

    if user_q:
        # Display user msg immediately
        st.session_state["chat_history"].append({"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.markdown(user_q)
            
        lang = resolve_language() if selected_language == "Auto Detect" else selected_language
        sys_p, usr_p = get_chat_prompt(
            code=code_input,
            language=lang,
            explanation=st.session_state["explanation"],
            chat_history=st.session_state["chat_history"],
            user_question=user_q
        )
        with st.chat_message("assistant"):
            response = st.write_stream(stream_groq(sys_p, usr_p, model))
        st.session_state["chat_history"].append({"role": "assistant", "content": response})
        st.rerun()

    if st.session_state["chat_history"]:
        if st.button("🗑 Clear Chat"):
            st.session_state["chat_history"] = []
            st.rerun()
