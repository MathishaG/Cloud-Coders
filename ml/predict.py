import pandas as pd
import joblib


# --------------------------------------------------
# LOAD TRAINED MODEL
# --------------------------------------------------

model = joblib.load("ml/model.pkl")

print("Model classes:", model.classes_)


# --------------------------------------------------
# LOAD PROCESSED STUDENT DATA
# --------------------------------------------------

data = pd.read_csv("ml/processed_student_data.csv")


# --------------------------------------------------
# PREDICT RISK CLASS
# --------------------------------------------------

predictions = model.predict(data)


# --------------------------------------------------
# GET PREDICTION PROBABILITIES
# --------------------------------------------------

probabilities = model.predict_proba(data)


# --------------------------------------------------
# CONVERT RISK CLASS TO RISK LEVEL
# --------------------------------------------------

def get_risk_level(risk_class):

    if risk_class == 2:
        return "High"

    elif risk_class == 1:
        return "Medium"

    else:
        return "Low"


# --------------------------------------------------
# CALCULATE RISK SCORE
# --------------------------------------------------

risk_scores = []

for index, prediction in enumerate(predictions):

    # Find the column corresponding to High Risk (class 2)
    if 2 in model.classes_:

        high_risk_index = list(model.classes_).index(2)

        score = probabilities[index][high_risk_index] * 100

    else:
        # If model did not learn High Risk class
        score = 0.0

    risk_scores.append(score)


# --------------------------------------------------
# ADD RESULTS
# --------------------------------------------------

data["risk_level"] = [
    get_risk_level(prediction)
    for prediction in predictions
]

data["risk_score"] = risk_scores


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

print("\nStudent Risk Predictions\n")

for index in range(len(data)):

    print(
        f"Student {index + 1}: "
        f"Risk Score = {data.loc[index, 'risk_score']:.2f}, "
        f"Risk Level = {data.loc[index, 'risk_level']}"
    )


# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

data.to_csv(
    "ml/risk_predictions.csv",
    index=False
)

print("\nRisk predictions saved to ml/risk_predictions.csv")