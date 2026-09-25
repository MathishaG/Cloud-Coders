# EduPulse AI — Student Success & Engagement Platform

A production-ready, AI-powered academic retention and engagement platform designed for modern universities and educational institutions.

## 🌟 Key Features

- **Student Self-Registration & Real-Time DB Sync**: Students can register their own accounts with academic markers (GPA, quizzes, exams, attendance), stored directly in SQLite and automatically retrieved on the university side.
- **Predictive ML Risk Engine**: Random Forest classifier evaluating continuous and summative academic markers (GPA, quizzes, midterm/finals, and lecture & lab attendance) with 90% evaluation accuracy.
- **Contextual NLP Extracurricular Discovery**: Natural language understanding engine using TF-IDF vectorization and word-boundary keyword filtering to map student hobbies and conversational interests to 16 campus clubs and leadership initiatives.
- **Faculty Counselor Assignment**: Multi-factor matching system that pairs at-risk students with top faculty counselors ranked by department, mentorship capacity, and student feedback scores.
- **Interactive Student Telemetry & Profile Update**: Real-time progress bars, assessment benchmarks, course recovery advisories, self-update academic form, and active counselor tracking.
- **High-Clarity Institutional Analytics & Logs**: Clear risk distribution donut charts with outside labels and center totals, dual comparative indicator bar charts with direct numerical values, correlation scatter plots with benchmark reference lines, and persistent SQLite assignment audit logs.


## 👥 Demo Logins & Fast 1-Click Access

The login interface includes **1-click quick login buttons** for judges and evaluators, or you can manually sign in:

| Role | Username | Password | Profile / Risk Case |
|---|---|---|---|
| **Student (High Risk)** | `student1` | `student123` | Kristina Vaughan (Low lab attendance case) |
| **Student (Medium Risk)** | `student2` | `student123` | Rodney Daniels (Proactive monitoring case) |
| **Student (Low Risk)** | `student11` | `student123` | Lawrence Powers (Exemplary standing case) |
| **University Admin** | `university` | `university123` | Academic Affairs & Retention Office |

## 🚀 How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Train / Verify the ML Risk Model**:
   ```bash
   python train_model.py
   ```

3. **Launch the Application**:
   ```bash
   python -m streamlit run app.py
   ```

The application will be accessible at `http://localhost:8501`.
