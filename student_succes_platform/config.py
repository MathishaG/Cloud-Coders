from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"

STUDENT_FILE = DATA_DIR / "student_dropout_behavior_dataset.csv"
FACULTY_FILE = DATA_DIR / "faculty_dataset.csv"
ACTIVITY_FILE = DATA_DIR / "activities.csv"
MODEL_FILE = MODEL_DIR / "risk_model.joblib"
