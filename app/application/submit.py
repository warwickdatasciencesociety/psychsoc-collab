from flask import Blueprint, request, redirect, render_template, session
from flask import current_app as app
from .models import Word
from . import db

# blueprint configuration
submit_bp = Blueprint("submit_bp", __name__)

# a simple HTML form to submit a basic entry
@submit_bp.route("/submit", methods=["GET", "POST"])
def submit_word():
    if "submitted" in session:
        if session["submitted"] == True:
            return render_template("error.html", message="You've already submitted a choice!")
    # if a POST request, get JSON data and add to database
    # some rudimentary checks
    if request.method == "POST":
        try:
            entry = Word(
                word_name=request.form["word_name"],
                student_fname=request.form["student_fname"],
                student_lname=request.form["student_lname"],
                student_email=request.form["student_email"])
            db.session.add(entry)
            db.session.commit()
            session["submitted"] = True
            return redirect("/")
        except Exception as e:
            return str(e)
    # otherwise, get the submission page
    return render_template("submit.html")
