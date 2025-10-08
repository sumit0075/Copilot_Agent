# Local Copilot Agent

Small utility that can either run as a file-watching agent or via a Streamlit frontend to send Python files to a local Ollama model for suggested corrections and optionally apply those corrections (creating a backup).

## Prerequisites

- Python 3.8+ (the repo includes a virtual env `myenv` as an example)
- Ollama installed and a compatible local model (e.g. `llama3.2`) and Ollama daemon running

## Setup (Windows PowerShell)

1. Activate the virtual environment (if you want to use the included `myenv`):

```powershell
.# from the repository root
.\myenv\Scripts\Activate.ps1
```

2. Install Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Streamlit frontend

A Streamlit UI is provided at `streamlit_app.py` to pick a Python file from a local directory, preview it, send it to the local Ollama model for analysis, view the full LLM feedback and the extracted corrected code, and optionally overwrite the file while creating a backup.

Run the app from the `Copilot_Agent` directory:

```powershell
streamlit run .\streamlit_app.py
```

UI summary:
- Left column: directory picker, file select dropdown, "Analyze" button, LLM feedback, and extracted corrected code.
- Right column: preview of the selected file.
- Overwrite option: if enabled the corrected code will replace the original file and a backup will be created next to the original file with a `.backup.py` suffix.

Notes:
- The Streamlit app calls the same `copilot_agent` functions and therefore requires `ollama` to be configured and a compatible model available locally.
- The app lists `.py` files in the given directory (non-recursive by default).

User Prompt mode
-----------------

The Streamlit frontend also includes a "User prompt" mode where you can type a custom instruction for the model (for example: "Make this code more robust and add type hints"). When you run the prompt on a selected file the app will:

- Send a combined prompt + file contents to the local Ollama model.
- Display the full model response and attempt to extract the corrected code (it prefers a `CORRECTED CODE:` block but will fall back to using the raw response cleaned of Markdown fences).
- Persist the last LLM response and the last extracted/cleaned modified code in the Streamlit session so you can apply or undo changes.

Apply & Undo workflow
---------------------

To avoid accidental overwrites, the app requires an explicit Apply action:

1. Run Analyze or User prompt.
2. Review the "Modified Code (last run)" pane.
3. Click "Apply stored modified code to file" to write the changes to disk. A backup file will be created next to the original named `yourfile.py.backup.py`.
4. If you want to revert immediately, click "Undo last overwrite" (appears after a successful Apply) to restore the backup.

Notes about backups and session state:
- The app stores the last backup path and the last modified content in `st.session_state` for the current Streamlit session. If you reload/close the app the session state is lost but the backup file remains on disk.
- Backups currently use a fixed suffix (`.backup.py`). If you want time-stamped or incremental backups, I can add that option.

Example user prompts
--------------------
- "Make this function handle invalid inputs and add type annotations."
- "Optimize this loop for large inputs and document complexity." 
- "Refactor this module to reduce duplication and improve readability, but keep behavior the same."



## Running

Start the agent which watches `test_code.py` by running:

```powershell
python copilot_agent.py
```

The agent will warm up the model, then watch the current directory for modifications to `test_code.py`. When modifications are detected it will:

- Send the current file contents to the local Ollama model
- Receive rewritten function(s) (LLM should return only the corrected function block(s))
- Generate a unified diff and save a backup (`*.bak`) before applying the patch

## Configuration

- To change the monitored file, edit the `CODE_FILE` constant in `copilot_agent.py`.
- The agent expects the LLM response to contain only the rewritten function(s). It strips common Markdown fences (```)

## Notes

- Ensure the Ollama daemon/service is running and the requested model is available.
- The agent uses `watchdog` to observe file changes and will run continuously until interrupted.

## License

MIT
