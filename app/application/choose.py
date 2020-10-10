from flask import Blueprint, session, render_template, request, redirect
from flask import current_app as app
import random
from .models import Word, Pair
from . import db

# blueprint configuration
choose_bp = Blueprint("choose_bp", __name__)

# this is the root page
@choose_bp.route("/", methods=["GET", "POST"])
def index():
    # set session variables if not set already
    if "remaining" not in session:
        session["remaining"] = 5
    if "submitted" not in session:
        session["submitted"] = False
    
    if request.method == "POST":
        try:
            if request.form["choice"] == "0":
                entry = Pair(
                    word1=session["entryOne"],
                    word2=session["entryTwo"])
            else:
                entry = Pair(
                    word1=session["entryTwo"],
                    word2=session["entryOne"])
            session["remaining"] -= 1
            db.session.add(entry)
            db.session.commit()
        except Exception as e:
            return redirect(request.url)

    if session["remaining"] > 0:
        # present user with two random choices
        # get all of the entries first
        allEntries = Word.query.all()

        chosenEntries = random.sample(allEntries, k=2)
        entryOne = chosenEntries[0]
        entryTwo = chosenEntries[1]

        session["entryOne"] = entryOne.word_id
        session["entryTwo"] = entryTwo.word_id

        # we have everything ready to put it into an HTML template
        return render_template("index.html", entryOne=entryOne.word_name, entryTwo=entryTwo.word_name, submitted=session["submitted"])

    return render_template("error.html", message="You've now decided on the maximum number of choices.") 
