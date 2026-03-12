from flask import Flask, render_template, request, redirect, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Secret key for login session
app.secret_key = "knotwork_secret_key"

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///candidates.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)


# ---------------------------
# Candidate Database Model
# ---------------------------
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    education = db.Column(db.String(200))
    experience = db.Column(db.String(200))
    about = db.Column(db.Text)
    resume = db.Column(db.String(200))


# ---------------------------
# Website Pages
# ---------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/jobs")
def jobs():
    return render_template("jobs.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


# ---------------------------
# Career / Resume Upload
# ---------------------------
@app.route("/career", methods=["GET", "POST"])
def career():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        education = request.form["education"]
        experience = request.form["experience"]
        about = request.form["about"]

        file = request.files["resume"]
        filename = file.filename

        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        candidate = Candidate(
            name=name,
            email=email,
            phone=phone,
            education=education,
            experience=experience,
            about=about,
            resume=filename
        )

        db.session.add(candidate)
        db.session.commit()

        return redirect("/thankyou")

    return render_template("career.html")


@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


# ---------------------------
# Resume Download Route
# ---------------------------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ---------------------------
# Admin Login System
# ---------------------------
ADMIN_USER = "admin"
ADMIN_PASS = "knotwork123"


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USER and password == ADMIN_PASS:
            session["admin"] = True
            return redirect("/admin")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/login")


@app.route("/admin")
def admin():

    if not session.get("admin"):
        return redirect("/login")

    candidates = Candidate.query.all()

    return render_template("admin.html", candidates=candidates)


# ---------------------------
# Create database automatically
# ---------------------------
with app.app_context():
    db.create_all()


# ---------------------------
# Start server (Render compatible)
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)