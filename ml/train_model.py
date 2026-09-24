import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier


# Files
actual_data = pd.read_csv("ml/dataset.csv")
processed_data = pd.read_csv("ml/processed_student_data.csv")


# Create risk based on final marks
def create_risk_level(final_marks):

    if final_marks < 40:
        return 2          # High Risk

    elif final_marks <= 60:
        return 1          # Medium Risk

    else:
        return 0          # Low Risk


# Create target
actual_data["risk_level"] = actual_data["final_marks"].apply(
    create_risk_level
)


# Input features
X = processed_data

# Target
y = actual_data["risk_level"]


# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# Create model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)


# Train model
model.fit(X_train, y_train)


# Save model
joblib.dump(model, "ml/model.pkl")