import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

from config import STUDENT_FILE, MODEL_FILE, MODEL_DIR
from utils import add_risk_labels
from ml_model import FEATURES

df = pd.read_csv(STUDENT_FILE)
df = add_risk_labels(df)

X = df[FEATURES].fillna(0)
y = df["derived_risk"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

model = RandomForestClassifier(
    n_estimators=250,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

pred = model.predict(X_test)

print("Accuracy:", round(accuracy_score(y_test, pred), 4))
print(classification_report(y_test, pred))

MODEL_DIR.mkdir(exist_ok=True)
joblib.dump(model, MODEL_FILE)
print("Saved model:", MODEL_FILE)
