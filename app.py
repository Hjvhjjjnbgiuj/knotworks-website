from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///candidates.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload folder
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

# Home Page
@app.route("/")
def home():
    return render_template("index.html")

# About Page
@app.route("/about")
def about():
    return render_template("about.html")

# Services Page
@app.route("/services")
def services():
    return render_template("services.html")

# Jobs Page
@app.route("/jobs")
def jobs():
    return render_template("jobs.html")

# Career Page (Resume Upload)
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

        upload_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(upload_path)

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

# Contact Page
@app.route("/contact")
def contact():
    return render_template("contact.html")

# Thank You Page
@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

# Admin Panel
@app.route("/admin")
def admin():

    candidates = Candidate.query.all()

    return render_template("admin.html", candidates=candidates)

# Create database automatically
with app.app_context():
    db.create_all()

# Render Server Start
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)