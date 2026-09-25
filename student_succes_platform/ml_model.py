import joblib
from config import MODEL_FILE
from utils import prepare_student_features

FEATURES = [
    "quiz1_marks", "quiz2_marks", "quiz3_marks",
    "assignments_submitted", "midterm_marks", "final_marks",
    "previous_gpa", "lecture_attendance_pct", "lab_attendance_pct",
    "assignment_completion_pct", "quiz_average", "exam_average"
]

def load_model():
    if not MODEL_FILE.exists():
        return None
    return joblib.load(MODEL_FILE)

def predict_risk(model, student_df):
    prepared = prepare_student_features(student_df)
    X = prepared[FEATURES].fillna(0)
    prediction = model.predict(X)[0]

    probabilities = {}
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X)[0]
        probabilities = dict(zip(model.classes_, probs))

    return prediction, probabilities
