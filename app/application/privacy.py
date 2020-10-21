from flask import Blueprint, session, render_template, request, redirect
from flask import current_app as app
import random
from .models import Word, Pair
from . import db

# blueprint configuration
privacy_bp = Blueprint("privacy_bp", __name__)

# this is the root page
@privacy_bp.route("/privacy", methods=["GET"])
def privacy():
    # set session variables if not set already
    
    return render_template("privacypolicy.html")
