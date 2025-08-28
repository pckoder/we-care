from typing import Dict
from rapidfuzz import fuzz

def evaluate_json(predicted: Dict, ground_truth: Dict) -> Dict:
    """
    Compare predicted JSON against ground truth and compute evaluation metrics.
    Uses fuzzy matching to account for minor OCR errors.

    Args:
        predicted (Dict): JSON output from OCR+LLM pipeline.
        ground_truth (Dict): Manually created ground truth JSON.

    Returns:
        Dict: Evaluation scores with field-wise comparison and overall accuracy.
    """

    # Fuzzy matching for basic fields
    results = {
        "patient_name_correct": fuzz.ratio(predicted.get("patient_name", ""), ground_truth.get("patient_name", "")) >= 90,
        "doctor_name_correct": fuzz.ratio(predicted.get("doctor_name", ""), ground_truth.get("doctor_name", "")) >= 90,
        "date_correct": fuzz.ratio(predicted.get("date", ""), ground_truth.get("date", "")) >= 90,
        "drugs_precision": 0.0,
        "drugs_recall": 0.0,
        "drugs_f1": 0.0
    }

    # Evaluate drugs
    pred_drugs = predicted.get("drugs", [])
    gt_drugs = ground_truth.get("drugs", [])

    if gt_drugs and pred_drugs:
        correct_matches = 0
        for gt_drug in gt_drugs:
            for pred_drug in pred_drugs:
                # Consider drug_name fuzzy match and exact dosage match
                name_match = fuzz.ratio(pred_drug.get("drug_name", ""), gt_drug.get("drug_name", "")) >= 85
                dosage_match = pred_drug.get("dosage", "") == gt_drug.get("dosage", "")
                if name_match and dosage_match:
                    correct_matches += 1
                    break

        precision = correct_matches / len(pred_drugs) if pred_drugs else 0
        recall = correct_matches / len(gt_drugs)
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0

        results["drugs_precision"] = round(precision, 2)
        results["drugs_recall"] = round(recall, 2)
        results["drugs_f1"] = round(f1, 2)

    return results
