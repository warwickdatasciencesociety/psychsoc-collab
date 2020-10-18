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
        session["remaining"] = 10
    if "submitted" not in session:
        session["submitted"] = False
    
    if request.method == "POST":
        try:
            if request.form["choice"] == "0":
                entry = Pair(
                    word1=session["entryOne"],
                    word2=session["entryTwo"],
                    is_left=True)
            else:
                entry = Pair(
                    word1=session["entryTwo"],
                    word2=session["entryOne"],
                    is_left=False)
            session["remaining"] -= 1
            db.session.add(entry)
            db.session.commit()
        except Exception as e:
            return render_template("error.html", message=str(e))

    if session["remaining"] > 0 or session["submitted"]:
        # present user with two random choices
        # get all of the entries first
        nonSeedEntries = Word.query.filter((Word.verified==1) & (Word.student_email!="seed")).all()

        seedEntries = Word.query.filter((Word.verified==1) & (Word.student_email=="seed")).all()

        allEntries = nonSeedEntries + seedEntries

        # create a weights list (order IS important)
        weightedVals = list()

        for entry in nonSeedEntries:
            weightedVals.append(1/len(nonSeedEntries))

        for entry in seedEntries:
            weightedVals.append(1/len(seedEntries))

        entryOne = ""
        entryTwo = ""

        while entryOne == entryTwo:

            chosenEntries = random.choices(allEntries, weights=weightedVals, k=2)
            entryOne = chosenEntries[0]
            entryTwo = chosenEntries[1]

            session["entryOne"] = entryOne.word_id
            session["entryTwo"] = entryTwo.word_id

        # we have everything ready to put it into an HTML template
        return render_template("index.html", entryOne=entryOne.word_name, entryTwo=entryTwo.word_name, remaining=session["remaining"], submitted=session["submitted"])

    return redirect("/submit")
