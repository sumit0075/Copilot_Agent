import streamlit as st
from pathlib import Path
from copilot_agent import get_advanced_code_corrections, extract_corrected_code, backup_and_overwrite, restore_backup
from user_prompt import apply_user_prompt

st.set_page_config(page_title="Copilot Agent - Code Fixer", layout="wide")

st.title("Copilot Agent — Code Fixer")
st.markdown(
    "Use this app to point to a local Python file, send it to the LLM for corrections, "
    "preview the LLM feedback and corrected code, and optionally overwrite the file with a backup."
)

# Layout: left preview, right controls/results
left_col, right_col = st.columns([2, 1])

# Controls live in the left column
with left_col:
    st.info("Pick a Python file from a directory.")
    dir_path = st.text_input("Directory path", value=".")
    dp = Path(dir_path)
    py_files = []
    if dp.is_dir():
        py_files = sorted([f.name for f in dp.iterdir() if f.is_file() and f.suffix == ".py"])
    else:
        st.warning("Directory not found")

    selected_from_dir = None
    if py_files:
        selected = st.selectbox("Choose a Python file", options=py_files)
        selected_from_dir = str(Path(dir_path) / selected)
        st.write(f"Selected: {selected_from_dir}")
        code_path = selected_from_dir
    else:
        code_path = None

# Options and outputs live in the left column (controls first, outputs below)
with left_col:
    mode = st.selectbox("Mode", options=["Analyze file", "User prompt"]) 
    overwrite = st.checkbox("Overwrite the file with corrected code", value=False)

    if mode == "Analyze file":
        analyze = st.button("Analyze file with LLM")

        if analyze:
            if not code_path:
                st.error("No file selected. Please choose a Python file from the directory first.")
            else:
                p = Path(code_path)
                if not p.is_file():
                    st.error(f"File not found: {code_path}")
                else:
                    with st.spinner("Reading file and sending code to LLM..."):
                        code_text = p.read_text(encoding="utf-8")

                        try:
                            llm_response = get_advanced_code_corrections(code_text)
                        except Exception as e:
                            st.error(f"LLM call failed: {e}")
                            llm_response = ""

                    if llm_response:
                        # Persist results so Apply/Undo remain available across reruns
                        st.session_state['last_llm_response'] = llm_response
                        corrected = extract_corrected_code(llm_response)
                        st.session_state['last_modified'] = corrected
                        st.session_state['last_source_path'] = str(p)

                    if llm_response and not extract_corrected_code(llm_response):
                        st.warning("Could not extract corrected code from the LLM response.")

    else:  # User prompt mode
        user_prompt = st.text_input("Enter instruction for the model", value="")
        run_prompt = st.button("Run user prompt on selected file")

        if run_prompt:
            if not code_path:
                st.error("No file selected. Please choose a Python file from the directory first.")
            elif not user_prompt.strip():
                st.error("Please enter a prompt/instruction for the model.")
            else:
                p = Path(code_path)
                if not p.is_file():
                    st.error(f"File not found: {code_path}")
                else:
                    code_text = p.read_text(encoding="utf-8")
                    with st.spinner("Sending user prompt to the model..."):
                        try:
                            llm_response, modified = apply_user_prompt(code_text, user_prompt)
                        except Exception as e:
                            st.error(f"LLM call failed: {e}")
                            llm_response, modified = "", ""

                    if llm_response:
                        # Persist results so Apply/Undo remain available across reruns
                        st.session_state['last_llm_response'] = llm_response
                        st.session_state['last_modified'] = modified
                        st.session_state['last_source_path'] = str(p)

    # If there is a last backup in session state, show undo option
    if st.session_state.get('last_backup'):
        try:
            last_b = Path(st.session_state['last_backup'])
            if last_b.is_file():
                if st.button("Undo last overwrite"):
                    try:
                        restore_backup(Path(code_path), last_b)
                        st.success("Backup restored — changes undone.")
                        del st.session_state['last_backup']
                    except Exception as e:
                        st.error(f"Failed to restore backup: {e}")
        except Exception:
            # If session state has corrupt path, clear it
            st.session_state.pop('last_backup', None)

    # Render persisted LLM response and modified code (if any)
    if st.session_state.get('last_llm_response'):
        st.subheader("LLM Full Response (last run)")
        st.text_area("LLM Response (last)", st.session_state['last_llm_response'], height=300)

    if st.session_state.get('last_modified'):
        st.subheader("Modified Code (last run)")
        st.code(st.session_state['last_modified'], language="python")
        st.caption("Verify the modified code before applying. If the model returned prose or unexpected content, edit your prompt and retry.")
        # Always offer Apply button for the stored modified code
        if st.button("Apply stored modified code to file"):
            try:
                source_path = Path(st.session_state.get('last_source_path', code_path))
                backup_path = backup_and_overwrite(source_path, st.session_state['last_modified'])
                st.session_state['last_backup'] = str(backup_path)
                st.success(f"File overwritten and backup created: {backup_path.name}")
            except Exception as e:
                st.error(f"Failed to overwrite file: {e}")

# Preview in the right column
with right_col:
    st.subheader("Selected file preview")
    if code_path:
        p = Path(code_path)
        if p.is_file():
            try:
                code_text_preview = p.read_text(encoding="utf-8")
                st.code(code_text_preview, language="python")
            except Exception as e:
                st.error(f"Unable to read selected file: {e}")
        else:
            st.info("Selected file not found in directory.")
    else:
        st.info("No file selected. Choose a file from the directory on the left.")

st.markdown("---")
st.caption("Note: This app calls an LLM via the `ollama` client from `copilot_agent.py`. Ensure your environment is configured to allow that call.")
