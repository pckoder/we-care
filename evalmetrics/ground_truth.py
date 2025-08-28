# evals/ground_truth.py

def get_ground_truths():
    """
    Returns the ground truth data for prescriptions.
    """
    return {
        "rx_001.jpg": {
            "patient_name": "Prateek Goel",
            "doctor_name": "Dr Ketan Dave",
            "date": "2024-08-15",
            "drugs": [
                {
                    "drug_name": "Amoxicillin",
                    "dosage": "500mg",
                    "instructions": "Take twice daily"
                },
                {
                    "drug_name": "Ibuprofen",
                    "dosage": "200mg",
                    "instructions": "Take after meals, three times daily"
                }
            ]
        },
        # Add more prescriptions here
    }