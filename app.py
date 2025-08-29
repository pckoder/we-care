# app.py
import streamlit as st
import time

from utils.file_processor import *
from utils.llm_agent import *
from utils.structured_db import *

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
if "formatted_allergy_summary" not in st.session_state:
    st.session_state.formatted_allergy_summary = None
if "formatted_preexist_summary" not in st.session_state:
    st.session_state.formatted_preexist_summary = None
if "formatted_drug_interactions_summary" not in st.session_state:
    st.session_state.formatted_drug_interactions_summary = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False

# Get the patient info if exists
patient_info = get_patient_by_name("Armande Cegna")
if patient_info:
    info = patient_info[0]
    st.info("Patient information loaded from database.")
else:
    info = {"name":"", "age": "", "allergies": "", "conditions": "", "surgery_history": "", "medications": ""}


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
        # Show the uploaded image
        st.image(uploaded_file, caption=f"Preview: {uploaded_file.name}", width='stretch')
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

        print ("-----------------------------")
        print(extracted_text)
        print ("-----------------------------")

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
        
        if extracted_text and extracted_text != "Could not extract text from image":
            analysis_status.info("⏳ Analyzing allergies...")
            formatted_summary =  analyze_personal_allergies_with_llm(extracted_text,info.get("allergies", ""))
            st.session_state.formatted_allergy_summary = formatted_summary
            time.sleep(0.25)
            analysis_status.success("✅ Allergies Alerts complete!")
        else:
            st.session_state.formatted_allergy_summary = None
            analysis_status.warning("❌ Cannot analyze allergies - extraction failed")

        if extracted_text and extracted_text != "Could not extract text from image":
            analysis_status.info("⏳ Analyzing Pre Existing Conditions ...")
            formatted_summary =  analyze_personal_preexistingconditions_with_llm(extracted_text,info.get("conditions", ""))
            st.session_state.formatted_preexist_summary = formatted_summary
            time.sleep(0.25)
            analysis_status.success("✅ Pre Existing Conditions Alerts complete!")
        else:
            st.session_state.formatted_preexist_summary = None
            analysis_status.warning("❌ Cannot analyze Pre Existing Conditions - extraction failed")

        if extracted_text and extracted_text != "Could not extract text from image":
            analysis_status.info("⏳ Analyzing Drug Interactions ...")
            formatted_summary =  analyze_personal_drug_interactions_with_llm(extracted_text, info.get("medications", ""))
            st.session_state.formatted_drug_interactions_summary = formatted_summary
            time.sleep(0.25)
            analysis_status.success("✅ Pre Existing Conditions Alerts complete!")
        else:
            st.session_state.formatted_drug_interactions_summary = None
            analysis_status.warning("❌ Cannot analyze Pre Existing Conditions - extraction failed")



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
# --- Patient Information Input ---
with st.expander("📝 Patient Information", expanded=True):
    tab0, tab1, tab2, tab3, tab4 = st.tabs(["📝 Enter / Update Patient Information", "📋 Prescription Analysis", "Allergy Analysis", "Pre Existing Conditions Analysis", "Drug Interactions Analysis"])
#st.header("Medical Assistant Chat")

# Display FORMATTED summary in main area if available
# if st.session_state.formatted_summary:
#     st.subheader("Prescription Analysis")
#     st.markdown(st.session_state.formatted_summary)
#     st.divider()


with tab0:
    with st.form(key="patient_info_form"):

        name = st.text_input("Name", value=info.get("name", ""), placeholder="e.g. Mike Smitth")
        age = st.text_input("Age", value=info.get("age", ""), placeholder="e.g. 45")
        allergies = st.text_area("Current Allergies", value=info.get("allergies", ""), placeholder="List any allergies")
        conditions = st.text_area("Pre-existing Conditions", value=info.get("conditions", ""), placeholder="List any conditions")
        surgery_history = st.text_area("Surgery History", value=info.get("surgery_history", ""), placeholder="Describe any surgeries")
        medications = st.text_area("Current Medications & Dosages", value=info.get("medications", ""), placeholder="e.g. Aspirin 100mg daily")
        submit_info = st.form_submit_button("Submit/Update Information")
        if submit_info:
            st.success("Patient information submitted!")
            st.session_state.patient_info = {
                "name": "Armande Cegna",
                "age": age,
                "allergies": allergies,
                "conditions": conditions,
                "surgery_history": surgery_history,
                "medications": medications
            }
            if patient_info:
                # Update existing record
                doc_id = patient_info[0].doc_id if hasattr(patient_info[0], 'doc_id') else patient_info[0].get('doc_id')
                update_patient_info(doc_id, st.session_state.patient_info)
            else:
                # Add new record
                add_patient_info(st.session_state.patient_info)
            st.json(st.session_state.patient_info)

with tab1:
    if st.session_state.formatted_summary:
        st.markdown(st.session_state.formatted_summary)
    else:
        st.info("No prescription analysis available. Please upload a prescription image.")
with tab2:
    if st.session_state.formatted_allergy_summary:
        st.markdown(st.session_state.formatted_allergy_summary)
    else:
        st.info("No allergy analysis available. Please upload a prescription image.")
with tab3:
    if st.session_state.formatted_preexist_summary:
        st.markdown(st.session_state.formatted_preexist_summary)
    else:
        st.info("No pre existing conditions analysis available. Please upload a prescription image.")
with tab4:
    if st.session_state.formatted_drug_interactions_summary:
        st.markdown(st.session_state.formatted_drug_interactions_summary)
    else:
        st.info("No drug interactions analysis available. Please upload a prescription image.")



#if st.session_state.formatted_summary:
#    with st.expander("📋 Prescription Analysis", expanded=True):  # Expanded by default but collapsible
#        st.markdown(st.session_state.formatted_summary)
#    st.divider()

#if st.session_state.formatted_allergy_summary:
#    with st.expander("📋 Allergy Analysis", expanded=True):  # Expanded by default but collapsible
#        st.markdown(st.session_state.formatted_allergy_summary)
#    st.divider()

#if st.session_state.formatted_preexist_summary:
#    with st.expander("📋 Pre Existing Conditions Analysis", expanded=True):  # Expanded by default but collapsible
#        st.markdown(st.session_state.formatted_preexist_summary)
#    st.divider()

#if st.session_state.formatted_drug_interactions_summary:
#    with st.expander("📋 Drug Interactions Analysis", expanded=True):  # Expanded by default but collapsible
#        st.markdown(st.session_state.formatted_drug_interactions_summary)
#    st.divider()




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

