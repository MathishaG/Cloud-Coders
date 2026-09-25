import hashlib
import sqlite3
from pathlib import Path
import pandas as pd
from config import STUDENT_FILE

DB_FILE = Path(__file__).resolve().parent / "student_platform.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            student_id INTEGER
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS counselor_assignments (
            student_id INTEGER PRIMARY KEY,
            faculty_id INTEGER,
            faculty_name TEXT,
            assigned_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER DEFAULT 20,
            gender TEXT DEFAULT 'Other',
            department TEXT DEFAULT 'Engineering',
            quiz1_marks REAL DEFAULT 0,
            quiz2_marks REAL DEFAULT 0,
            quiz3_marks REAL DEFAULT 0,
            total_assignments INTEGER DEFAULT 10,
            assignments_submitted REAL DEFAULT 8,
            midterm_marks REAL DEFAULT 50,
            final_marks REAL DEFAULT 50,
            previous_gpa REAL DEFAULT 3.0,
            total_lectures INTEGER DEFAULT 40,
            lectures_attended INTEGER DEFAULT 30,
            total_lab_sessions INTEGER DEFAULT 6,
            labs_attended INTEGER DEFAULT 4
        )
        """
    )

    # Populate baseline students if table is empty
    cur.execute("SELECT COUNT(*) FROM students")
    count = cur.fetchone()[0]
    if count == 0 and STUDENT_FILE.exists():
        raw_df = pd.read_csv(STUDENT_FILE)
        if "assignments_submitted" in raw_df.columns:
            raw_df["assignments_submitted"] = raw_df["assignments_submitted"].fillna(raw_df["total_assignments"] * 0.8)
        if "department" not in raw_df.columns:
            raw_df["department"] = "Engineering"
        raw_df.to_sql("students", conn, if_exists="append", index=False)

    users = [
        ("student1", hash_password("student123"), "student", 1),
        ("student2", hash_password("student123"), "student", 2),
        ("student11", hash_password("student123"), "student", 11),
        ("university", hash_password("university123"), "university", None)
    ]

    cur.executemany(
        "INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)",
        users
    )

    conn.commit()
    conn.close()


def get_all_students():
    """Retrieve all students stored in the SQLite database."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM students ORDER BY student_id ASC", conn)
    conn.close()
    return df


def get_student_by_id(student_id):
    """Retrieve a single student record by their student_id."""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM students WHERE student_id = ?", conn, params=(int(student_id),))
    conn.close()
    if not df.empty:
        return df.iloc[0].to_dict()
    return None


def register_student(
    name, username, password, age=20, gender="Other", department="Engineering",
    previous_gpa=3.0, quiz1_marks=8.0, quiz2_marks=8.0, quiz3_marks=8.0,
    midterm_marks=65.0, final_marks=70.0,
    total_lectures=40, lectures_attended=32,
    total_lab_sessions=6, labs_attended=5,
    total_assignments=10, assignments_submitted=8
):
    """Register a new student with academic information and credentials."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT username FROM users WHERE username = ?", (username.strip(),))
    if cur.fetchone():
        conn.close()
        return False, "Username is already registered. Please choose another username."

    cur.execute("SELECT COALESCE(MAX(student_id), 0) + 1 FROM students")
    new_id = int(cur.fetchone()[0])

    cur.execute(
        """
        INSERT INTO students (
            student_id, name, age, gender, department,
            quiz1_marks, quiz2_marks, quiz3_marks,
            total_assignments, assignments_submitted,
            midterm_marks, final_marks, previous_gpa,
            total_lectures, lectures_attended,
            total_lab_sessions, labs_attended
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            new_id, name.strip(), int(age), str(gender), str(department),
            float(quiz1_marks), float(quiz2_marks), float(quiz3_marks),
            int(total_assignments), float(assignments_submitted),
            float(midterm_marks), float(final_marks), float(previous_gpa),
            int(total_lectures), int(lectures_attended),
            int(total_lab_sessions), int(labs_attended)
        )
    )

    cur.execute(
        "INSERT INTO users (username, password_hash, role, student_id) VALUES (?, ?, ?, ?)",
        (username.strip(), hash_password(password.strip()), "student", new_id)
    )

    conn.commit()
    conn.close()
    return True, new_id


def update_student_academic_info(
    student_id, name, age, gender, department,
    previous_gpa, quiz1_marks, quiz2_marks, quiz3_marks,
    midterm_marks, final_marks,
    total_lectures, lectures_attended,
    total_lab_sessions, labs_attended,
    total_assignments, assignments_submitted
):
    """Update student academic parameters and personal information."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE students SET
            name = ?, age = ?, gender = ?, department = ?,
            previous_gpa = ?, quiz1_marks = ?, quiz2_marks = ?, quiz3_marks = ?,
            midterm_marks = ?, final_marks = ?,
            total_lectures = ?, lectures_attended = ?,
            total_lab_sessions = ?, labs_attended = ?,
            total_assignments = ?, assignments_submitted = ?
        WHERE student_id = ?
        """,
        (
            name.strip(), int(age), str(gender), str(department),
            float(previous_gpa), float(quiz1_marks), float(quiz2_marks), float(quiz3_marks),
            float(midterm_marks), float(final_marks),
            int(total_lectures), int(lectures_attended),
            int(total_lab_sessions), int(labs_attended),
            int(total_assignments), float(assignments_submitted),
            int(student_id)
        )
    )
    conn.commit()
    conn.close()
    return True


def get_student_assignment(student_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT student_id, faculty_id, faculty_name, assigned_at FROM counselor_assignments WHERE student_id=?",
        (int(student_id),)
    )
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "student_id": row[0],
            "faculty_id": row[1],
            "faculty_name": row[2],
            "assigned_at": row[3]
        }
    return None


def authenticate(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT username, role, student_id FROM users "
        "WHERE username=? AND password_hash=?",
        (username, hash_password(password))
    )
    result = cur.fetchone()
    conn.close()
    return result


def save_assignment(student_id, faculty_id, faculty_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO counselor_assignments "
        "(student_id, faculty_id, faculty_name) VALUES (?, ?, ?)",
        (int(student_id), int(faculty_id), faculty_name)
    )
    conn.commit()
    conn.close()


def get_assignments():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM counselor_assignments",
        conn
    )
    conn.close()
    return df
