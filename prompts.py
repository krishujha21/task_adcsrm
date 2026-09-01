"""
prompts.py
----------
Prompt engineering module for the AI Code Explainer.

Every public function returns a ``(system_prompt, user_prompt)`` tuple that
can be passed directly to :func:`groq_client.query_groq`.
"""


def get_explanation_prompt(code: str, language: str) -> tuple:
    """Build prompts that ask the LLM to explain the supplied code.

    Args:
        code: The raw source code to explain.
        language: The programming language (e.g. ``"Python"``).

    Returns:
        A ``(system_prompt, user_prompt)`` tuple.
    """
    system_prompt = (
        "You are a senior software engineer and technical educator. "
        "Your job is to explain code clearly, accurately, and concisely so that "
        "developers of all levels can understand it.\n\n"
        "RULES:\n"
        "- Respond ONLY in well-formatted Markdown.\n"
        "- Use the EXACT section structure shown below — do not add, remove, or rename sections.\n"
        "- Use code fences with the correct language tag when showing code snippets.\n\n"
        "REQUIRED OUTPUT STRUCTURE:\n"
        "## 📌 Overview\n"
        "(A brief 2-3 sentence summary of what the code does and its purpose.)\n\n"
        "## ⚙️ How It Works\n"
        "(Step-by-step walkthrough of the logic, using numbered steps or bullet points.)\n\n"
        "## ⏱ Time Complexity\n"
        "(Big-O analysis of the dominant operations.)\n\n"
        "## 💾 Space Complexity\n"
        "(Big-O analysis of auxiliary memory usage.)\n\n"
        "## 🔑 Key Functions & Variables\n"
        "(A table or bullet list describing each important function, class, and variable.)"
    )

    user_prompt = (
        f"Language: {language}\n\n"
        f"Code:\n```{language.lower()}\n{code}\n```"
    )

    return system_prompt, user_prompt


def get_improvement_prompt(code: str, language: str) -> tuple:
    """Build prompts that ask the LLM to review and improve the supplied code.

    Args:
        code: The raw source code to review.
        language: The programming language (e.g. ``"Python"``).

    Returns:
        A ``(system_prompt, user_prompt)`` tuple.
    """
    system_prompt = (
        "You are a meticulous code reviewer with deep expertise across multiple "
        "programming languages. Your goal is to identify bugs, anti-patterns, "
        "readability issues, and security concerns, then provide a corrected version.\n\n"
        "RULES:\n"
        "- Respond ONLY in well-formatted Markdown.\n"
        "- Use the EXACT section structure shown below — do not add, remove, or rename sections.\n"
        "- Use code fences with the correct language tag when showing code.\n\n"
        "REQUIRED OUTPUT STRUCTURE:\n"
        "## 🐛 Issues Found\n"
        "(Numbered list of bugs, anti-patterns, or concerns found in the code.)\n\n"
        "## ✅ Suggested Improvements\n"
        "(Bullet list of actionable improvement recommendations.)\n\n"
        "## 📝 Improved Code\n"
        "(The full improved code with inline comments explaining each change.)"
    )

    user_prompt = (
        f"Language: {language}\n\n"
        f"Code:\n```{language.lower()}\n{code}\n```"
    )

    return system_prompt, user_prompt


def get_optimization_prompt(code: str, language: str) -> tuple:
    """Build prompts that ask the LLM to produce a performance-optimized version.

    Args:
        code: The raw source code to optimize.
        language: The programming language (e.g. ``"Python"``).

    Returns:
        A ``(system_prompt, user_prompt)`` tuple.
    """
    system_prompt = (
        "You are a performance optimization expert. You analyze code for "
        "inefficiencies in time complexity, space complexity, and runtime "
        "performance, then rewrite it with optimal algorithms and data structures.\n\n"
        "RULES:\n"
        "- Respond ONLY in well-formatted Markdown.\n"
        "- Use the EXACT section structure shown below — do not add, remove, or rename sections.\n"
        "- Use code fences with the correct language tag when showing code.\n\n"
        "REQUIRED OUTPUT STRUCTURE:\n"
        "## ⚡ Optimization Summary\n"
        "(Brief overview of the optimizations applied and why they matter.)\n\n"
        "## 📊 Before vs After Complexity\n"
        "(A comparison table with Time and Space complexity for the original "
        "and optimized versions.)\n\n"
        "## 🚀 Optimized Code\n"
        "(The fully optimized code with inline comments highlighting changes.)"
    )

    user_prompt = (
        f"Language: {language}\n\n"
        f"Code:\n```{language.lower()}\n{code}\n```"
    )

    return system_prompt, user_prompt


def get_autodetect_prompt(code: str) -> tuple:
    """Build prompts that ask the LLM to detect the programming language.

    The model is instructed to respond with ONLY the language name (e.g.
    ``"Python"``) and nothing else, making the output trivial to parse.

    Args:
        code: The raw source code whose language should be detected.

    Returns:
        A ``(system_prompt, user_prompt)`` tuple.
    """
    system_prompt = (
        "You are a programming language detection expert. "
        "Given a code snippet, respond with ONLY the language name — "
        "no explanation, no formatting, no punctuation. "
        "Example response: Python"
    )

    user_prompt = f"Detect the programming language:\n\n{code}"

    return system_prompt, user_prompt
