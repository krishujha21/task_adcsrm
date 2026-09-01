import streamlit as st
import hashlib

from groq_client import query_groq
from prompts import (
    get_explanation_prompt,
    get_improvement_prompt,
    get_optimization_prompt,
    get_autodetect_prompt
)

st.set_page_config(
    page_title="AI Code Explainer",
    page_icon="🧠",
    layout="wide"
)

# Initialize Session State
if "explanation" not in st.session_state:
    st.session_state.explanation = ""
if "improvement" not in st.session_state:
    st.session_state.improvement = ""
if "optimized" not in st.session_state:
    st.session_state.optimized = ""
if "last_code_hash" not in st.session_state:
    st.session_state.last_code_hash = ""

def get_code_hash(code_string):
    return hashlib.md5(code_string.encode("utf-8")).hexdigest()

# Sidebar
with st.sidebar:
    st.title("🧠 AI Code Explainer")
    st.caption("Understand any code instantly")
    st.divider()
    
    language = st.selectbox(
        "Language",
        ["Auto Detect", "Python", "C++", "Java", "JavaScript", "TypeScript", "Go", "Rust"]
    )
    
    model = st.selectbox(
        "Model",
        ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "gemma2-9b-it"]
    )
    
    st.divider()
    st.markdown("<small>Powered by Groq + Streamlit</small>", unsafe_allow_html=True)

# Main Area
st.header("Paste your code below")

code_input = st.text_area("Code", height=300, placeholder="# paste your code here...", label_visibility="collapsed")

# Clear results if code input changes
current_hash = get_code_hash(code_input) if code_input else ""
if current_hash != st.session_state.last_code_hash:
    st.session_state.explanation = ""
    st.session_state.improvement = ""
    st.session_state.optimized = ""
    st.session_state.last_code_hash = current_hash

# Action Buttons
col1, col2, col3 = st.columns([1, 1, 1])

def process_action(prompt_func, state_key):
    """Run a prompt function → Groq pipeline and store the result in session state."""
    if not code_input.strip():
        st.warning("Please paste some code first")
        return

    try:
        with st.spinner("Thinking..."):
            # Resolve language when Auto Detect is selected
            resolved_language = language
            if language == "Auto Detect":
                detect_sys, detect_usr = get_autodetect_prompt(code_input)
                resolved_language = query_groq(detect_sys, detect_usr, model).strip()

            # Build the actual prompt pair and call Groq
            system_prompt, user_prompt = prompt_func(code_input, language=resolved_language)
            result = query_groq(system_prompt, user_prompt, model)
            st.session_state[state_key] = result

        st.toast("Done!", icon="✅")
    except RuntimeError as e:
        st.error(f"{str(e)}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

with col1:
    if st.button("🔍 Explain Code", use_container_width=True):
        process_action(get_explanation_prompt, "explanation")

with col2:
    if st.button("✨ Improve Code", use_container_width=True):
        process_action(get_improvement_prompt, "improvement")

with col3:
    if st.button("⚡ Optimized Version", use_container_width=True):
        process_action(get_optimization_prompt, "optimized")

# Results Section
if st.session_state.explanation:
    with st.expander("📖 Explanation", expanded=True):
        st.markdown(st.session_state.explanation)

if st.session_state.improvement:
    with st.expander("✨ Improvements", expanded=True):
        st.markdown(st.session_state.improvement)

if st.session_state.optimized:
    with st.expander("⚡ Optimized Version", expanded=True):
        st.markdown(st.session_state.optimized)
