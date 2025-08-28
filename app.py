# app.py
import streamlit as st
import time
from utils.file_processor import process_uploaded_file, format_ocr_to_json
from utils.llm_agent import format_prescription_with_llm, analyze_with_llm
from evalmetrics.config import EVAL_MODE
from evalmetrics.ground_truth import get_ground_truths
from evalmetrics.evaluations import evaluate_json

st.set_page_config(layout="wide")
st.title("AI Medical Assistant")

# Initialize session state
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = None
if "formatted_summary" not in st.session_state:
    st.session_state.formatted_summary = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

# Left Sidebar - File Upload Only
with st.sidebar:
    st.header("Upload Documents")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['jpg', 'jpeg', 'png'],
        help="Upload prescription images (JPG, PNG)"
    )
    if uploaded_file is not None:
        if uploaded_file.name != st.session_state.get('current_file_name', ''):
            st.session_state.file_processed = False  # RESET the flag
            st.session_state.current_file_name = uploaded_file.name  # Track new file
            
    # Only process if a new file is uploaded AND it hasn't been processed yet
    if uploaded_file is not None and not st.session_state.file_processed:
        st.success(f"Uploaded: {uploaded_file.name}")
        
        # Create progress containers
        extraction_status = st.empty()
        analysis_status = st.empty()
        
        # Step 1: Extraction
        extraction_status.info("⏳ Extracting text from image...")
        extracted_text = process_uploaded_file(uploaded_file)
        st.session_state.extracted_text = extracted_text
        time.sleep(0.5)
        extraction_status.success("✅ Extraction complete!")
        
        # Step 2: Analysis (only if extraction worked)
        if extracted_text and extracted_text != "Could not extract text from image":
            analysis_status.info("⏳ Analyzing prescription...")
            formatted_summary = format_prescription_with_llm(extracted_text)
            st.session_state.formatted_summary = formatted_summary
            time.sleep(0.5)
            analysis_status.success("✅ Analysis complete!")
        else:
            st.session_state.formatted_summary = None
            analysis_status.warning("❌ Cannot analyze - extraction failed")
        
        # Mark file as processed to prevent re-processing on chat interactions
        st.session_state.file_processed = True

                # --- Offline Evaluation Branch ---
        if EVAL_MODE:
            # Use uploaded file name as key to ground truth
            # Call the function to get the dict
            ground_truth_dict = get_ground_truths()
            gt = ground_truth_dict.get(uploaded_file.name)
            if gt:
                json_output = format_ocr_to_json(st.session_state.extracted_text)
                score = evaluate_json(json_output, gt)
                st.write(f"Evaluation score (offline): {score}")
            else:
                st.warning("No ground truth defined for this Rx file.")

# Main Area - Chat Interface
#st.header("Medical Assistant Chat")

# Display FORMATTED summary in main area if available
# if st.session_state.formatted_summary:
#     st.subheader("Prescription Analysis")
#     st.markdown(st.session_state.formatted_summary)
#     st.divider()

if st.session_state.formatted_summary:
    with st.expander("📋 Prescription Analysis", expanded=True):  # Expanded by default but collapsible
        st.markdown(st.session_state.formatted_summary)
    st.divider()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know about this prescription?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your question..."):
            # if st.session_state.extracted_text and st.session_state.extracted_text != "Could not extract text from image":
            #     response = analyze_with_llm(prompt, st.session_state.extracted_text)
            # else:
            #     response = "Please upload a prescription image first."
            response = analyze_with_llm(prompt, st.session_state.extracted_text)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

