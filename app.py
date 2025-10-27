from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import subprocess
import webbrowser
import json
import threading
import requests

# ------------------------------------------------
# INITIAL SETUP
# ------------------------------------------------
app = Flask(__name__)
app.secret_key = 'supersecretkey'

basedir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(basedir, 'instance')
os.makedirs(instance_dir, exist_ok=True)

UPLOAD_FOLDER = os.path.join(basedir, 'submissions')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_dir, 'smart_lab.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------------------------------------
# MODELS
# ------------------------------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # teacher, student, lab_assistant

    profile = db.relationship('Profile', backref='user', uselist=False)
    submissions = db.relationship('Submission', backref='student', lazy=True)
    exams_created = db.relationship('Exam', backref='teacher', lazy=True)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120))
    department = db.Column(db.String(100))
    roll = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Software(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    path_windows = db.Column(db.String(255))
    cmd = db.Column(db.String(255))
    type = db.Column(db.String(50))
    url = db.Column(db.String(255))
    is_installed = db.Column(db.Boolean, default=False)

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, default=30)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    published = db.Column(db.Boolean, default=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    submissions = db.relationship('Submission', backref='exam', lazy=True)

    @property
    def time_remaining(self):
        if self.end_time:
            remaining = (self.end_time - datetime.utcnow()).total_seconds()
            return max(0, int(remaining))
        return 0

    def submitted_by(self, student_id):
        return Submission.query.filter_by(exam_id=self.id, student_id=student_id).first() is not None

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_name = db.Column(db.String(255))
    code = db.Column(db.Text)
    mark = db.Column(db.Float)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def student_name(self):
        if self.student and self.student.profile and self.student.profile.full_name:
            return self.student.profile.full_name
        return self.student.username if self.student else "Unknown"

    @property
    def exam_title(self):
        return self.exam.title if self.exam else "Unknown Exam"

# ------------------------------------------------
# LOGIN MANAGEMENT
# ------------------------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------
def normalize_path(path):
    if not path:
        return None
    path = os.path.expandvars(path.strip('"'))
    return os.path.normpath(path)

def load_software_from_config():
    try:
        with open('config.json') as f:
            softwares = json.load(f).get('softwares', [])
        for s in softwares:
            existing = Software.query.filter_by(name=s['name']).first()
            if not existing:
                db.session.add(Software(
                    name=s['name'],
                    path_windows=s.get('path_windows'),
                    cmd=s.get('cmd'),
                    type=s.get('type'),
                    url=s.get('url'),
                    is_installed=False
                ))
        db.session.commit()
    except Exception as e:
        print(f"[Error loading config.json] {e}")

def check_installed(software):
    installed = False
    try:
        if software.type == 'exe' and software.path_windows:
            clean_path = normalize_path(software.path_windows)
            installed = os.path.exists(clean_path)
        elif software.type == 'cmd' and software.cmd:
            result = subprocess.run(software.cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            installed = result.returncode == 0
    except Exception:
        installed = False
    software.is_installed = installed
    db.session.commit()
    return installed


@app.route('/lab/check_software_status/<software_name>')
@login_required
def check_software_status(software_name):
    if current_user.role != 'lab_assistant':
        return jsonify({'status': 'error', 'message': 'Access denied'})

    software = Software.query.filter_by(name=software_name).first()
    if not software:
        return jsonify({'status': 'error', 'message': 'Software not found'})

    installed = check_installed(software)
    return jsonify({'status': 'success', 'installed': installed})


# ------------------------------------------------
# DOWNLOAD & INSTALL WITH PROGRESS
# ------------------------------------------------
progress_data = {}

def download_software(software):
    """Download software from URL and track progress."""
    url = software.url
    local_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{software.name}.exe")
    progress_data[software.name] = 0
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_length = int(r.headers.get('content-length', 0))
            downloaded = 0
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        progress_data[software.name] = int(downloaded * 100 / total_length)
        progress_data[software.name] = 100
        subprocess.Popen([local_filename], shell=True)
        check_installed(software)
    except Exception as e:
        progress_data[software.name] = -1
        print(f"Download failed for {software.name}: {e}")

# ------------------------------------------------
# ROUTES
# ------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        if not all([username,email,password,role]):
            flash('All fields required!','danger')
            return redirect(url_for('signup'))
        if User.query.filter_by(username=username).first():
            flash('Username exists!','danger')
            return redirect(url_for('signup'))
        hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        user = User(username=username,email=email,password=hashed,role=role)
        db.session.add(user)
        db.session.commit()
        db.session.add(Profile(full_name=username,department='Not set',roll='Not set',user_id=user.id))
        db.session.commit()
        flash('Signup success!','success')
        return redirect(url_for('login'))
    return render_template('signup.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        if not all([email,password,role]):
            flash('All fields required!','danger')
            return redirect(url_for('login'))
        user = User.query.filter_by(email=email,role=role).first()
        if not user or not check_password_hash(user.password,password):
            flash('Invalid credentials!','danger')
            return redirect(url_for('login'))
        login_user(user)
        flash('Login success!','success')
        if role=='teacher':
            return redirect(url_for('teacher_dashboard'))
        elif role=='student':
            return redirect(url_for('student_dashboard'))
        elif role=='lab_assistant':
            return redirect(url_for('lab_dashboard'))
    return render_template('login.html')

# ---------------- LAB DASHBOARD ----------------
@app.route('/lab/dashboard')
@login_required
def lab_dashboard():
    if current_user.role!='lab_assistant':
        flash('Access denied!','danger')
        return redirect(url_for('index'))
    softwares = Software.query.all()
    for s in softwares: check_installed(s)
    return render_template('lab_dashboard.html',softwares=softwares)

@app.route('/lab/install/<software_name>', methods=['POST'])
@login_required
def lab_install(software_name):
    if current_user.role != 'lab_assistant':
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))

    software = Software.query.filter_by(name=software_name).first()
    if not software:
        flash('Software not found!', 'danger')
        return redirect(url_for('lab_dashboard'))

    if check_installed(software):
        flash(f"{software.name} is already installed.", 'success')
        return redirect(url_for('lab_dashboard'))

    if software.url:
        threading.Thread(target=download_software, args=(software,), daemon=True).start()
        flash(f"Downloading {software.name} in background...", 'info')
    else:
        flash(f"No download URL. Please install {software.name} manually.", 'warning')

    return redirect(url_for('lab_dashboard'))

@app.route('/lab/progress/<software_name>')
@login_required
def lab_progress(software_name):
    value = progress_data.get(software_name, 0)
    return jsonify({'progress': value})

@app.route('/redirect_to_download/<int:software_id>')
@login_required
def redirect_to_download(software_id):
    software = Software.query.get(software_id)
    if software and software.url:
        return redirect(software.url)
    flash('Download URL not found','danger')
    return redirect(url_for('lab_dashboard'))

# ---------------- TEACHER DASHBOARD ----------------
@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role!='teacher':
        flash('Access denied!','danger')
        return redirect(url_for('index'))
    exams = Exam.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher_dashboard.html',exams=exams)

@app.route('/create_exam', methods=['POST'])
@login_required
def create_exam():
    if current_user.role!='teacher':
        return jsonify({'status':'error','message':'Access denied'})
    title = request.form.get('title')
    desc = request.form.get('description')
    duration = request.form.get('duration',30)
    start_time_str = request.form.get('start_time')
    try:
        start_time = datetime.strptime(start_time_str,'%Y-%m-%d %H:%M') if start_time_str else datetime.utcnow()
    except:
        start_time=datetime.utcnow()
    end_time = start_time + timedelta(minutes=int(duration))
    exam = Exam(title=title,description=desc,duration_minutes=int(duration),
                start_time=start_time,end_time=end_time,teacher_id=current_user.id)
    db.session.add(exam)
    db.session.commit()
    return jsonify({'status':'success'})

@app.route('/teacher/submissions/<int:exam_id>')
@login_required
def teacher_submissions(exam_id):
    if current_user.role!='teacher':
        flash('Access denied!','danger')
        return redirect(url_for('index'))
    exam = Exam.query.get(exam_id)
    submissions = Submission.query.filter_by(exam_id=exam_id).all() if exam else []
    return render_template('teacher_submissions.html',exam=exam,submissions=submissions)

@app.route('/save_mark', methods=['POST'])
@login_required
def save_mark():
    if current_user.role!='teacher':
        return jsonify({'status':'error','message':'Access denied'})
    sub_id = request.form.get('submission_id')
    mark = request.form.get('mark')
    sub = Submission.query.get(sub_id)
    if not sub:
        return jsonify({'status':'error','message':'Submission not found'})
    sub.mark=float(mark)
    db.session.commit()
    return jsonify({'status':'success'})

@app.route('/publish_result/<int:exam_id>')
@login_required
def publish_result(exam_id):
    if current_user.role!='teacher':
        flash('Access denied!','danger')
        return redirect(url_for('index'))
    exam = Exam.query.get(exam_id)
    if exam:
        exam.published=True
        db.session.commit()
        flash('Result published!','success')
    return redirect(url_for('teacher_dashboard'))

@app.route('/download_submission/<filename>')
@login_required
def download_submission(filename):
    if not filename:
        flash('File not found!','danger')
        return redirect(url_for('student_dashboard'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# ---------------- STUDENT DASHBOARD ----------------
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role!='student':
        flash('Access denied!','danger')
        return redirect(url_for('index'))

    exams = Exam.query.order_by(Exam.start_time.desc().nullslast()).all()
    softwares = Software.query.all()

    for exam in exams:
        submission = Submission.query.filter_by(exam_id=exam.id, student_id=current_user.id).first()
        exam.submitted = bool(submission)
        exam.submission_file = submission.file_name if submission and submission.file_name else None
        exam.mark = submission.mark if submission and exam.published else None
        exam.remaining_time = exam.time_remaining

    return render_template('dashboard_student.html',exams=exams,softwares=softwares)

@app.route('/submit_exam', methods=['POST'])
@login_required
def submit_exam():
    if current_user.role!='student':
        return jsonify({'status':'error','message':'Access denied'})
    exam_id = request.form.get('exam_id')
    software_name = request.form.get('software')
    file = request.files.get('file')
    if not all([exam_id,software_name]) or not file:
        return jsonify({'status':'error','message':'All fields required'})
    exam = Exam.query.get(exam_id)
    if not exam:
        return jsonify({'status':'error','message':'Exam not found'})
    if exam.end_time and datetime.utcnow() > exam.end_time:
        return jsonify({'status':'error','message':'Exam time is over, cannot submit'})
    safe_filename = f"{current_user.id}_{exam_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    file.save(save_path)
    submission = Submission.query.filter_by(exam_id=exam_id,student_id=current_user.id).first()
    if not submission:
        submission = Submission(exam_id=exam_id,student_id=current_user.id,file_name=safe_filename,submitted_at=datetime.utcnow())
        db.session.add(submission)
    else:
        submission.file_name = safe_filename
        submission.submitted_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'status':'success'})

# ---------------- LOGOUT ----------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out!','success')
    return redirect(url_for('login'))

# ------------------------------------------------
# RUN
# ------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        load_software_from_config()
    app.run(debug=True)
