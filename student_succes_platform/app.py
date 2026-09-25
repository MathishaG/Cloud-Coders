import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import FACULTY_FILE, ACTIVITY_FILE
from database import (
    init_db,
    authenticate,
    get_assignments,
    get_student_assignment,
    get_all_students,
    register_student,
    update_student_academic_info
)
from utils import add_risk_labels
from ml_model import load_model, predict_risk
from recommender import load_activities, chatbot_reply
from counselor import assign_counselor, get_candidate_counselors
from styles import (
    CUSTOM_CSS,
    get_risk_badge,
    render_stat_card,
    render_hero_banner,
    render_activity_card,
    clean_html
)

def st_html(html_str: str):
    """Safely render HTML without markdown code block indentation issues."""
    st.markdown(clean_html(html_str), unsafe_allow_html=True)

# 1. Page Configuration
st.set_page_config(
    page_title="EduPulse AI | Student Success & Engagement Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom modern design system CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 2. Database Initialization
init_db()

# 3. Data Loading & ML Caching
def load_students():
    """Retrieve students directly from SQLite database."""
    return get_all_students()

@st.cache_data
def load_faculty():
    return pd.read_csv(FACULTY_FILE)

@st.cache_data
def load_activity_data():
    return load_activities(ACTIVITY_FILE)

students = load_students()
faculty = load_faculty()
activities = load_activity_data()
students_with_features = add_risk_labels(students)
model = load_model()

# 4. Session State Management
if "role" not in st.session_state:
    st.session_state.role = None

if "student_id" not in st.session_state:
    st.session_state.student_id = None

if "checked_student_id" not in st.session_state:
    st.session_state.checked_student_id = None

if "interest_query" not in st.session_state:
    st.session_state.interest_query = ""

if "saved_activities" not in st.session_state:
    st.session_state.saved_activities = []


# 5. Plotly Helper Functions for High-Clarity Visual Design
PLOTLY_FONT = "Plus Jakarta Sans, sans-serif"
COLOR_MAP = {
    "Low": "#10b981",
    "Medium": "#f59e0b",
    "High": "#ef4444"
}

def style_plotly_fig(fig, title="", height=380):
    fig.update_layout(
        title={
            "text": title,
            "y": 0.96,
            "x": 0.02,
            "xanchor": "left",
            "yanchor": "top",
            "font": {"size": 15, "family": PLOTLY_FONT, "color": "#0f172a"}
        },
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": PLOTLY_FONT, "color": "#334155", "size": 12},
        margin=dict(l=30, r=30, t=55, b=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font={"size": 12, "family": PLOTLY_FONT}
        )
    )
    fig.update_xaxes(showgrid=True, gridcolor="#f1f5f9", title_font={"family": PLOTLY_FONT, "size": 13, "color": "#475569"})
    fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", title_font={"family": PLOTLY_FONT, "size": 13, "color": "#475569"})
    return fig


def logout():
    st.session_state.role = None
    st.session_state.student_id = None
    st.session_state.checked_student_id = None
    st.session_state.interest_query = ""
    st.rerun()

# 6. Sidebar Navigation & Global Layout
def render_sidebar():
    with st.sidebar:
        # Brand Header
        st_html(
            """
            <div style="padding: 0.5rem 0 1rem 0; border-bottom: 1px solid #1e293b; margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="background: linear-gradient(135deg, #4f46e5, #6366f1); width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.25rem;">
                        🎓
                    </div>
                    <div>
                        <div style="font-weight: 800; font-size: 1.15rem; color: #ffffff; letter-spacing: -0.01em;">EduPulse AI</div>
                        <div style="font-size: 0.72rem; color: #94a3b8; font-weight: 500;">STUDENT SUCCESS & RETENTION</div>
                    </div>
                </div>
            </div>
            """
        )

        # Active User Profile Card
        if st.session_state.role == "student":
            student_match = students[students["student_id"] == st.session_state.student_id]
            st_name = student_match.iloc[0]["name"] if not student_match.empty else "Student Scholar"
            st_html(
                f"""
                <div style="background: #1e293b; border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem; border: 1px solid #334155;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="background: #4f46e5; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.9rem;">
                            {st_name[0] if st_name else 'S'}
                        </div>
                        <div>
                            <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">{st_name}</div>
                            <div style="font-size: 0.75rem; color: #94a3b8;">ID: #{st.session_state.student_id} • Student Portal</div>
                        </div>
                    </div>
                </div>
                """
            )
            if st.button("🚪 Logout", key="sidebar_logout_top", use_container_width=True):
                logout()
        elif st.session_state.role == "university":
            st_html(
                """
                <div style="background: #1e293b; border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem; border: 1px solid #334155;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div style="background: #0284c7; color: white; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1rem;">
                            🏛️
                        </div>
                        <div>
                            <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">Academic Affairs</div>
                            <div style="font-size: 0.75rem; color: #94a3b8;">Institutional Administrator</div>
                        </div>
                    </div>
                </div>
                """
            )
            if st.button("🚪 Logout", key="sidebar_logout_top", use_container_width=True):
                logout()

        # System Architecture Telemetry
        st_html(
            f"""
            <div style="margin-top: 1rem; padding: 0.9rem; background: rgba(30, 41, 59, 0.5); border-radius: 10px; border: 1px solid #334155; font-size: 0.78rem;">
                <div style="color: #94a3b8; font-weight: 700; text-transform: uppercase; margin-bottom: 0.4rem; letter-spacing: 0.05em;">SYSTEM TELEMETRY</div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="color: #cbd5e1;">ML Engine:</span>
                    <span style="color: #10b981; font-weight: 600;">RandomForest (90%)</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="color: #cbd5e1;">NLP Matcher:</span>
                    <span style="color: #38bdf8; font-weight: 600;">TF-IDF + Cosine</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span style="color: #cbd5e1;">Database:</span>
                    <span style="color: #a78bfa; font-weight: 600;">SQLite Connected</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #cbd5e1;">Active Cohort:</span>
                    <span style="color: #f8fafc; font-weight: 600;">{len(students)} Students</span>
                </div>
            </div>
            """
        )

        st_html("<div style='margin-top: 1.5rem;'></div>")

        if st.session_state.role is not None:
            if st.button("🚪 Logout", key="sidebar_logout_bottom", use_container_width=True):
                logout()


# 7. Login & Registration Page
def login_page():
    # Hide sidebar on the entering/login page
    st_html(
        """
        <style>
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {
            display: none !important;
        }
        </style>
        """
    )

    # Top Hero Banner
    st_html(
        render_hero_banner(
            title="AI-Powered Student Success & Engagement Platform",
            subtitle="Predictive early-warning risk monitoring, faculty counselor assignment, and NLP extracurricular discovery designed for student retention."
        )
    )

    col_form, col_features = st.columns([1.1, 0.9], gap="large")

    with col_form:
        st_html(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.75rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
                <div style="margin-bottom: 1.25rem;">
                    <h3 style="margin: 0; font-size: 1.35rem; color: #0f172a;">Student & Institutional Portal</h3>
                    <p style="margin: 0; font-size: 0.88rem; color: #64748b;">Sign in with existing credentials or register a new student profile.</p>
                </div>
            """
        )

        tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 New Student Registration"])

        # TAB 1: EXISTING SIGN IN
        with tab_login:
            role_choice = st.radio(
                "Select Portal Access",
                ["👨‍🎓 Student Portal", "🏛️ Institutional Administrator"],
                horizontal=True,
                label_visibility="collapsed"
            )

            # Quick demo filler buttons
            st_html("<div style='font-size: 0.78rem; font-weight: 700; color: #64748b; text-transform: uppercase; margin: 1rem 0 0.5rem 0;'>⚡ Quick 1-Click Demo Login</div>")
            q1, q2 = st.columns(2)
            with q1:
                if st.button("👩‍🎓 Student #1 (High Risk)", use_container_width=True, help="Kristina Vaughan - High Risk Case"):
                    st.session_state.role = "student"
                    st.session_state.student_id = 1
                    st.rerun()
                if st.button("👨‍🎓 Student #2 (Medium Risk)", use_container_width=True, help="Rodney Daniels - Medium Risk Case"):
                    st.session_state.role = "student"
                    st.session_state.student_id = 2
                    st.rerun()
            with q2:
                if st.button("👨‍🎓 Student #11 (Low Risk)", use_container_width=True, help="Lawrence Powers - Low Risk Case"):
                    st.session_state.role = "student"
                    st.session_state.student_id = 11
                    st.rerun()
                if st.button("🏛️ University Admin", use_container_width=True, help="Institutional Retention Office"):
                    st.session_state.role = "university"
                    st.session_state.student_id = None
                    st.rerun()

            st_html("<div style='margin: 1.2rem 0; border-top: 1px solid #e2e8f0;'></div>")

            with st.form("manual_login_form"):
                default_user = "student1" if "Student" in role_choice else "university"
                username = st.text_input("Enter Username / ID", value=default_user, placeholder="Enter your username or ID")
                password = st.text_input("Enter Password", type="password", value="student123" if "Student" in role_choice else "university123", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)

                if submitted:
                    result = authenticate(username, password)
                    if result:
                        st.session_state.role = result[1]
                        st.session_state.student_id = result[2]
                        st.rerun()
                    else:
                        st.error("Invalid username or password. Please check your credentials.")

        # TAB 2: STUDENT REGISTRATION
        with tab_register:
            st.markdown("<p style='font-size: 0.88rem; color: #475569; margin-bottom: 0.75rem;'>Fill in your personal information and academic metrics. Your profile will be stored in the database and analyzed automatically.</p>", unsafe_allow_html=True)
            
            with st.form("student_registration_form"):
                st.markdown("<div style='font-size: 0.92rem; font-weight: 700; color: #0f172a; margin-bottom: 0.6rem; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 0.35rem;'>👤 Personal & Account Information</div>", unsafe_allow_html=True)
                reg_col1, reg_col2 = st.columns(2)
                with reg_col1:
                    reg_name = st.text_input("Enter Full Name *", placeholder="e.g. Maya Chen")
                    reg_user = st.text_input("Enter Username *", placeholder="e.g. mayachen")
                    reg_pass = st.text_input("Enter Password *", type="password", placeholder="e.g. pass123")
                with reg_col2:
                    reg_age = st.number_input("Enter Student Age", min_value=16, max_value=60, value=21)
                    reg_gender = st.selectbox("Select Gender", ["Female", "Male", "Other"])
                    reg_dept = st.selectbox("Select Department", ["IT", "Engineering", "Science", "Business", "Other"])

                st.markdown("<div style='font-size: 0.92rem; font-weight: 700; color: #0f172a; margin: 1rem 0 0.6rem 0; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 0.35rem;'>📈 Enter Academic GPA & Exam Marks</div>", unsafe_allow_html=True)
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    reg_gpa = st.number_input("Enter Previous GPA (0.0 - 4.0)", min_value=0.0, max_value=4.0, value=3.20, step=0.05)
                with m_col2:
                    reg_mid = st.number_input("Enter Midterm Exam Marks (0 - 100)", min_value=0.0, max_value=100.0, value=70.0, step=1.0)
                with m_col3:
                    reg_fin = st.number_input("Enter Final Exam Marks (0 - 100)", min_value=0.0, max_value=100.0, value=75.0, step=1.0)

                st.markdown("<div style='font-size: 0.92rem; font-weight: 700; color: #0f172a; margin: 1rem 0 0.6rem 0; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 0.35rem;'>📝 Enter Continuous Evaluation Quiz Marks</div>", unsafe_allow_html=True)
                q_col1, q_col2, q_col3 = st.columns(3)
                with q_col1:
                    reg_q1 = st.number_input("Enter Quiz 1 Marks (0 - 10)", min_value=0.0, max_value=10.0, value=8.0, step=0.5)
                with q_col2:
                    reg_q2 = st.number_input("Enter Quiz 2 Marks (0 - 10)", min_value=0.0, max_value=10.0, value=8.5, step=0.5)
                with q_col3:
                    reg_q3 = st.number_input("Enter Quiz 3 Marks (0 - 10)", min_value=0.0, max_value=10.0, value=9.0, step=0.5)

                st.markdown("<div style='font-size: 0.92rem; font-weight: 700; color: #0f172a; margin: 1rem 0 0.6rem 0; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 0.35rem;'>📊 Enter Attendance & Deliverables Count</div>", unsafe_allow_html=True)
                att_c1, att_c2, att_c3 = st.columns(3)
                with att_c1:
                    reg_lec_att = st.number_input("Enter Lectures Attended", min_value=0, max_value=50, value=34)
                    reg_lec_tot = st.number_input("Enter Total Lectures", min_value=1, max_value=50, value=40)
                with att_c2:
                    reg_lab_att = st.number_input("Enter Labs Attended", min_value=0, max_value=15, value=5)
                    reg_lab_tot = st.number_input("Enter Total Lab Sessions", min_value=1, max_value=15, value=6)
                with att_c3:
                    reg_asg_sub = st.number_input("Enter Assignments Submitted", min_value=0, max_value=20, value=9)
                    reg_asg_tot = st.number_input("Enter Total Assignments", min_value=1, max_value=20, value=10)

                st_html("<div style='margin-top: 1rem;'></div>")
                reg_submit = st.form_submit_button("🚀 Register & Create Student Account", use_container_width=True)

                if reg_submit:
                    if not reg_name.strip() or not reg_user.strip() or not reg_pass.strip():
                        st.error("Please fill in your Full Name, Username, and Password.")
                    else:
                        success, result_val = register_student(
                            name=reg_name, username=reg_user, password=reg_pass,
                            age=reg_age, gender=reg_gender, department=reg_dept,
                            previous_gpa=reg_gpa, quiz1_marks=reg_q1, quiz2_marks=reg_q2, quiz3_marks=reg_q3,
                            midterm_marks=reg_mid, final_marks=reg_fin,
                            total_lectures=reg_lec_tot, lectures_attended=reg_lec_att,
                            total_lab_sessions=reg_lab_tot, labs_attended=reg_lab_att,
                            total_assignments=reg_asg_tot, assignments_submitted=reg_asg_sub
                        )
                        if success:
                            st.session_state.role = "student"
                            st.session_state.student_id = result_val
                            st.success(f"🎉 Account registered successfully! Your Student ID is #{result_val}. Redirecting to dashboard...")
                            st.rerun()
                        else:
                            st.error(result_val)

        st_html("</div>")

    with col_features:
        st_html(
            """
            <div style="display: flex; flex-direction: column; gap: 12px; height: 100%;">
                <div class="feature-box">
                    <div style="font-size: 1.5rem; margin-bottom: 4px;">🎯</div>
                    <h4 style="font-weight: 700; margin: 0; color: #0f172a;">Predictive ML Risk Engine</h4>
                    <p style="margin: 0; color: #64748b; font-size: 0.85rem;">Random Forest model trained on multi-modal indicators (GPA, quizzes, midterms, finals, lectures & lab attendance) with 90% evaluation accuracy.</p>
                </div>
                <div class="feature-box">
                    <div style="font-size: 1.5rem; margin-bottom: 4px;">💬</div>
                    <h4 style="font-weight: 700; margin: 0; color: #0f172a;">NLP Interest & Activity Matcher</h4>
                    <p style="margin: 0; color: #64748b; font-size: 0.85rem;">Conversational TF-IDF semantic vectorizer with contextual keyword filtering that maps conversational hobbies to 16 campus clubs.</p>
                </div>
                <div class="feature-box">
                    <div style="font-size: 1.5rem; margin-bottom: 4px;">👨‍🏫</div>
                    <h4 style="font-weight: 700; margin: 0; color: #0f172a;">Intelligent Counselor Assignment</h4>
                    <p style="margin: 0; color: #64748b; font-size: 0.85rem;">Smart faculty counselor matching based on department, student feedback rating, and mentorship experience.</p>
                </div>
                <div class="feature-box">
                    <div style="font-size: 1.5rem; margin-bottom: 4px;">🔒</div>
                    <h4 style="font-weight: 700; margin: 0; color: #0f172a;">Persistent SQLite Telemetry Store</h4>
                    <p style="margin: 0; color: #64748b; font-size: 0.85rem;">Relational persistence for multi-tier authentication, dynamic intervention audit trails, and student engagement records.</p>
                </div>
            </div>
            """
        )


# 8. Student Dashboard Page
def student_page():
    render_sidebar()

    student_id = st.session_state.student_id

    # Retrieve fresh student data from SQLite database
    matched_student = students[students["student_id"] == student_id]
    if matched_student.empty:
        st.error(f"Student ID #{student_id} not found in database.")
        return

    student = matched_student.iloc[0]
    student_row = students_with_features[students_with_features["student_id"] == student_id].iloc[0]

    # Predict risk with ML model
    if model:
        pred_risk, risk_probs = predict_risk(model, pd.DataFrame([student_row]))
    else:
        pred_risk = student_row["derived_risk"]
        risk_probs = {}

    # Header Card with Logout Button
    hdr_left, hdr_right = st.columns([4.2, 0.8])
    with hdr_left:
        st_html(
            f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.25rem 1.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 4px; flex-wrap: wrap;">
                    <h1 style="margin: 0; font-size: 1.85rem; color: #0f172a;">Welcome back, {student['name']}</h1>
                    {get_risk_badge(pred_risk)}
                    <span class="badge badge-indigo">Semester Status: Week 12 of 16</span>
                </div>
                <div style="font-size: 0.9rem; color: #64748b;">
                    Student ID: <strong>#{student_id}</strong> &nbsp;•&nbsp; Department: <strong>{student.get('department', 'Engineering')}</strong> &nbsp;•&nbsp; Age: <strong>{student.get('age', 21)}</strong> &nbsp;•&nbsp; Gender: <strong>{student.get('gender', 'N/A')}</strong> &nbsp;•&nbsp; Academic Standing: <strong>Active Scholar</strong>
                </div>
            </div>
            """
        )
    with hdr_right:
        st_html("<div style='margin-top: 14px;'></div>")
        if st.button("🚪 Logout", key="student_header_logout", use_container_width=True):
            logout()

    st_html("<div style='margin-bottom: 1rem;'></div>")

    # Top KPI Metrics Cards
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        gpa_val = float(student_row['previous_gpa'])
        gpa_theme = "emerald" if gpa_val >= 3.0 else ("amber" if gpa_val >= 2.5 else "rose")
        st.markdown(render_stat_card("Previous GPA", f"{gpa_val:.2f}", "Benchmark: 3.00", "🎓", gpa_theme), unsafe_allow_html=True)
    with k2:
        lec_val = float(student_row['lecture_attendance_pct'])
        lec_theme = "emerald" if lec_val >= 75 else ("amber" if lec_val >= 60 else "rose")
        st.markdown(render_stat_card("Lecture Attendance", f"{lec_val:.1f}%", f"{int(student_row['lectures_attended'])}/{int(student_row['total_lectures'])} Sessions", "📚", lec_theme), unsafe_allow_html=True)
    with k3:
        lab_val = float(student_row['lab_attendance_pct'])
        lab_theme = "emerald" if lab_val >= 75 else ("amber" if lab_val >= 60 else "rose")
        st.markdown(render_stat_card("Lab Attendance", f"{lab_val:.1f}%", f"{int(student_row['labs_attended'])}/{int(student_row['total_lab_sessions'])} Labs", "🔬", lab_theme), unsafe_allow_html=True)
    with k4:
        asg_val = float(student_row['assignment_completion_pct'])
        asg_theme = "emerald" if asg_val >= 75 else ("amber" if asg_val >= 60 else "rose")
        st.markdown(render_stat_card("Assignments", f"{asg_val:.1f}%", f"{int(student_row['assignments_submitted'])}/{int(student_row['total_assignments'])} Completed", "📝", asg_theme), unsafe_allow_html=True)
    with k5:
        exam_avg = float(student_row['exam_average'])
        exam_theme = "emerald" if exam_avg >= 60 else ("amber" if exam_avg >= 45 else "rose")
        st.markdown(render_stat_card("Exam Average", f"{exam_avg:.1f}/100", "Midterm & Final Average", "📈", exam_theme), unsafe_allow_html=True)

    st_html("<div style='margin-top: 1.5rem;'></div>")

    # Tabbed Content Navigation
    tab_academic, tab_telemetry, tab_ai, tab_mentor, tab_update = st.tabs([
        "📊 Academic Overview & Grades",
        "📈 Attendance & Telemetry",
        "🤖 AI Extracurricular Advisor",
        "🤝 My Assigned Counselor",
        "📝 Update My Academic Info"
    ])

    # TAB 1: ACADEMIC OVERVIEW
    with tab_academic:
        c_chart, c_table = st.columns([1.2, 0.8], gap="large")

        with c_chart:
            st_html(
                """
                <div class="saas-card">
                    <h3 style="margin-top: 0; font-size: 1.15rem; color: #0f172a;">Assessment Performance Breakdown</h3>
                    <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.5rem;">Visual comparison of your scores across continuous and summative assessments.</p>
                """
            )

            marks_df = pd.DataFrame({
                "Assessment": ["Quiz 1 (10)", "Quiz 2 (10)", "Quiz 3 (10)", "Midterm (100)", "Final (100)"],
                "Marks": [
                    student_row["quiz1_marks"],
                    student_row["quiz2_marks"],
                    student_row["quiz3_marks"],
                    student_row["midterm_marks"],
                    student_row["final_marks"]
                ],
                "Max": [10, 10, 10, 100, 100],
                "Percentage": [
                    (student_row["quiz1_marks"] / 10) * 100,
                    (student_row["quiz2_marks"] / 10) * 100,
                    (student_row["quiz3_marks"] / 10) * 100,
                    (student_row["midterm_marks"] / 100) * 100,
                    (student_row["final_marks"] / 100) * 100
                ]
            })

            fig = px.bar(
                marks_df,
                x="Assessment",
                y="Percentage",
                text=marks_df["Marks"].apply(lambda v: f"{v:.1f}"),
                color="Percentage",
                color_continuous_scale=[(0, "#ef4444"), (0.5, "#f59e0b"), (0.75, "#10b981"), (1, "#059669")],
                range_y=[0, 115]
            )
            fig.update_traces(
                textposition="outside",
                marker_line_color="#e2e8f0",
                marker_line_width=1,
                opacity=0.9
            )
            fig.add_hline(
                y=50,
                line_dash="dot",
                line_color="#94a3b8",
                annotation_text="Passing Threshold (50%)",
                annotation_position="bottom right"
            )
            fig.update_coloraxes(showscale=False)
            fig = style_plotly_fig(fig, title="", height=320)
            st.plotly_chart(fig, use_container_width=True)
            st_html("</div>")

        with c_table:
            st_html(
                """
                <div class="saas-card">
                    <h3 style="margin-top: 0; font-size: 1.15rem; color: #0f172a;">Course Summary & Benchmarks</h3>
                    <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 1rem;">Holistic telemetry vs institutional standards.</p>
                """
            )

            indicators = pd.DataFrame({
                "Academic Indicator": [
                    "Previous GPA",
                    "Quiz Average",
                    "Exam Average",
                    "Lecture Attendance",
                    "Lab Attendance",
                    "Assignment Completion"
                ],
                "Your Score": [
                    f"{student_row['previous_gpa']:.2f}",
                    f"{student_row['quiz_average']:.2f} / 10",
                    f"{student_row['exam_average']:.1f} / 100",
                    f"{student_row['lecture_attendance_pct']:.1f}%",
                    f"{student_row['lab_attendance_pct']:.1f}%",
                    f"{student_row['assignment_completion_pct']:.1f}%"
                ],
                "Target": [
                    "≥ 3.00",
                    "≥ 7.00",
                    "≥ 60.0",
                    "≥ 75.0%",
                    "≥ 75.0%",
                    "≥ 80.0%"
                ],
                "Status": [
                    "✅ Met" if student_row['previous_gpa'] >= 3.0 else ("⚠️ Fair" if student_row['previous_gpa'] >= 2.5 else "❌ Warning"),
                    "✅ Met" if student_row['quiz_average'] >= 7.0 else "⚠️ Fair",
                    "✅ Met" if student_row['exam_average'] >= 60.0 else "⚠️ Fair",
                    "✅ Met" if student_row['lecture_attendance_pct'] >= 75.0 else ("⚠️ Fair" if student_row['lecture_attendance_pct'] >= 60.0 else "❌ Warning"),
                    "✅ Met" if student_row['lab_attendance_pct'] >= 75.0 else ("⚠️ Fair" if student_row['lab_attendance_pct'] >= 60.0 else "❌ Warning"),
                    "✅ Met" if student_row['assignment_completion_pct'] >= 80.0 else "⚠️ Fair"
                ]
            })

            st.dataframe(indicators, hide_index=True, use_container_width=True)
            st_html("</div>")

    # TAB 2: ATTENDANCE & TELEMETRY
    with tab_telemetry:
        st_html(
            """
            <div class="saas-card">
                <h3 style="margin-top: 0; font-size: 1.2rem; color: #0f172a;">Coursework & Laboratory Telemetry Progress</h3>
                <p style="font-size: 0.88rem; color: #64748b; margin-bottom: 1.25rem;">Live monitoring of required instructional hours and assignment deliverables.</p>
            """
        )

        p1, p2, p3 = st.columns(3)

        with p1:
            lec_pct = min(float(student_row["lecture_attendance_pct"]) / 100, 1.0)
            st_html(f"<strong>Lecture Attendance: {student_row['lecture_attendance_pct']:.1f}%</strong>")
            st.progress(lec_pct)
            st.caption(f"Attended {int(student_row['lectures_attended'])} of {int(student_row['total_lectures'])} lectures")

        with p2:
            lab_pct = min(float(student_row["lab_attendance_pct"]) / 100, 1.0)
            st_html(f"<strong>Lab Attendance: {student_row['lab_attendance_pct']:.1f}%</strong>")
            st.progress(lab_pct)
            st.caption(f"Attended {int(student_row['labs_attended'])} of {int(student_row['total_lab_sessions'])} lab sessions")

        with p3:
            asg_pct = min(float(student_row["assignment_completion_pct"]) / 100, 1.0)
            st_html(f"<strong>Assignment Completion: {student_row['assignment_completion_pct']:.1f}%</strong>")
            st.progress(asg_pct)
            st.caption(f"Submitted {int(student_row['assignments_submitted'])} of {int(student_row['total_assignments'])} assignments")

        st_html("<div style='margin-top: 1.5rem;'></div>")

        # Actionable AI Academic Guidance Box
        if pred_risk == "High":
            st_html(
                """
                <div class="diagnostic-box diagnostic-high">
                    <h4 style="margin: 0 0 0.5rem 0; font-size: 1.05rem;">🔴 Academic Early Warning Action Plan</h4>
                    <p style="margin: 0; font-size: 0.9rem; line-height: 1.5;">
                        Your attendance or examination markers are below the recommended threshold. Laboratory attendance requires immediate attention. A faculty counselor has been recommended or assigned to your profile. Please check the 'My Assigned Counselor' tab.
                    </p>
                </div>
                """
            )
        elif pred_risk == "Medium":
            st_html(
                """
                <div class="diagnostic-box diagnostic-medium">
                    <h4 style="margin: 0 0 0.5rem 0; font-size: 1.05rem;">🟡 Academic Proactive Monitoring</h4>
                    <p style="margin: 0; font-size: 0.9rem; line-height: 1.5;">
                        You are maintaining fair academic standing, but certain indicators have room for improvement. Boosting lab participation and maintaining consistent assignment submissions will comfortably elevate your academic standing to Low Risk.
                    </p>
                </div>
                """
            )
        else:
            st_html(
                """
                <div class="diagnostic-box diagnostic-low">
                    <h4 style="margin: 0 0 0.5rem 0; font-size: 1.05rem;">🟢 Exemplary Academic Standing</h4>
                    <p style="margin: 0; font-size: 0.9rem; line-height: 1.5;">
                        Congratulations! Your attendance, exam performance, and coursework submissions satisfy honors criteria. Keep up the consistent consistency and consider exploring leadership or hackathon activities!
                    </p>
                </div>
                """
            )

        st_html("</div>")

    # TAB 3: AI EXTRACURRICULAR ADVISOR
    with tab_ai:
        st_html(
            """
            <div class="saas-card">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;">
                    <div style="font-size: 1.4rem;">🤖</div>
                    <div>
                        <h3 style="margin: 0; font-size: 1.2rem; color: #0f172a;">AI Passion & Extracurricular Assistant</h3>
                        <p style="margin: 0; font-size: 0.88rem; color: #64748b;">
                            Our natural language processing engine analyzes your everyday interests and hobbies to recommend campus clubs, teams, and creative collectives.
                        </p>
                    </div>
                </div>
            """
        )

        st_html("<p style='font-size: 0.85rem; font-weight: 600; color: #334155; margin-bottom: 6px;'>💡 Try one of these sample prompts (click to test):</p>")
        chips = [
            "I love coding, Python and participating in hackathons",
            "I enjoy digital design, photography and video editing",
            "I like dancing, theatre, acting and stage performance",
            "I love football, fitness, athletics and team sports",
            "I enjoy public speaking, debating and organizing events"
        ]

        c_chip_cols = st.columns(len(chips))
        for idx, (chip, col) in enumerate(zip(chips, c_chip_cols)):
            with col:
                if st.button(f"#{idx+1} {chip.split(',')[0]}...", key=f"chip_{idx}", use_container_width=True):
                    st.session_state.interest_query = chip
                    st.rerun()

        st_html("<div style='margin-top: 0.75rem;'></div>")

        user_text = st.text_area(
            "Tell the AI Assistant about your hobbies, passions, or creative interests:",
            value=st.session_state.interest_query,
            placeholder="Example: I enjoy playing guitar, composing songs, and collaborating with fellow musicians in my free time...",
            height=95
        )

        if st.button("✨ Analyze My Interests & Discover Campus Clubs", type="primary", use_container_width=True):
            if not user_text.strip():
                st.warning("Please type a few sentences describing your interests or click one of the sample prompt chips above.")
            else:
                with st.spinner("Analyzing semantic interests using NLP & TF-IDF vectorizer..."):
                    interest_text, recommendations = chatbot_reply(user_text, activities)

                st_html(
                    f"""
                    <div style="background: #eef2ff; border: 1px solid #c7d2fe; border-radius: 12px; padding: 1rem 1.25rem; margin: 1.25rem 0;">
                        <div style="font-weight: 700; color: #3730a3; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
                            <span>🧠</span> AI Interest Analysis
                        </div>
                        <div style="font-size: 0.92rem; color: #312e81;">
                            {interest_text}
                        </div>
                    </div>
                    """
                )

                st_html("<h4 style='font-size: 1.1rem; color: #0f172a; margin: 1.25rem 0 0.75rem 0;'>🏆 Personalized Extracurricular Recommendations</h4>")

                r_col1, r_col2 = st.columns(2)
                for idx, (_, activity) in enumerate(recommendations.iterrows()):
                    target_col = r_col1 if idx % 2 == 0 else r_col2
                    with target_col:
                        st.markdown(
                            render_activity_card(
                                name=activity["activity_name"],
                                category=activity.get("category", "General"),
                                description=activity.get("description", ""),
                                score_pct=float(activity.get("similarity", 0.0)),
                                interest_tag=activity.get("detected_interest", "Campus Life")
                            ),
                            unsafe_allow_html=True
                        )

        st_html("</div>")

    # TAB 4: MY ASSIGNED COUNSELOR
    with tab_mentor:
        assignment = get_student_assignment(student_id)

        st_html(
            """
            <div class="saas-card">
                <h3 style="margin-top: 0; font-size: 1.2rem; color: #0f172a;">Academic Counselor Assignment</h3>
                <p style="font-size: 0.88rem; color: #64748b; margin-bottom: 1.25rem;">
                    Institutional advising status, counselor assignments, and intervention milestones.
                </p>
            """
        )

        if assignment:
            st_html(
                f"""
                <div style="background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); border: 1.5px solid #86efac; border-radius: 14px; padding: 1.5rem; margin-bottom: 1.25rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 1.5rem;">👨‍🏫</span>
                            <span style="font-size: 1.15rem; font-weight: 800; color: #065f46;">Assigned Counselor: {assignment['faculty_name']}</span>
                        </div>
                        <span class="badge badge-low">Counselor Active</span>
                    </div>
                    <div style="font-size: 0.9rem; color: #047857; line-height: 1.5; margin-bottom: 1rem;">
                        A departmental faculty counselor has been assigned to partner with you on coursework pacing, laboratory attendance recovery, and study schedules.
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; background: #ffffff; padding: 1rem; border-radius: 10px; border: 1px solid #bbf7d0;">
                        <div>
                            <div style="font-size: 0.75rem; color: #64748b; font-weight: 700; text-transform: uppercase;">Faculty Counselor ID</div>
                            <div style="font-weight: 700; color: #0f172a;">#{assignment['faculty_id']}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.75rem; color: #64748b; font-weight: 700; text-transform: uppercase;">Date Assigned</div>
                            <div style="font-weight: 700; color: #0f172a;">{assignment.get('assigned_at', 'Recent')}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.75rem; color: #64748b; font-weight: 700; text-transform: uppercase;">Advising Channel</div>
                            <div style="font-weight: 700; color: #059669;">Office Hours & Direct Advising</div>
                        </div>
                    </div>
                </div>
                """
            )

            b1, b2 = st.columns([1, 1])
            with b1:
                if st.button("📅 Request Advising Office Hour Appointment", use_container_width=True):
                    st.toast("✅ Appointment request sent to your assigned faculty counselor!", icon="🎉")
            with b2:
                if st.button("📥 Download Course Recovery Milestone Plan", use_container_width=True):
                    st.toast("📄 Academic recovery syllabus prepared and downloaded.", icon="📝")

        else:
            st_html(
                """
                <div style="background: #f8fafc; border: 1.5px dashed #cbd5e1; border-radius: 14px; padding: 2rem; text-align: center;">
                    <div style="font-size: 2.25rem; margin-bottom: 0.5rem;">🎓</div>
                    <h4 style="margin: 0 0 0.5rem 0; color: #334155; font-size: 1.1rem;">Routine Academic Advising Active</h4>
                    <p style="margin: 0 auto; max-width: 520px; font-size: 0.9rem; color: #64748b; line-height: 1.5;">
                        You are currently in standard institutional advising. No specialized counselor is required at this time. If you require assistance, you may request a counselor anytime via student affairs.
                    </p>
                </div>
                """
            )

        st_html("</div>")

    # TAB 5: UPDATE ACADEMIC INFO
    with tab_update:
        st_html(
            """
            <div class="saas-card" style="margin-bottom: 1.25rem;">
                <h3 style="margin-top: 0; font-size: 1.2rem; color: #0f172a;">Update My Academic Profile & Information</h3>
                <p style="font-size: 0.88rem; color: #64748b; margin-bottom: 0;">
                    Update your latest marks, attendance hours, and semester deliverables. Changes are saved to the database and re-analyzed in real time.
                </p>
            </div>
            """
        )

        with st.form("student_update_form"):
            st.markdown("<div style='font-size: 0.92rem; font-weight: 700; color: #0f172a; margin-bottom: 0.6rem; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 0.35rem;'>👤 Personal & Academic Profile</div>", unsafe_allow_html=True)
            u_c1, u_c2 = st.columns(2)
            with u_c1:
                u_name = st.text_input("Enter Full Name", value=str(student.get("name", "")), placeholder="Enter your full name")
                u_age = st.number_input("Enter Student Age", min_value=16, max_value=60, value=int(student.get("age", 21)))
                u_gender = st.selectbox("Select Gender", ["Female", "Male", "Other"], index=0 if student.get("gender") == "Female" else (1 if student.get("gender") == "Male" else 2))
                u_dept = st.selectbox("Select Department", ["IT", "Engineering", "Science", "Business", "Other"], index=0)
            with u_c2:
                u_gpa = st.number_input("Enter Previous GPA (0.0 - 4.0)", min_value=0.0, max_value=4.0, value=float(student.get("previous_gpa", 3.0)), step=0.05)
                u_mid = st.number_input("Enter Midterm Exam Marks (0 - 100)", min_value=0.0, max_value=100.0, value=float(student.get("midterm_marks", 60.0)), step=1.0)
                u_fin = st.number_input("Enter Final Exam Marks (0 - 100)", min_value=0.0, max_value=100.0, value=float(student.get("final_marks", 60.0)), step=1.0)

            st.markdown("<div style='font-size: 0.92rem; font-weight: 700; color: #0f172a; margin: 1rem 0 0.6rem 0; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 0.35rem;'>📝 Enter Continuous Evaluation Quiz Marks</div>", unsafe_allow_html=True)
            uq_1, uq_2, uq_3 = st.columns(3)
            with uq_1:
                u_q1 = st.number_input("Enter Quiz 1 Marks (0 - 10)", min_value=0.0, max_value=10.0, value=float(student.get("quiz1_marks", 7.0)), step=0.5)
            with uq_2:
                u_q2 = st.number_input("Enter Quiz 2 Marks (0 - 10)", min_value=0.0, max_value=10.0, value=float(student.get("quiz2_marks", 7.0)), step=0.5)
            with uq_3:
                u_q3 = st.number_input("Enter Quiz 3 Marks (0 - 10)", min_value=0.0, max_value=10.0, value=float(student.get("quiz3_marks", 7.0)), step=0.5)

            st.markdown("<div style='font-size: 0.92rem; font-weight: 700; color: #0f172a; margin: 1rem 0 0.6rem 0; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 0.35rem;'>📊 Enter Attendance & Deliverables Count</div>", unsafe_allow_html=True)
            ua_1, ua_2, ua_3 = st.columns(3)
            with ua_1:
                u_lec_att = st.number_input("Enter Lectures Attended", min_value=0, max_value=50, value=int(student.get("lectures_attended", 30)))
                u_lec_tot = st.number_input("Enter Total Lectures", min_value=1, max_value=50, value=int(student.get("total_lectures", 40)))
            with ua_2:
                u_lab_att = st.number_input("Enter Labs Attended", min_value=0, max_value=15, value=int(student.get("labs_attended", 4)))
                u_lab_tot = st.number_input("Enter Total Lab Sessions", min_value=1, max_value=15, value=int(student.get("total_lab_sessions", 6)))
            with ua_3:
                u_asg_sub = st.number_input("Enter Assignments Submitted", min_value=0, max_value=20, value=int(student.get("assignments_submitted", 8)))
                u_asg_tot = st.number_input("Enter Total Assignments", min_value=1, max_value=20, value=int(student.get("total_assignments", 10)))

            st_html("<div style='margin-top: 1rem;'></div>")
            u_submit = st.form_submit_button("💾 Save Updated Academic Information", use_container_width=True)

            if u_submit:
                update_student_academic_info(
                    student_id=student_id, name=u_name, age=u_age, gender=u_gender, department=u_dept,
                    previous_gpa=u_gpa, quiz1_marks=u_q1, quiz2_marks=u_q2, quiz3_marks=u_q3,
                    midterm_marks=u_mid, final_marks=u_fin,
                    total_lectures=u_lec_tot, lectures_attended=u_lec_att,
                    total_lab_sessions=u_lab_tot, labs_attended=u_lab_att,
                    total_assignments=u_asg_tot, assignments_submitted=u_asg_sub
                )
                st.success("✅ Academic information updated successfully in the database!")
                st.rerun()


# 9. University Admin Dashboard Page
def university_page():
    render_sidebar()

    # Header Card with Logout Button
    hdr_left, hdr_right = st.columns([4.2, 0.8])
    with hdr_left:
        st_html(
            """
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.25rem 1.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px; flex-wrap: wrap;">
                    <h1 style="margin: 0; font-size: 1.85rem; color: #0f172a;">Institutional Retention & Early Warning Dashboard</h1>
                    <span class="badge badge-indigo">Admin Portal</span>
                    <span class="badge badge-low">● ML Early Warning Active</span>
                </div>
                <div style="font-size: 0.9rem; color: #64748b;">
                    Cohort Risk Monitoring • Multi-modal Telemetry • Faculty Counselor Assignment
                </div>
            </div>
            """
        )
    with hdr_right:
        st_html("<div style='margin-top: 14px;'></div>")
        if st.button("🚪 Logout", key="uni_header_logout", use_container_width=True):
            logout()

    st_html("<div style='margin-bottom: 1rem;'></div>")

    df = students_with_features.copy()

    # Model inference for complete cohort
    if model:
        predictions = []
        for _, row in df.iterrows():
            pred, _ = predict_risk(model, pd.DataFrame([row]))
            predictions.append(pred)
        df["risk"] = predictions
    else:
        df["risk"] = df["derived_risk"]

    total = len(df)
    high = int((df["risk"] == "High").sum())
    medium = int((df["risk"] == "Medium").sum())
    low = int((df["risk"] == "Low").sum())
    assignments_df = get_assignments()
    total_assigned = len(assignments_df)

    # Executive KPI Metric Cards
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(render_stat_card("Enrolled Cohort", f"{total}", "Active Registered Students", "👥", "indigo"), unsafe_allow_html=True)
    with k2:
        st.markdown(render_stat_card("Low Risk (Safe)", f"{low}", f"{(low/total)*100:.1f}% of cohort", "🟢", "emerald"), unsafe_allow_html=True)
    with k3:
        st.markdown(render_stat_card("Medium Risk", f"{medium}", f"{(medium/total)*100:.1f}% watchlist", "🟡", "amber"), unsafe_allow_html=True)
    with k4:
        st.markdown(render_stat_card("High Risk (Critical)", f"{high}", f"{(high/total)*100:.1f}% need counselor", "🔴", "rose"), unsafe_allow_html=True)
    with k5:
        st.markdown(render_stat_card("Counselor Assigned", f"{total_assigned}", f"{min(total_assigned, high)}/{high} High-Risk Covered", "📋", "cyan"), unsafe_allow_html=True)

    st_html("<div style='margin-top: 1.5rem;'></div>")

    # Structured Tabs (Updated names and terminology)
    tab_analytics, tab_directory, tab_assign, tab_logs = st.tabs([
        "📊 Executive Analytics & Risk Drivers",
        "👥 Student Risk Directory",
        "👨‍🏫 Assign Counselor",
        "📋 Assigned Counselors List"
    ])

    # TAB 1: EXECUTIVE ANALYTICS (HIGH CLARITY PLOTS)
    with tab_analytics:
        row1_c1, row1_c2 = st.columns([1, 1.25], gap="large")

        with row1_c1:
            st_html(
                """
                <div class="saas-card">
                    <h3 style="margin-top: 0; font-size: 1.15rem; color: #0f172a;">Cohort Risk Distribution</h3>
                    <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.5rem;">Visual breakdown of students categorized by predictive risk level.</p>
                """
            )

            risk_counts = df["risk"].value_counts().reindex(["Low", "Medium", "High"], fill_value=0).reset_index()
            risk_counts.columns = ["Risk Tier", "Students"]

            donut_fig = px.pie(
                risk_counts,
                names="Risk Tier",
                values="Students",
                hole=0.62,
                color="Risk Tier",
                color_discrete_map=COLOR_MAP
            )
            # High-clarity outside labels and center summary annotation
            donut_fig.update_traces(
                textposition="outside",
                texttemplate="<b>%{label} Risk</b><br>%{value} Students (%{percent})",
                textfont=dict(size=13, family=PLOTLY_FONT),
                marker=dict(line=dict(color="#ffffff", width=2.5))
            )
            donut_fig.update_layout(
                showlegend=True,
                annotations=[
                    dict(
                        text=f"<span style='font-size:24px;font-weight:800;color:#0f172a;'>{total}</span><br><span style='font-size:12px;color:#64748b;font-weight:600;'>TOTAL STUDENTS</span>",
                        x=0.5, y=0.5,
                        showarrow=False,
                        align="center"
                    )
                ]
            )
            donut_fig = style_plotly_fig(donut_fig, title="", height=360)
            st.plotly_chart(donut_fig, use_container_width=True)
            st_html("</div>")

        with row1_c2:
            st_html(
                """
                <div class="saas-card">
                    <h3 style="margin-top: 0; font-size: 1.15rem; color: #0f172a;">Attendance & Deliverables by Risk Cohort (%)</h3>
                    <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.5rem;">Clear comparison showing why students are categorized into each risk tier.</p>
                """
            )

            # High-clarity grouped comparison with direct data values on bars
            grouped_att = df.groupby("risk")[["lecture_attendance_pct", "lab_attendance_pct", "assignment_completion_pct"]].mean().reindex(["Low", "Medium", "High"]).reset_index()
            
            att_melted = pd.melt(
                grouped_att,
                id_vars=["risk"],
                value_vars=["lecture_attendance_pct", "lab_attendance_pct", "assignment_completion_pct"],
                var_name="Indicator",
                value_name="Average Percentage"
            )
            att_melted["Indicator"] = att_melted["Indicator"].replace({
                "lecture_attendance_pct": "Lecture Attendance %",
                "lab_attendance_pct": "Lab Attendance %",
                "assignment_completion_pct": "Assignment Submissions %"
            })

            grouped_fig = px.bar(
                att_melted,
                x="Indicator",
                y="Average Percentage",
                color="risk",
                barmode="group",
                color_discrete_map=COLOR_MAP,
                text=att_melted["Average Percentage"].apply(lambda v: f"{v:.1f}%"),
                range_y=[0, 115]
            )
            grouped_fig.update_traces(
                textposition="outside",
                textfont=dict(size=12, family=PLOTLY_FONT, color="#0f172a"),
                marker_line_color="#ffffff",
                marker_line_width=1.5
            )
            grouped_fig.update_layout(
                yaxis_title="Average Metric (%)",
                xaxis_title="",
                legend_title="Risk Level"
            )
            grouped_fig = style_plotly_fig(grouped_fig, title="", height=360)
            st.plotly_chart(grouped_fig, use_container_width=True)
            st_html("</div>")

        # Row 2: High-Clarity Academic Performance Comparison & Scatter Quadrants
        sc_col1, sc_col2 = st.columns([1, 1], gap="large")

        with sc_col1:
            st_html(
                """
                <div class="saas-card">
                    <h3 style="margin-top: 0; font-size: 1.15rem; color: #0f172a;">Exam & GPA Averages by Risk Tier</h3>
                    <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.5rem;">Average exam scores (out of 100) and previous GPA comparison.</p>
                """
            )
            acad_grouped = df.groupby("risk")[["exam_average", "previous_gpa"]].mean().reindex(["Low", "Medium", "High"]).reset_index()
            acad_melted = pd.melt(acad_grouped, id_vars=["risk"], value_vars=["exam_average", "previous_gpa"], var_name="Metric", value_name="Score")
            acad_melted["Metric"] = acad_melted["Metric"].replace({"exam_average": "Exam Average (100)", "previous_gpa": "Previous GPA (4.0)"})
            
            acad_fig = px.bar(
                acad_melted,
                x="Metric",
                y="Score",
                color="risk",
                barmode="group",
                color_discrete_map=COLOR_MAP,
                text=acad_melted.apply(lambda r: f"{r['Score']:.2f}" if "GPA" in r['Metric'] else f"{r['Score']:.1f}", axis=1),
                range_y=[0, 115]
            )
            acad_fig.update_traces(
                textposition="outside",
                textfont=dict(size=12, family=PLOTLY_FONT, color="#0f172a"),
                marker_line_color="#ffffff",
                marker_line_width=1.5
            )
            acad_fig.update_layout(yaxis_title="Average Score", xaxis_title="", legend_title="Risk Level")
            acad_fig = style_plotly_fig(acad_fig, title="", height=350)
            st.plotly_chart(acad_fig, use_container_width=True)
            st_html("</div>")

        with sc_col2:
            st_html(
                """
                <div class="saas-card">
                    <h3 style="margin-top: 0; font-size: 1.15rem; color: #0f172a;">Attendance vs Exam Scores with Threshold Quadrants</h3>
                    <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.5rem;">Visual separation with 75% attendance and 50% passing benchmarks.</p>
                """
            )
            scatter_fig = px.scatter(
                df,
                x="lecture_attendance_pct",
                y="exam_average",
                color="risk",
                hover_data=["student_id", "name", "previous_gpa", "lab_attendance_pct"],
                labels={
                    "lecture_attendance_pct": "Lecture Attendance (%)",
                    "exam_average": "Exam Score Average (Midterm & Final)",
                    "risk": "Risk Tier"
                },
                color_discrete_map=COLOR_MAP
            )
            scatter_fig.update_traces(
                marker=dict(size=9, opacity=0.82, line=dict(width=1, color="#ffffff"))
            )
            scatter_fig.add_hline(
                y=50,
                line_dash="dash",
                line_color="#94a3b8",
                annotation_text="Passing Threshold (50%)",
                annotation_position="bottom right"
            )
            scatter_fig.add_vline(
                x=75,
                line_dash="dash",
                line_color="#94a3b8",
                annotation_text="Attendance Standard (75%)",
                annotation_position="top left"
            )
            scatter_fig = style_plotly_fig(scatter_fig, title="", height=350)
            st.plotly_chart(scatter_fig, use_container_width=True)
            st_html("</div>")

    # TAB 2: STUDENT RISK DIRECTORY
    with tab_directory:
        st_html(
            """
            <div class="saas-card">
                <h3 style="margin-top: 0; font-size: 1.15rem; color: #0f172a;">Student Telemetry & Risk Directory</h3>
                <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 1rem;">Filter, search, and select students to assign a faculty counselor.</p>
            """
        )

        f_col1, f_col2, f_col3 = st.columns([1.5, 1, 1])
        with f_col1:
            search_query = st.text_input("🔍 Search by Student Name or Student ID", placeholder="e.g. Kristina, 1, Smith...")
        with f_col2:
            selected_risk = st.multiselect(
                "Filter by Risk Level",
                ["Low", "Medium", "High"],
                default=["Low", "Medium", "High"]
            )
        with f_col3:
            min_gpa = st.slider("Minimum GPA Filter", 0.0, 4.0, 0.0, 0.1)

        # Filter dataframe
        filtered_df = df[df["risk"].isin(selected_risk) & (df["previous_gpa"] >= min_gpa)].copy()
        if search_query.strip():
            sq = search_query.strip().lower()
            filtered_df = filtered_df[
                filtered_df["name"].astype(str).str.lower().str.contains(sq) |
                filtered_df["student_id"].astype(str).str.contains(sq)
            ]

        # Merge with assignment status
        assigned_ids = set(assignments_df["student_id"].tolist()) if not assignments_df.empty else set()
        filtered_df["Counselor Status"] = filtered_df["student_id"].apply(
            lambda sid: "✅ Assigned" if sid in assigned_ids else "⚠️ Not Assigned"
        )

        display_cols = [
            "student_id", "name", "department", "previous_gpa", "lecture_attendance_pct",
            "lab_attendance_pct", "assignment_completion_pct", "risk", "Counselor Status"
        ]

        st.caption(f"Showing **{len(filtered_df)}** of {len(df)} registered students in database.")

        st.dataframe(
            filtered_df[display_cols].rename(columns={
                "student_id": "ID",
                "name": "Student Name",
                "department": "Department",
                "previous_gpa": "Prev GPA",
                "lecture_attendance_pct": "Lecture Att %",
                "lab_attendance_pct": "Lab Att %",
                "assignment_completion_pct": "Asg Comp %",
                "risk": "Risk Tier"
            }),
            hide_index=True,
            use_container_width=True
        )

        st_html("<div style='margin-top: 1rem;'></div>")

        # Quick Select for Counselor Assignment
        st.markdown("#### 👨‍🏫 Select Student for Counselor Assignment")
        s_pick_col1, s_pick_col2 = st.columns([2, 1])
        with s_pick_col1:
            student_options = {f"#{row['student_id']} - {row['name']} ({row['risk']} Risk)": row['student_id'] for _, row in df.iterrows()}
            chosen_label = st.selectbox("Select a student to assign a counselor:", list(student_options.keys()))
        with s_pick_col2:
            st_html("<div style='margin-top: 28px;'></div>")
            if st.button("Proceed to Assign Counselor ➔", type="primary", use_container_width=True):
                st.session_state.checked_student_id = student_options[chosen_label]
                st.toast(f"Selected student #{st.session_state.checked_student_id} for counselor assignment!", icon="🎯")

        st_html("</div>")

    # TAB 3: COUNSELOR ASSIGNMENT
    with tab_assign:
        st_html(
            """
            <div class="saas-card">
                <h3 style="margin-top: 0; font-size: 1.2rem; color: #0f172a;">Faculty Counselor Assignment Hub</h3>
                <p style="font-size: 0.88rem; color: #64748b; margin-bottom: 1.25rem;">
                    Review student academic indicators, select the student, and assign a dedicated faculty counselor.
                </p>
            """
        )

        # Student Picker / Search
        student_id_lookup = {f"#{r['student_id']} - {r['name']} [{r['risk']} Risk]": r['student_id'] for _, r in df.iterrows()}
        all_labels = list(student_id_lookup.keys())

        default_idx = 0
        if st.session_state.checked_student_id:
            for i, (lbl, sid) in enumerate(student_id_lookup.items()):
                if sid == st.session_state.checked_student_id:
                    default_idx = i
                    break

        selected_label = st.selectbox(
            "Select Student for Diagnostic Evaluation & Counselor Assignment:",
            options=all_labels,
            index=default_idx
        )
        active_student_id = student_id_lookup[selected_label]
        target_student = df[df["student_id"] == active_student_id].iloc[0]

        st_html("<div style='margin-top: 1rem;'></div>")

        # Student Diagnostic Card
        d_left, d_right = st.columns([1.1, 0.9], gap="large")

        with d_left:
            st_html(
                f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.25rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                        <span style="font-size: 1.2rem; font-weight: 800; color: #0f172a;">#{target_student['student_id']} {target_student['name']}</span>
                        {get_risk_badge(target_student['risk'])}
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.88rem; color: #334155; margin-bottom: 1rem;">
                        <div>Department: <strong>{target_student.get('department', 'Engineering')}</strong></div>
                        <div>Previous GPA: <strong>{target_student['previous_gpa']:.2f}</strong></div>
                        <div>Lecture Attendance: <strong>{target_student['lecture_attendance_pct']:.1f}%</strong></div>
                        <div>Lab Attendance: <strong>{target_student['lab_attendance_pct']:.1f}%</strong></div>
                        <div>Assignment Completion: <strong>{target_student['assignment_completion_pct']:.1f}%</strong></div>
                        <div>Midterm Marks: <strong>{target_student['midterm_marks']:.1f}/100</strong></div>
                        <div>Final Marks: <strong>{target_student['final_marks']:.1f}/100</strong></div>
                    </div>
                """
            )

            # Risk factor diagnostics
            st_html("<strong style='font-size: 0.85rem; color: #0f172a;'>Primary Contributing Risk Factors:</strong>")
            reasons = []
            if target_student["lab_attendance_pct"] < 60:
                reasons.append(f"🔴 Critically low lab attendance ({target_student['lab_attendance_pct']:.1f}%), missing practicals.")
            elif target_student["lab_attendance_pct"] < 75:
                reasons.append(f"🟡 Lab attendance ({target_student['lab_attendance_pct']:.1f}%) below institutional threshold.")

            if target_student["lecture_attendance_pct"] < 60:
                reasons.append(f"🔴 Low lecture attendance ({target_student['lecture_attendance_pct']:.1f}%).")
            elif target_student["lecture_attendance_pct"] < 75:
                reasons.append(f"🟡 Sub-optimal lecture attendance ({target_student['lecture_attendance_pct']:.1f}%).")

            if target_student["previous_gpa"] < 2.5:
                reasons.append(f"🔴 Prior GPA ({target_student['previous_gpa']:.2f}) indicates prolonged academic distress.")
            elif target_student["previous_gpa"] < 3.0:
                reasons.append(f"🟡 Prior GPA ({target_student['previous_gpa']:.2f}) is borderline.")

            if target_student["exam_average"] < 50:
                reasons.append(f"🔴 Exam average ({target_student['exam_average']:.1f}) is below standard pass rate.")

            if not reasons:
                reasons.append("🟢 All primary indicators are within safe thresholds.")

            for r in reasons:
                st_html(f"<div style='font-size: 0.85rem; color: #475569; margin-bottom: 3px;'>{r}</div>")

            st_html("</div>")

        with d_right:
            # Counselor Recommendation Banner
            risk = target_student["risk"]
            if risk == "High":
                st_html(
                    """
                    <div class="diagnostic-box diagnostic-high">
                        <h4 style="margin: 0 0 0.35rem 0; font-size: 1.05rem;">🔴 Counselor Assignment REQUIRED</h4>
                        <p style="margin: 0; font-size: 0.88rem; line-height: 1.4;">
                            High-risk student flagged by predictive ML model. Pairing with a faculty counselor is recommended to prevent student attrition.
                        </p>
                    </div>
                    """
                )
            elif risk == "Medium":
                st_html(
                    """
                    <div class="diagnostic-box diagnostic-medium">
                        <h4 style="margin: 0 0 0.35rem 0; font-size: 1.05rem;">🟡 Counselor Assignment RECOMMENDED</h4>
                        <p style="margin: 0; font-size: 0.88rem; line-height: 1.4;">
                            Medium-risk student flagged for proactive advising. Pairing with a mentor is advised for coursework and attendance coaching.
                        </p>
                    </div>
                    """
                )
            else:
                st_html(
                    """
                    <div class="diagnostic-box diagnostic-low">
                        <h4 style="margin: 0 0 0.35rem 0; font-size: 1.05rem;">🟢 Counselor Assignment OPTIONAL</h4>
                        <p style="margin: 0; font-size: 0.88rem; line-height: 1.4;">
                            Student is in good standing. Routine counseling is available if requested.
                        </p>
                    </div>
                    """
                )

            # Department selection
            st_html("<strong style='font-size: 0.88rem; color: #0f172a;'>Select Department for Counselor Match:</strong>")
            faculty_depts = ["IT", "Engineering", "Science", "Business", "All"]
            chosen_dept = st.selectbox("Department", faculty_depts, key="dept_choice", label_visibility="collapsed")

        st_html("<div style='margin-top: 1.5rem;'></div>")

        # Faculty Candidates Section
        st_html("<h4 style='font-size: 1.15rem; color: #0f172a; margin-bottom: 0.75rem;'>👨‍🏫 Available Faculty Counselors (Ranked by Mentorship & Student Feedback)</h4>")

        candidate_mentors = get_candidate_counselors(faculty, department=chosen_dept, top_n=3)

        cand_cols = st.columns(3)
        for idx, (_, mentor) in enumerate(candidate_mentors.iterrows()):
            with cand_cols[idx]:
                st_html(
                    f"""
                    <div class="faculty-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="font-weight: 800; font-size: 1.05rem; color: #0f172a;">Prof. #{int(mentor['ID'])}</span>
                            <span class="badge badge-indigo">{mentor['Department']}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: #475569; margin-bottom: 0.75rem;">
                            <div>Degree: <strong>{mentor.get('Highest_Degree', 'Ph.D')}</strong></div>
                            <div>Teaching Experience: <strong>{mentor.get('Teaching_Experience', 0)} years</strong></div>
                            <div>Mentorship Count: <strong>{mentor.get('Mentorship_Count', 0)} students</strong></div>
                            <div>Student Feedback: <strong style="color: #059669;">{mentor.get('Student_Feedback', 0)} / 100 ⭐</strong></div>
                        </div>
                    </div>
                    """
                )
                if st.button(f"Assign Counselor (Prof. #{int(mentor['ID'])})", key=f"assign_mentor_{int(mentor['ID'])}", use_container_width=True):
                    assigned_fac = assign_counselor(
                        pd.Series(target_student),
                        faculty,
                        chosen_dept,
                        faculty_id=int(mentor["ID"])
                    )
                    st.success(
                        f"🎉 Counselor Assigned Successfully! "
                        f"Prof. #{int(assigned_fac['ID'])} ({assigned_fac.get('Department', chosen_dept)}) "
                        f"has been assigned as counselor for student #{target_student['student_id']} ({target_student['name']})."
                    )
                    st.rerun()

        st_html("</div>")

    # TAB 4: ASSIGNED COUNSELORS LIST
    with tab_logs:
        st_html(
            """
            <div class="saas-card">
                <h3 style="margin-top: 0; font-size: 1.2rem; color: #0f172a;">Active Counselor Assignments</h3>
                <p style="font-size: 0.88rem; color: #64748b; margin-bottom: 1.25rem;">
                    Institutional assignment audit trail retrieved from SQLite database.
                </p>
            """
        )

        current_assignments = get_assignments()

        if current_assignments.empty:
            st.info("No counselor assignments have been recorded yet.")
        else:
            # Merge with student names
            merged = current_assignments.merge(
                students[["student_id", "name"]],
                on="student_id",
                how="left"
            )
            merged["name"] = merged["name"].fillna("Registered Student")

            st.dataframe(
                merged[["student_id", "name", "faculty_id", "faculty_name", "assigned_at"]].rename(columns={
                    "student_id": "Student ID",
                    "name": "Student Name",
                    "faculty_id": "Faculty ID",
                    "faculty_name": "Assigned Counselor",
                    "assigned_at": "Assigned Timestamp"
                }),
                hide_index=True,
                use_container_width=True
            )

        st_html("</div>")


# 10. Main Router
if st.session_state.role is None:
    login_page()
elif st.session_state.role == "student":
    student_page()
else:
    university_page()
