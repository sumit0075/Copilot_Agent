# Local Copilot Agent

Small utility that monitors `test_code.py`, sends the code to a local Ollama model for suggested function-level patches, and applies patches (saving a `.bak` backup).

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
