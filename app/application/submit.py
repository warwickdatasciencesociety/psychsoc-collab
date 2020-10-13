from flask import Blueprint, request, redirect, render_template, session, url_for
from flask import current_app as app
from .models import Word
from . import db

# blueprint configuration
submit_bp = Blueprint("submit_bp", __name__)

# a simple HTML form to submit a basic entry
@submit_bp.route("/submit", methods=["GET", "POST"])
def submit_word():
    # if a POST request, get JSON data and add to database
    # some rudimentary checks
    if request.method == "POST":
        try:
            entry = Word(
                word_name=request.form["word_name"].title(),
                student_fname=request.form["student_fname"],
                student_lname=request.form["student_lname"],
                student_email=request.form["student_email"],
                verified=0)
            session["submitted"] = True
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for("choose_bp.index"))
        except Exception as e:
            return render_template("error.html", message=str(e))
    # otherwise, get the submission page
    return render_template("submit.html")

