from typing import Tuple
import ollama
from copilot_agent import extract_corrected_code


def apply_user_prompt(code_text: str, user_prompt: str, model: str = "llama3.2") -> Tuple[str, str]:
    """Send a combined prompt + code to the LLM and return (full_response, modified_code).

    The function sends the user's instruction followed by the code. The LLM is expected
    to return a section titled 'CORRECTED CODE:' containing the modified code (similar
    to the main analysis format). The function returns the raw response and the
    extracted code (empty string if extraction fails).
    """
    prompt = f"""
User instruction:
{user_prompt}

Apply the instruction to the following Python code and return the full modified file or the modified functions.

CODE:
"""
    prompt = prompt + f"""\n\n\"\"\"\n{code_text}\n\"\"\"\n"""

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    llm_response = response["message"]["content"]
    modified = extract_corrected_code(llm_response)
    if not modified:
        # Fallback: remove common markdown fences and use the body as modified code
        import re
        # Remove triple-backtick fences and optional language tags
        cleaned = re.sub(r"```(?:python)?\n", "", llm_response, flags=re.IGNORECASE)
        cleaned = re.sub(r"\n```", "", cleaned)
        # Strip leading/trailing whitespace
        modified = cleaned.strip()
    return llm_response, modified
