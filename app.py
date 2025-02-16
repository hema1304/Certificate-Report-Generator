from flask import Flask, render_template, request, redirect, url_for,flash,session
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote, unquote
from functools import wraps
from datetime import datetime,timedelta
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "defaultsecretkey")  # for handling sessions
app.config['SQLALCHEMY_DATABASE_URI'] =  os.getenv("DATABASE_URL", "sqlite:///students.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=int(os.getenv("SESSION_TIMEOUT", 15)))  # Auto logout after 15 min

db = SQLAlchemy(app)

# Mock admin credentials (store in DB for production)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME","admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

class Student(db.Model):
    id = db.Column(db.Integer,primary_key = True,autoincrement=True)  # Auto-incremented ID  
    uid = db.Column(db.String(20), unique=True, nullable=False)   # Unique certificate ID
    name = db.Column(db.String(100), nullable=False)
    date_of_joining = db.Column(db.String(20), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(10), nullable=False)
    duration = db.Column(db.String(10), nullable=False)
    completion_date = db.Column(db.String(20), nullable=True)  # Can be NULL initially

def generate_uid(location, language):
    # Get first 3 letters of location and language in uppercase
    location_code = location[:3].upper()
    language_code = language[:3].upper()
    
    # Count students from the same location & language
    existing_count = Student.query.filter_by(location=location, language=language).count()
    # Increment count for new entry
    next_id = existing_count + 1

    return f"{location_code}/{language_code}/{str(next_id).zfill(3)}"


# ------------------ Authentication Routes ------------------

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            session.permanent = True  # Make session expire after timeout
            session["show_flash"] = True  # Store flag in session
            return redirect(url_for("update"))
        flash("Invalid credentials. Please try again.", "danger")  # Flash error message
        return redirect(url_for("admin_login"))  # Redirect to login again

    return render_template("admin_login.html")

@app.route("/admin_logout")
def admin_logout():
    session.pop("admin", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

# ------------------ Admin Access Decorator ------------------

def admin_required(f):
    @wraps(f)  # This ensures Flask recognizes the original function name
    def wrap(*args, **kwargs):
        if not session.get("admin"):
            flash("Admin login required to Update details.", "warning")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrap



# ------------------ Routes ------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/enroll', methods=['GET', 'POST'])
def enroll():
    if request.method == 'POST':
        name = request.form['name']
        date_of_joining = request.form['date_of_joining']
        language = request.form['language']
        location = request.form['location']
        duration = request.form['duration']
        uid = generate_uid(location, language)
        
        # Create a new student entry
        new_student  = Student(uid=uid,name=name, date_of_joining=date_of_joining, language=language, location=location, duration=duration,completion_date=None)
        db.session.add(new_student)
        db.session.commit()
        
        
        return redirect(url_for('students'))
    return render_template('enroll.html')

@app.route('/students')
def students():
    students = Student.query.all()
    # Encode UID before passing it to template
    for student in students:
        student.encoded_uid = quote(student.uid, safe='')  # Encode UID
    return render_template('students.html', students=students)

@app.route('/certificate/<string:uid>')
def certificate(uid):
    decoded_uid = unquote(uid)  # Convert back to original format
    student = Student.query.filter_by(uid=decoded_uid).first_or_404()
    return render_template('certificate.html', student=student)

@app.route('/update')
@admin_required
def update():
    if "admin" not in session:
        flash("Your session has expired. Please log in again.", "warning")
        return redirect(url_for("admin_login"))
    
    if session.pop("show_flash", None):  # Check and remove flag
        flash("Login successful!", "success")  # Re-trigger flash message
    students = Student.query.all()
    for student in students:
        student.encoded_uid = quote(student.uid, safe='')  # Encode UID
    return render_template('update.html', students=students)


@app.route('/complete/<string:uid>', methods=['POST'])
@admin_required
def complete_course(uid):
    decoded_uid = unquote(uid)  # Decode UID before querying
    student = Student.query.filter_by(uid=decoded_uid).first_or_404()
    
    if student.completion_date is None:  # Only update if not already completed
        student.completion_date = datetime.today().strftime("%Y-%m-%d")
        db.session.commit()
        flash("Database updated successfully!", "success")
    
    return redirect(url_for('students'))  # Redirect back to student list


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure the database is created
    app.run(host="0.0.0.0", port=5000,debug = True)
