# utils/file_processor.py
import requests
from PIL import Image
import io
import base64
from typing import Optional
import os
import re
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

# Get API key from environment
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def process_image_with_mistral_ocr(image_file) -> Optional[str]:
    """
    Process image using Mistral OCR API for handwritten text extraction
    """
    try:
        # Read and encode the image
        image = Image.open(image_file)
        buffered = io.BytesIO()
        image.save(buffered, format=image.format if image.format else "JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # Mistral OCR API endpoint
        url = "https://api.mistral.ai/v1/ocr"
        
        # Prepare headers with API key
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # CORRECT PAYLOAD - MATCHES OFFICIAL DOCS EXACTLY
        payload = {
            "model": "mistral-ocr-latest",  # Model is at the TOP LEVEL
            "document": {                   # document contains only type and image_url
                "type": "image_url",        # ✅ Must be "image_url", not "image"
                "image_url": f"data:image/jpeg;base64,{img_str}"  # ✅ Correct parameter name
            },
            "include_image_base64": True    # ✅ Required top-level parameter
        }

        # Make API request
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        # Extract text from response
        result = response.json()
        print("FULL API RESPONSE:", result)  # <-- ADD THIS LINE
        # Extract text from the markdown field of the first page
        if result.get('pages') and len(result['pages']) > 0:
            extracted_text = result['pages'][0].get('markdown', '').strip()
            return extracted_text
        else:
            return "No text could be extracted from the document."
    except Exception as e:
        print(f"OCR processing error: {str(e)}")
        return None

def process_uploaded_file(uploaded_file):
    """
    Main function to handle different file types
    """
    file_type = uploaded_file.type
    
    try:
        if file_type in ["image/jpeg", "image/jpg", "image/png"]:
            # Process image with OCR
            extracted_text = process_image_with_mistral_ocr(uploaded_file)
            return extracted_text or "Could not extract text from image"
        else:
            return f"File type {file_type} will be supported soon."
    except Exception as e:
        return f"Error processing file: {str(e)}"


def format_ocr_to_json(ocr_text: str) -> Dict:
    """
    Convert raw OCR text of a prescription into structured JSON.
    
    Args:
        ocr_text (str): Raw text extracted from OCR.

    Returns:
        dict: JSON structure with patient info, doctor, date, and list of drugs.
    """
    # Initialize structure
    result = {
        "patient_name": None,
        "doctor_name": None,
        "date": None,
        "drugs": []
    }

    # Split text by lines
    lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]

    # Simple patterns for common fields
    for line in lines:
        if "Patient:" in line:
            result["patient_name"] = line.split("Patient:")[-1].strip()
        elif "Doctor:" in line:
            result["doctor_name"] = line.split("Doctor:")[-1].strip()
        elif "Date:" in line:
            result["date"] = line.split("Date:")[-1].strip()
        # Detect drug entries (simple heuristic: drug name + dosage + instructions)
        elif re.search(r'\d+mg', line, re.IGNORECASE):
            parts = line.split(',')
            if len(parts) >= 2:
                drug_name = parts[0].strip()
                dosage = parts[1].strip()
                instructions = ','.join(parts[2:]).strip() if len(parts) > 2 else ""
                result["drugs"].append({
                    "drug_name": drug_name,
                    "dosage": dosage,
                    "instructions": instructions
                })
    
    return result