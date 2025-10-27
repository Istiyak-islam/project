from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# -------------------------
# USER MODEL
# -------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'teacher', 'student', or 'lab_assistant'

    # Relationships
    profile = db.relationship('Profile', backref='user', uselist=False)
    submissions = db.relationship('Submission', backref='student', lazy=True)
    exams_created = db.relationship('Exam', backref='teacher', lazy=True)


# -------------------------
# PROFILE MODEL
# -------------------------
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120))
    department = db.Column(db.String(100))
    roll = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


# -------------------------
# EXAM MODEL
# -------------------------
class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, default=30)  # Exam duration in minutes
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    published = db.Column(db.Boolean, default=False)  # Marks/results published or not
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    submissions = db.relationship('Submission', backref='exam', lazy=True)


# -------------------------
# SUBMISSION MODEL
# -------------------------
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255))  # Path or filename of uploaded code
    code = db.Column(db.Text)              # Optional: direct code submission
    mark = db.Column(db.Float)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign Keys
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Convenience properties
    @property
    def student_name(self):
        """Return the student's full name or username."""
        if self.student and self.student.profile and self.student.profile.full_name:
            return self.student.profile.full_name
        return self.student.username if self.student else "Unknown"

    @property
    def exam_title(self):
        """Return the title of the exam."""
        return self.exam.title if self.exam else "Unknown Exam"


# -------------------------
# SOFTWARE MODEL
# -------------------------
class Software(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    path_windows = db.Column(db.String(255))  # Path to executable
    cmd = db.Column(db.String(255))           # Command to launch/check software
    type = db.Column(db.String(50))           # exe, cmd, paid
    url = db.Column(db.String(255))           # Official download URL
    is_installed = db.Column(db.Boolean, default=False)


# -------------------------
# LAB CHECK MODEL
# -------------------------
class LabCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    software_name = db.Column(db.String(100))
    path = db.Column(db.String(255))
    is_installed = db.Column(db.Boolean, default=False)
    date_checked = db.Column(db.DateTime, default=datetime.utcnow)
