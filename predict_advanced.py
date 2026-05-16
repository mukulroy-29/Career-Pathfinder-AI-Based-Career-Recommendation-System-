import joblib
import pandas as pd
import numpy as np

# Load trained model
model = joblib.load("career_model.pkl")

# -----------------------------
# Career Requirements Database
# -----------------------------
career_requirements = {
    "Software Engineer": {"Math_Skill": 7, "Logical_Thinking": 8},
    "Data Scientist": {"Math_Skill": 8, "Logical_Thinking": 8},
    "AI Engineer": {"Math_Skill": 8, "Logical_Thinking": 9},
    "UI/UX Designer": {"Creativity": 8},
    "Doctor": {"Logical_Thinking": 7, "Communication_Skill": 6},
    "Marketing Manager": {"Communication_Skill": 8}
}

# -----------------------------
# Minimum Skill Check
# -----------------------------
def minimum_skill_check(input_data):
    avg_skill = (
        input_data["Math_Skill"] +
        input_data["Communication_Skill"] +
        input_data["Creativity"] +
        input_data["Logical_Thinking"]
    ) / 4

    if avg_skill < 3:
        return False, avg_skill
    return True, avg_skill


# -----------------------------
# Skill Gap Analyzer
# -----------------------------
def analyze_skill_gap(career, input_data):
    required = career_requirements.get(career, {})
    gaps = []

    for skill, min_value in required.items():
        if input_data[skill] < min_value:
            gaps.append(f"Improve {skill} (Required: {min_value})")

    return gaps


# -----------------------------
# Career Prediction Function
# -----------------------------
def predict_career(input_data):

    # Step 1: Check Minimum Skill
    is_valid, avg_skill = minimum_skill_check(input_data)

    if not is_valid:
        return {
            "Status": "Rejected",
            "Reason": "Overall skill level is too low.",
            "Average Skill Score": round(avg_skill, 2)
        }

    df = pd.DataFrame([input_data])

    probabilities = model.predict_proba(df)[0]
    classes = model.classes_

    # Top 3 careers
    top_indices = np.argsort(probabilities)[-3:][::-1]

    results = []

    for idx in top_indices:
        career = classes[idx]
        confidence = round(probabilities[idx] * 100, 2)

        gaps = analyze_skill_gap(career, input_data)

        suitability_score = round(
            (
                input_data["Math_Skill"] +
                input_data["Communication_Skill"] +
                input_data["Creativity"] +
                input_data["Logical_Thinking"]
            ) / 40 * 100, 2
        )

        results.append({
            "Career": career,
"Prediction Probability (%)": confidence,
            "Suitability Score (%)": suitability_score,
            "Skill Gaps": gaps if gaps else "No major gaps"
        })

    return {
        "Status": "Success",
        "Predictions": results
    }


# -----------------------------
# Example Test Case
# -----------------------------

