import streamlit as st
from pathlib import Path
from copilot_agent import get_advanced_code_corrections, extract_corrected_code, backup_and_overwrite

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
    overwrite = st.checkbox("Overwrite the file with corrected code", value=False)

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
                    st.subheader("LLM Full Feedback")
                    st.text_area("LLM Response", llm_response, height=300)

                    corrected = extract_corrected_code(llm_response)
                    if corrected:
                        st.subheader("Extracted Corrected Code")
                        st.code(corrected, language="python")

                        if overwrite:
                            try:
                                backup_and_overwrite(p, corrected)
                                st.success(f"File overwritten and backup created next to original.")
                            except Exception as e:
                                st.error(f"Failed to overwrite file: {e}")
                    else:
                        st.warning("Could not extract corrected code from the LLM response.")

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
