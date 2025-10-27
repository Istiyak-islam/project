# server/models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(200), nullable=True)
    role = db.Column(db.String(30), nullable=False)  # teacher, student, lab
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship("Profile", backref="user", uselist=False)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    fullname = db.Column(db.String(200))
    extra = db.Column(db.Text)  # JSON or plain text

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    teacher_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey("exam.id"))
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    filename = db.Column(db.String(400))
    marks = db.Column(db.Float, nullable=True)
    graded_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LabCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(200))
    software = db.Column(db.String(200))
    status = db.Column(db.String(50))
    path = db.Column(db.String(400))
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)
