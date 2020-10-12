from flask import Blueprint, request, redirect, render_template, session
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
            # see if the word already exists
            existing = Word.query.filter_by(word_name=request.form["word_name"]).first()
            if existing is not None:
                # add to the counter and present an error message
                existing.occurrences += 1
                db.session.commit()
                return render_template("error.html", message="Word has already been submitted!")
            entry = Word(
                word_name=request.form["word_name"],
                student_fname=request.form["student_fname"],
                student_lname=request.form["student_lname"],
                student_email=request.form["student_email"],
                occurrences=1)
            session["submitted"] = True
            db.session.add(entry)
            db.session.commit()
            return redirect("/goagain")
        except Exception as e:
            return render_template("error.html", message=str(e))
    # otherwise, get the submission page
    return render_template("submit.html")

# an even simpler HTML form to ask if they want to submit another word
@submit_bp.route("/goagain", methods=["GET", "POST"])
def go_again():
    if request.method == "POST":
        if request.form["choice"] == "0":
            return redirect("/submit")
        return redirect("/")
    return render_template("goagain.html")
