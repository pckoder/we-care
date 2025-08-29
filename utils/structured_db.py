"""
CRUD operations for patient information using TinyDB.
"""
from tinydb import TinyDB, Query

DB_PATH = 'db.json'
db = TinyDB(DB_PATH)
Patient = Query()

def add_patient_info(info: dict):
    """Add new patient info to the database."""
    return db.insert(info)

def get_all_patients():
    """Retrieve all patient records."""
    return db.all()

def get_patient_by_age(age):
    """Retrieve patient(s) by age."""
    return db.search(Patient.age == age)

def update_patient_info(doc_id, updated_info: dict):
    """Update patient info by document ID."""
    return db.update(updated_info, doc_ids=[doc_id])

def delete_patient(doc_id):
    """Delete patient info by document ID."""
    return db.remove(doc_ids=[doc_id])

def get_patient_by_name(name):
    """Retrieve patient(s) by name."""
    return db.search(Patient.name == name)
