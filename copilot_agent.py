# # import ollama
# # import time
# # from watchdog.observers import Observer
# # from watchdog.events import FileSystemEventHandler

# # CODE_FILE = "test_code.py"  # file to monitor and analyze

# # def analyze_code(code):
# #     """
# #     Sends the code to the local LLM and gets suggestions, corrections, or rewrites.
# #     """
# #     prompt = f"""
# # You are an AI code assistant like VS Code Copilot.
# # Analyze the following Python code and:
# # 1. Suggest improvements, corrections, or optimizations.
# # 2. Detect possible bugs or logical errors.
# # 3. If any part of the code needs to be rewritten, provide the corrected code version.

# # Code:
# # {code}

# # Your response should include:
# # - Suggestions section
# # - Rewritten code (if needed)
# # """

# #     # Debug print before LLM call
# #     print("Detected file change! Sending to LLM...")

# #     start = time.time()
# #     response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
# #     end = time.time()

# #     # Debug print after LLM response
# #     print(f"✅ LLM has responded in {end - start:.2f} seconds\n")

# #     return response['message']['content']


# # class CodeChangeHandler(FileSystemEventHandler):
# #     def on_modified(self, event):
# #         if event.src_path.endswith(CODE_FILE):
# #             print("\n🧩 Detected changes in code file... Analyzing...\n")
# #             with open(CODE_FILE, "r", encoding="utf-8") as f:
# #                 code = f.read()
# #             result = analyze_code(code)
# #             print("💡 LLM Feedback:\n")
# #             print(result)
# #             print("\n✅ Analysis complete.\n")


# # if __name__ == "__main__":
# #     print("🚀 Local Copilot Agent running...")
# #     print(f"Monitoring file: {CODE_FILE}\n")

# #     event_handler = CodeChangeHandler()
# #     observer = Observer()
# #     observer.schedule(event_handler, ".", recursive=False)
# #     observer.start()

# #     try:
# #         while True:
# #             time.sleep(1)
# #     except KeyboardInterrupt:
# #         observer.stop()
# #     observer.join()

# import ollama
# import time
# from watchdog.observers import Observer
# from watchdog.events import FileSystemEventHandler
# from pathlib import Path
# import difflib
# import shutil

# CODE_FILE = "test_code.py"  # file to monitor and analyze

# # ---------------- Helper functions ----------------
# def backup_and_write(path: Path, content: str):
#     """Create a backup and write new content to the file."""
#     bak = path.with_suffix(path.suffix + ".bak")
#     shutil.copy2(path, bak)
#     path.write_text(content, encoding="utf-8")
#     print(f"✅ File updated: {path} (backup saved as {bak})")

# def make_diff(original, updated, filename):
#     """Return a unified diff between original and updated code."""
#     return list(difflib.unified_diff(
#         original.splitlines(keepends=True),
#         updated.splitlines(keepends=True),
#         fromfile=f"{filename} (original)",
#         tofile=f"{filename} (LLM suggestion)",
#         lineterm=''
#     ))

# # ---------------- LLM Analysis ----------------
# def analyze_code(code):
#     """
#     Sends the code to the local LLM and gets suggestions, corrections, or rewrites.
#     """
#     prompt = f"""
# You are an AI code assistant like VS Code Copilot.
# Analyze the following Python code and:
# 1. Suggest improvements, corrections, or optimizations.
# 2. Detect possible bugs or logical errors.
# 3. If any part of the code needs to be rewritten, provide the corrected code version.

# Code:
# {code}

# Return the corrected full code only.
# """

#     # Debug print before LLM call
#     print("Detected file change! Sending to LLM...")

#     start = time.time()
#     response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
#     end = time.time()

#     # Debug print after LLM response
#     print(f"✅ LLM has responded in {end - start:.2f} seconds\n")

#     return response['message']['content']

# # ---------------- Watchdog Handler ----------------
# class CodeChangeHandler(FileSystemEventHandler):
#     def on_modified(self, event):
#         if event.src_path.endswith(CODE_FILE):
#             print("\n🧩 Detected changes in code file... Analyzing...\n")
#             path = Path(CODE_FILE)
#             original_code = path.read_text(encoding="utf-8")

#             suggested_code = analyze_code(original_code)

#             # Show diff for user review
#             if suggested_code and suggested_code != original_code:
#                 print("===== DIFF =====")
#                 for line in make_diff(original_code, suggested_code, CODE_FILE):
#                     print(line.rstrip())

#                 # Interactive prompt
#                 choice = input("\nDo you want to apply these changes? (y/n): ").strip().lower()
#                 if choice == 'y':
#                     backup_and_write(path, suggested_code)
#                 else:
#                     print("❌ Changes were not applied.")
#             else:
#                 print("No changes suggested by LLM.")

# # ---------------- Main ----------------
# if __name__ == "__main__":
#     print("🚀 Local Copilot Agent running...")
#     print(f"Monitoring file: {CODE_FILE}\n")

#     event_handler = CodeChangeHandler()
#     observer = Observer()
#     observer.schedule(event_handler, ".", recursive=False)
#     observer.start()

#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         observer.stop()
#     observer.join()











# import ollama
# from pathlib import Path

# CODE_FILE = "test_code.py"  # Replace with your Python file path

# def get_code_corrections(code_snippet: str):
#     prompt = f"""
# You are an AI programming assistant like VS Code Copilot.
# I will provide a Python code snippet. Your task is:

# 1. Detect any errors, bugs, or issues (syntax errors, logical errors, wrong variable usage, missing imports, etc.).
# 2. Explain each error clearly and concisely.
# 3. Provide the corrected version of only the code that contains the error.

# Always respond in the following format:

# ERROR DETECTED:
# <Explain the error in detail, what it is, why it happens, and its impact.>

# CORRECTED CODE:
# <Provide only the corrected code snippet, no extra explanation.>

# Here is the code to analyze:
# \"\"\"
# {code_snippet}
# \"\"\"
# """
#     response = ollama.chat(
#         model="llama3.2",
#         messages=[{"role": "user", "content": prompt}]
#     )
#     return response['message']['content']  # Adjust if Ollama returns 'content' instead

# # ---------------- Read file and analyze ----------------
# path = Path(CODE_FILE)
# if not path.is_file():
#     print(f"❌ File not found: {CODE_FILE}")
# else:
#     code_content = path.read_text(encoding="utf-8")
#     result = get_code_corrections(code_content)
#     print("💡 LLM Feedback:\n")
#     print(result)




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





