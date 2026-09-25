import pandas as pd

def prepare_student_features(df):
    out = df.copy()

    numeric_cols = [
        "quiz1_marks", "quiz2_marks", "quiz3_marks",
        "total_assignments", "assignments_submitted",
        "midterm_marks", "final_marks", "previous_gpa",
        "total_lectures", "lectures_attended",
        "total_lab_sessions", "labs_attended"
    ]

    for col in numeric_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    out["assignments_submitted"] = out["assignments_submitted"].fillna(
        out["total_assignments"] * 0.8
    ).clip(lower=0)

    out["lecture_attendance_pct"] = (
        out["lectures_attended"] / out["total_lectures"].replace(0, 1) * 100
    ).clip(0, 100)

    out["lab_attendance_pct"] = (
        out["labs_attended"] / out["total_lab_sessions"].replace(0, 1) * 100
    ).clip(0, 100)

    out["assignment_completion_pct"] = (
        out["assignments_submitted"] /
        out["total_assignments"].replace(0, 1) * 100
    ).clip(0, 100)

    out["quiz_average"] = out[
        ["quiz1_marks", "quiz2_marks", "quiz3_marks"]
    ].mean(axis=1)

    out["exam_average"] = out[
        ["midterm_marks", "final_marks"]
    ].mean(axis=1)

    return out


def risk_score(row):
    score = 0

    if row["previous_gpa"] < 2.5:
        score += 2
    elif row["previous_gpa"] < 3.0:
        score += 1

    if row["lecture_attendance_pct"] < 60:
        score += 2
    elif row["lecture_attendance_pct"] < 75:
        score += 1

    if row["lab_attendance_pct"] < 60:
        score += 2
    elif row["lab_attendance_pct"] < 75:
        score += 1

    if row["assignment_completion_pct"] < 60:
        score += 2
    elif row["assignment_completion_pct"] < 80:
        score += 1

    if row["exam_average"] < 40:
        score += 2
    elif row["exam_average"] < 55:
        score += 1

    if row["quiz_average"] < 5:
        score += 1

    if score >= 7:
        return "High"
    if score >= 4:
        return "Medium"
    return "Low"


def add_risk_labels(df):
    out = prepare_student_features(df)
    out["derived_risk"] = out.apply(risk_score, axis=1)
    return out
