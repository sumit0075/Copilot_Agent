import ollama
from pathlib import Path

CODE_FILE = "test_code.py"  # Replace with your Python file path

# ---------------- LLM Analysis ----------------
def get_advanced_code_corrections(code_snippet: str):
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
\"\"\"
{code_snippet}
\"\"\"
"""
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content']


# ---------------- Extract Corrected Code ----------------
def extract_corrected_code(llm_response: str) -> str:
    """
    Extract only the code from the LLM response (after 'CORRECTED CODE:').
    """
    import re
    match = re.search(r"CORRECTED CODE:\s*```(?:python)?\s*(.*?)```", llm_response, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        # If no code block formatting, return everything after "CORRECTED CODE:"
        parts = llm_response.split("CORRECTED CODE:")
        return parts[1].strip() if len(parts) > 1 else ""

# ---------------- Backup & Overwrite ----------------
def backup_and_overwrite(file_path: Path, corrected_code: str):
    backup_path = file_path.with_name("backup.py")  # Backup in same folder
    file_path.replace(backup_path)  # Move original to backup
    file_path.write_text(corrected_code, encoding="utf-8")  # Overwrite with corrected code
    print(f"✅ Original file overwritten. Backup saved as '{backup_path.name}'.")

# ---------------- Main ----------------
path = Path(CODE_FILE)
if not path.is_file():
    print(f"❌ File not found: {CODE_FILE}")
else:
    code_content = path.read_text(encoding="utf-8")
    llm_feedback = get_advanced_code_corrections(code_content)

    # Print full feedback in terminal
    print("💡 LLM Feedback:\n")
    print(llm_feedback)

    # Extract only the corrected code and overwrite file
    corrected_code = extract_corrected_code(llm_feedback)
    if corrected_code:
        backup_and_overwrite(path, corrected_code)
    else:
        print("⚠️ Could not extract corrected code from LLM response.")





