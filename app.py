from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import os

app = Flask(__name__)

# Secret key for login sessions
app.secret_key = "knotworks_secret_key"

# ---------------- CONFIG ----------------

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///recruitment.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Email config (can update later)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "your_email@gmail.com"
app.config["MAIL_PASSWORD"] = "your_app_password"

db = SQLAlchemy(app)
mail = Mail(app)

# ---------------- DATABASE MODELS ----------------

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(100))
    qualification = db.Column(db.String(200))
    experience = db.Column(db.String(200))
    resume = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    location = db.Column(db.String(100))
    job_type = db.Column(db.String(100))


# ---------------- GLOBAL CONTEXT ----------------

@app.context_processor
def inject_year():
    return {"current_year": datetime.now().year}


# ---------------- WEBSITE ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/career")
def career():
    return render_template("career.html")


@app.route("/jobs")
def jobs():
    jobs = Job.query.all()
    return render_template("jobs.html", jobs=jobs)


# ---------------- CAREER FORM ----------------

@app.route("/submit-career", methods=["POST"])
def submit_career():

    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    qualification = request.form.get("qualification")
    experience = request.form.get("experience")

    resume_file = request.files["resume"]
    filename = resume_file.filename
    resume_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    candidate = Candidate(
        name=name,
        email=email,
        phone=phone,
        qualification=qualification,
        experience=experience,
        resume=filename
    )

    db.session.add(candidate)
    db.session.commit()

    return redirect(url_for("thankyou"))


@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


# ---------------- ADMIN LOGIN ----------------

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "knotworks123"


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")


# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin")
def admin():

    if not session.get("admin"):
        return redirect("/login")

    candidates = Candidate.query.order_by(Candidate.date.desc()).all()
    jobs = Job.query.all()

    return render_template("admin.html", candidates=candidates, jobs=jobs)


# ---------------- ADD JOB ----------------

@app.route("/add-job", methods=["POST"])
def add_job():

    if not session.get("admin"):
        return redirect("/login")

    title = request.form.get("title")
    location = request.form.get("location")
    job_type = request.form.get("type")

    job = Job(title=title, location=location, job_type=job_type)

    db.session.add(job)
    db.session.commit()

    return redirect("/admin")


# ---------------- RESUME DOWNLOAD ----------------

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ---------------- RUN SERVER ----------------

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)