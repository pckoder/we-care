# utils/llm_agent.py
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

def is_healthcare_related(question):
    """
    Classify if a question is healthcare-related before processing
    """
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.0
        )
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a healthcare topic classifier. Determine if the user's question is related to healthcare, medicine, prescriptions, or patient health.

RETURN ONLY ONE WORD: "healthcare" or "offtopic"

RULES:
- Return "healthcare" for: medications, symptoms, conditions, prescriptions, doctors, medical advice, health concerns
- Return "offtopic" for: general knowledge, geography, history, entertainment, sports, politics, unrelated questions

EXAMPLES:
User: What is this medication for? -> healthcare
User: Do I have any allergies? -> healthcare  
User: What's the capital of France? -> offtopic
User: How far is the moon? -> offtopic
User: Can this drug cause drowsiness? -> healthcare"""),
            ("human", "User question: {question}")
        ])
        
        chain = prompt_template | llm | StrOutputParser()
        classification = chain.invoke({"question": question})
        
        return classification.strip().lower() == "healthcare"
        
    except Exception as e:
        print(f"Classification error: {str(e)}")
        return False  # Default to false if classification fails

def analyze_with_llm(user_question, extracted_text):
    """
    Use LLM to analyze extracted prescription text and answer user questions
    """
    try:
        # # Initialize LLM - using gpt-4o-mini as requested
        # llm = ChatOpenAI(
        #     model="gpt-4o-mini",
        #     api_key=os.getenv("OPENAI_API_KEY"),
        #     temperature=0.1  # Low temperature for factual responses
        # )
        """
        Use LLM to analyze extracted prescription text and answer user questions
        """
    
        # FIRST: Check if question is healthcare-related
        if not is_healthcare_related(user_question):
            return "I'm designed to help with healthcare-related questions about your prescriptions and medical needs. Please ask me about medications, symptoms, or your health information."
        
        # Proceed with healthcare questions
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.1
        )
        
        # Create a prompt template for medical analysis
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful medical assistant. Analyze the extracted prescription text and provide helpful information to the patient.

EXTRACTED PRESCRIPTION TEXT:
{extracted_text}

Please help the patient understand this prescription. Be clear, concise, and medical accurate."""),
            ("human", "User question: {question}")
        ])
        
        # Create chain
        chain = prompt_template | llm | StrOutputParser()
        
        # Invoke the chain
        response = chain.invoke({
            "extracted_text": extracted_text,
            "question": user_question
        })
        
        return response
        
    except Exception as e:
        print(f"LLM analysis error: {str(e)}")
        return "I apologize, I'm having trouble analyzing that right now. Please try again."

def format_prescription_with_llm(extracted_text):
    """
    Automatically format extracted prescription text into structured, readable summary
    """
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.0  # Zero temperature for consistent formatting
        )
        
        # Detailed prompt for structured formatting
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a medical transcription expert. Format the extracted prescription text into a clean, structured, patient-friendly summary.

ORGANIZE THE INFORMATION AS FOLLOWS:

**Patient Information**
- Name: [Extract patient name]
- Age: [Extract age]
- Other details: [Address, ID, etc.]

**Prescription Details**
Create a table for medications:
| Medication | Dosage | Quantity | Instructions |
|------------|--------|----------|-------------|
| [Drug 1] | [Strength] | [Amount] | [Directions] |
| [Drug 2] | [Strength] | [Amount] | [Directions] |

**Physician/Prescriber Information**
- Doctor: [Doctor name]
- Clinic: [Clinic name]
- Contact: [Phone/address]
- Date: [Prescription date]

**Additional Notes**
- [Any special instructions, refills, etc.]

RULES:
1. Use clean markdown formatting
2. Be extremely accurate - only include information found in the text
3. If information is missing, leave it blank rather than guessing
4. Make it easy for a patient to understand
5. Use professional medical terminology

EXTRACTED TEXT:
{extracted_text}""")
        ])
        
        chain = prompt_template | llm | StrOutputParser()
        formatted_output = chain.invoke({"extracted_text": extracted_text})
        
        return formatted_output
        
    except Exception as e:
        print(f"Prescription formatting error: {str(e)}")
        # Fallback to raw text if LLM fails
        return f"**Extracted Text:**\n{extracted_text}"