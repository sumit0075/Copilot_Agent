import ollama
from pathlib import Path
from typing import Optional


# ---------------- LLM Analysis ----------------
def get_advanced_code_corrections(code_snippet: str) -> str:
    """Send the code snippet to the LLM and return its full text response.

    This function returns the raw LLM response (string) so callers can display
    or further parse it.
    """
    prompt = f"""
You are an AI programming assistant like VS Code Copilot, with advanced error detection.
I will provide a Python code snippet. Your task is:

1. Detect all errors in the code, including:
   - Syntax errors
   - Logical errors
   - Wrong variable usage
   - Undefined variables
   - Missing imports
   - Missing lines or code blocks
2. For undefined variables or missing elements:
   - Suggest a default value or placeholder.
   - If possible, automatically define it to make the code runnable.
   - Clearly indicate to the user that this is a suggested placeholder.
3. Explain each error clearly and concisely, including:
   - What the error is
   - Why it happens
   - Its impact on the code
4. Provide a corrected version of the code, making it runnable if possible.
5. Always maintain the original logic unless it is broken.
6. Format your response exactly as below:

ERROR DETECTED:
<Explain all detected errors, including missing variables or lines.>

CORRECTED CODE:
<Provide only the corrected code snippet. For missing variables, include suggested default definitions with a comment '# Placeholder value, replace if needed'>

Here is the code to analyze:
"""
    prompt = prompt + f"""\n\n\"\"\"\n{code_snippet}\n\"\"\"\n"""
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]


# ---------------- Extract Corrected Code ----------------
def extract_corrected_code(llm_response: str) -> str:
    """Extract only the code from the LLM response (after 'CORRECTED CODE:').

    The LLM may format the corrected code as a fenced code block with or without
    a language. This function tries to handle typical formats and falls back to
    returning everything after the 'CORRECTED CODE:' marker.
    """
    import re
    # Try fenced code block first
    match = re.search(r"CORRECTED CODE:\s*```(?:python)?\s*(.*?)```", llm_response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback: everything after the marker
    parts = llm_response.split("CORRECTED CODE:")
    return parts[1].strip() if len(parts) > 1 else ""


# ---------------- Backup & Overwrite ----------------
def backup_and_overwrite(file_path: Path, corrected_code: str) -> None:
    """Backup the original file and overwrite it with corrected_code.

    The backup name is the original file name with a `.backup.py` suffix to
    avoid clobbering an existing `backup.py` file.
    """
    backup_path = file_path.with_suffix(file_path.suffix + ".backup.py")
    # Use replace to move original to backup (atomic on many systems).
    file_path.replace(backup_path)
    file_path.write_text(corrected_code, encoding="utf-8")
    return backup_path


def restore_backup(file_path: Path, backup_path: Path) -> None:
    """Restore a previously created backup over the current file.

    This will remove the current file (if present) and move the backup back
    to the original file path.
    """
    if backup_path.is_file():
        # Remove current file if it exists
        if file_path.is_file():
            file_path.unlink()
        backup_path.replace(file_path)
    else:
        raise FileNotFoundError(f"Backup file not found: {backup_path}")


# ---------------- Main / Script entry ----------------
def main(code_file: Optional[str] = None, do_overwrite: bool = True) -> None:
    """Run the full flow against `code_file`. If `code_file` is None, uses
    'test_code.py' in the current directory.
    """
    CODE_FILE = code_file or "test_code.py"
    path = Path(CODE_FILE)
    if not path.is_file():
        print(f"❌ File not found: {CODE_FILE}")
        return

    code_content = path.read_text(encoding="utf-8")
    llm_feedback = get_advanced_code_corrections(code_content)

    # Print full feedback in terminal
    print("💡 LLM Feedback:\n")
    print(llm_feedback)

    # Extract only the corrected code and optionally overwrite file
    corrected_code = extract_corrected_code(llm_feedback)
    if corrected_code:
        if do_overwrite:
            backup_and_overwrite(path, corrected_code)
            print(f"✅ Original file overwritten. Backup saved as '{path.with_suffix(path.suffix + ".backup.py").name}'.")
        else:
            print("✅ Corrected code extracted (overwrite disabled).")
    else:
        print("⚠️ Could not extract corrected code from LLM response.")


if __name__ == "__main__":
    main()





