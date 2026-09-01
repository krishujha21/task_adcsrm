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
        f"Code:\n```{language}\n{code}\n```"
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
        "(The full improved code with inline comments explaining each change.)\n\n"
        "IMPORTANT: At the very end of your response, after all explanations, "
        "add a section with this exact header:\n"
        "## IMPROVED_CODE_ONLY\n"
        "Then provide ONLY the complete improved code — no explanation, "
        "no markdown fences, no comments about changes. Raw code only. "
        "This section will be parsed programmatically."
    )

    user_prompt = (
        f"Language: {language}\n\n"
        f"Code:\n```{language}\n{code}\n```"
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
        f"Code:\n```{language}\n{code}\n```"
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


def get_chat_prompt(
    code: str,
    language: str,
    explanation: str,
    chat_history: list,
    user_question: str,
) -> tuple:
    """Build prompts for conversational follow-up about the code.

    Args:
        code: The raw source code being discussed.
        language: The programming language.
        explanation: The initial explanation already given to the user.
        chat_history: List of dicts ``[{"role": "user"/"assistant", "content": "..."}]``.
        user_question: The user's current follow-up question.

    Returns:
        A ``(system_prompt, user_prompt)`` tuple.
    """
    system_prompt = (
        "You are a patient, expert programming tutor having a conversation "
        "about a specific piece of code. The user has already received an explanation "
        "and is now asking follow-up questions.\n\n"
        "Rules:\n"
        "- Answer only about the provided code\n"
        "- Be concise but complete\n"
        "- Use markdown for code snippets\n"
        "- Reference specific line numbers when relevant\n"
        "- If asked something unrelated to the code, redirect politely"
    )

    user_prompt = (
        f"Language: {language}\n\n"
        f"Code:\n```{language}\n{code}\n```\n\n"
        f"Initial Explanation Already Given:\n{explanation}\n\n"
        f"Now answer the user's follow-up question: {user_question}"
    )

    return system_prompt, user_prompt


def get_quiz_prompt(code: str, language: str) -> tuple:
    """Generate 4 MCQ questions from the provided code.

    The LLM is instructed to respond in strict JSON format for
    programmatic parsing.

    Args:
        code: The raw source code to quiz about.
        language: The programming language.

    Returns:
        A ``(system_prompt, user_prompt)`` tuple.
    """
    system_prompt = (
        "You are a programming educator. Generate exactly 4 multiple choice "
        "questions about the provided code.\n\n"
        "Respond ONLY in this exact JSON format. No markdown fences. No extra text. No preamble:\n"
        '{\n'
        '  "questions": [\n'
        '    {\n'
        '      "question": "What does this function return when input is 0?",\n'
        '      "options": ["A) 0", "B) 1", "C) None", "D) Error"],\n'
        '      "correct": "A",\n'
        '      "explanation": "Because the base case returns 0..."\n'
        '    }\n'
        '  ]\n'
        '}\n\n'
        "Rules:\n"
        "- Questions must be specific to THIS code, not generic\n"
        "- Mix question types: output prediction, complexity, variable purpose, edge cases\n"
        "- All 4 options must be plausible\n"
        "- Explanation must reference the actual code\n"
        "- Respond with pure JSON only — no markdown, no backticks, nothing else"
    )

    user_prompt = (
        f"Language: {language}\n\n"
        f"Code:\n```{language}\n{code}\n```\n\n"
        "Generate 4 MCQ questions about this specific code. Respond in JSON only."
    )

    return system_prompt, user_prompt


def get_complexity_prompt(code: str, language: str) -> tuple:
    """Extract time and space complexity for visualization.

    The LLM is instructed to respond in strict JSON format with
    complexity values and numeric ranks for chart rendering.

    Args:
        code: The raw source code to analyze.
        language: The programming language.

    Returns:
        A ``(system_prompt, user_prompt)`` tuple.
    """
    system_prompt = (
        "You are an algorithms expert. Analyze the provided code and return "
        "complexity information in strict JSON format.\n\n"
        "Respond ONLY in this exact JSON format. No markdown. No extra text. No preamble:\n"
        '{\n'
        '  "time_complexity": "O(n log n)",\n'
        '  "space_complexity": "O(n)",\n'
        '  "time_explanation": "The outer loop runs n times, inner sort is O(log n)...",\n'
        '  "space_explanation": "We store n elements in the auxiliary array...",\n'
        '  "time_rank": 4,\n'
        '  "space_rank": 4\n'
        '}\n\n'
        "time_rank and space_rank must be integers 1-7 mapping to:\n"
        "1 = O(1)\n"
        "2 = O(log n)\n"
        "3 = O(n)\n"
        "4 = O(n log n)\n"
        "5 = O(n²)\n"
        "6 = O(2^n)\n"
        "7 = O(n!)\n\n"
        "Respond with pure JSON only."
    )

    user_prompt = (
        f"Language: {language}\n\n"
        f"Code:\n```{language}\n{code}\n```\n\n"
        "Analyze time and space complexity. Respond in JSON only."
    )

    return system_prompt, user_prompt
