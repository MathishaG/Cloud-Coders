import pandas as pd
from database import save_assignment

def get_candidate_counselors(faculty_df, department=None, top_n=5):
    faculty = faculty_df.copy()

    if department and str(department).lower() not in ["all", "any", "other", ""]:
        same_dept = faculty[
            faculty["Department"].astype(str).str.lower()
            == str(department).lower()
        ]
        if not same_dept.empty:
            faculty = same_dept

    faculty["mentor_score"] = pd.to_numeric(
        faculty["Mentorship_Count"],
        errors="coerce"
    ).fillna(0)

    faculty["feedback_score"] = pd.to_numeric(
        faculty["Student_Feedback"],
        errors="coerce"
    ).fillna(0)

    faculty["experience_score"] = pd.to_numeric(
        faculty.get("Teaching_Experience", 0),
        errors="coerce"
    ).fillna(0)

    faculty = faculty.sort_values(
        ["mentor_score", "feedback_score", "experience_score"],
        ascending=[False, False, False]
    )

    return faculty.head(top_n)


def assign_counselor(student, faculty_df, department, faculty_id=None):
    faculty = faculty_df.copy()

    if faculty_id is not None:
        matched = faculty[faculty["ID"] == int(faculty_id)]
        if not matched.empty:
            selected = matched.iloc[0]
        else:
            candidates = get_candidate_counselors(faculty, department, top_n=1)
            selected = candidates.iloc[0]
    else:
        candidates = get_candidate_counselors(faculty, department, top_n=1)
        selected = candidates.iloc[0]

    dept_label = selected.get("Department", department)
    faculty_title = f"Prof. #{int(selected['ID'])} ({dept_label})"

    save_assignment(
        student["student_id"],
        selected["ID"],
        faculty_title
    )

    return selected

