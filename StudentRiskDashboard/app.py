import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Student Risk Dashboard",
    page_icon="🎓",
    layout="wide"
)

# =========================================================
# LOAD DATASET
# =========================================================

@st.cache_data
def load_data():
    return pd.read_csv("student_dropout_behavior_dataset.csv")


df = load_data()

# =========================================================
# TITLE
# =========================================================

st.title("🎓 Student Risk Dashboard")

st.markdown(
    "### Early identification of students who may need academic support"
)

st.divider()

# =========================================================
# ATTENDANCE CALCULATION
# =========================================================

df["attendance_percentage"] = (
    df["lectures_attended"] /
    df["total_lectures"]
) * 100

df["lab_attendance_percentage"] = (
    df["labs_attended"] /
    df["total_lab_sessions"]
) * 100

# =========================================================
# RISK SCORE CALCULATION
# =========================================================

def calculate_risk(row):

    score = 0

    # Lecture Attendance
    if row["attendance_percentage"] < 50:
        score += 30
    elif row["attendance_percentage"] < 75:
        score += 15

    # Previous GPA
    if row["previous_gpa"] < 2.5:
        score += 25
    elif row["previous_gpa"] < 3.0:
        score += 10

    # Midterm Marks
    if row["midterm_marks"] < 40:
        score += 20
    elif row["midterm_marks"] < 50:
        score += 10

    # Final Marks
    if row["final_marks"] < 40:
        score += 15
    elif row["final_marks"] < 50:
        score += 5

    # Lab Attendance
    if row["lab_attendance_percentage"] < 50:
        score += 10

    return min(score, 100)


df["risk_score"] = df.apply(calculate_risk, axis=1)

# =========================================================
# RISK LEVEL
# =========================================================

def get_risk_level(score):

    if score >= 70:
        return "High Risk"

    elif score >= 40:
        return "Medium Risk"

    else:
        return "Low Risk"


df["risk_level"] = df["risk_score"].apply(get_risk_level)

# Priority is based on risk score
df["priority"] = df["risk_score"]

# =========================================================
# DASHBOARD METRICS
# =========================================================

total_students = len(df)

high_risk = len(
    df[df["risk_level"] == "High Risk"]
)

medium_risk = len(
    df[df["risk_level"] == "Medium Risk"]
)

low_risk = len(
    df[df["risk_level"] == "Low Risk"]
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Students",
        total_students
    )

with col2:
    st.metric(
        "🔴 High Risk",
        high_risk
    )

with col3:
    st.metric(
        "🟠 Medium Risk",
        medium_risk
    )

with col4:
    st.metric(
        "🟢 Low Risk",
        low_risk
    )

st.divider()

# =========================================================
# RISK DISTRIBUTION
# =========================================================

left, right = st.columns(2)

with left:

    st.subheader("📊 Risk Distribution")

    risk_counts = df["risk_level"].value_counts()

    fig = px.pie(
        values=risk_counts.values,
        names=risk_counts.index,
        title="Student Risk Levels"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

# =========================================================
# ACADEMIC PERFORMANCE
# =========================================================

with right:

    st.subheader("📈 Academic Performance")

    average_data = pd.DataFrame({
        "Category": [
            "Midterm",
            "Final",
            "Previous GPA",
            "Attendance"
        ],

        "Average": [
            df["midterm_marks"].mean(),
            df["final_marks"].mean(),
            df["previous_gpa"].mean(),
            df["attendance_percentage"].mean()
        ]
    })

    fig2 = px.bar(
        average_data,
        x="Category",
        y="Average",
        title="Average Student Performance"
    )

    st.plotly_chart(
        fig2,
        width="stretch"
    )

st.divider()

# =========================================================
# HIGH PRIORITY STUDENTS
# =========================================================

st.subheader("🚨 High Priority Students")

priority_df = df.sort_values(
    by="priority",
    ascending=False
)

possible_columns = [
    "student_id",
    "name",
    "previous_gpa",
    "attendance_percentage",
    "midterm_marks",
    "final_marks",
    "risk_score",
    "risk_level"
]

display_columns = [
    column
    for column in possible_columns
    if column in priority_df.columns
]

st.dataframe(
    priority_df[display_columns].head(20),
    width="stretch"
)

st.divider()

# =========================================================
# RISK FACTORS
# =========================================================

st.subheader("📊 Risk Factors")

factor_data = pd.DataFrame({
    "Risk Factor": [
        "Low Attendance",
        "Low Previous GPA",
        "Low Midterm Marks",
        "Low Final Marks",
        "Low Lab Attendance"
    ],

    "Impact Score": [
        30,
        25,
        20,
        15,
        10
    ]
})

fig3 = px.bar(
    factor_data,
    x="Risk Factor",
    y="Impact Score",
    title="Risk Factor Contribution"
)

st.plotly_chart(
    fig3,
    width="stretch"
)

st.divider()

# =========================================================
# STUDENT SEARCH
# =========================================================

st.subheader("🔎 Student Details")

if "student_id" in df.columns:

    student_ids = (
        df["student_id"]
        .astype(str)
        .unique()
    )

    selected_student = st.selectbox(
        "Select Student ID",
        student_ids
    )

    student = df[
        df["student_id"].astype(str)
        == selected_student
    ].iloc[0]

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Risk Score",
            f"{student['risk_score']}/100"
        )

    with col2:

        st.metric(
            "Risk Level",
            student["risk_level"]
        )

    with col3:

        st.metric(
            "Attendance",
            f"{student['attendance_percentage']:.1f}%"
        )

st.divider()

# =========================================================
# FOOTER
# =========================================================

st.caption(
    "EarlyWarn - Student At-Risk Prediction and "
    "Counselor Allocation System"
)