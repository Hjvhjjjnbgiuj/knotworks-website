from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# secret key for login sessions
app.secret_key = "knotwork_secret_key"

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///candidates.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)


# Candidate Model
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    education = db.Column(db.String(200))
    experience = db.Column(db.String(200))
    about = db.Column(db.Text)
    resume = db.Column(db.String(200))


# Home
@app.route("/")
def home():
    return render_template("index.html")


# About
@app.route("/about")
def about():
    return render_template("about.html")


# Services
@app.route("/services")
def services():
    return render_template("services.html")


# Jobs
@app.route("/jobs")
def jobs():
    return render_template("jobs.html")


# Contact
@app.route("/contact")
def contact():
    return render_template("contact.html")


# Career / Resume upload
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

        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)

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


# Thankyou page
@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


# --------------------
# ADMIN LOGIN SYSTEM
# --------------------

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


# create database
with app.app_context():
    db.create_all()


# render server start
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)