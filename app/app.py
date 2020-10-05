import time
import os
import random

from flask import (
    Flask,
    render_template,
    request,
    abort,
    jsonify,
    redirect,
    url_for)
from flask import send_file

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)

from werkzeug.security import safe_str_cmp
import requests
import jinja2
import pdfkit
import datetime
import hashlib
import uuid
from os import listdir
from os.path import isfile, join
from PyPDF2 import PdfFileWriter, PdfFileReader
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from dotenv import load_dotenv
import pymysql
import jsonpickle


load_dotenv()
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

app.config['JWT_TOKEN_LOCATION'] = ['cookies']

# Set the cookie paths, so that you are only sending your access token
# cookie to the access endpoints, and only sending your refresh token
# to the refresh endpoint. Technically this is optional, but it is in
# your best interest to not send additional cookies in the request if
# they aren't needed.
app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'

# Disable CSRF protection for this example. In almost every case,
# this is a bad idea. See examples/csrf_protection_with_cookies.py
# for how safely store JWTs in cookies
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

# Set the secret key to sign the JWTs with
app.config['JWT_SECRET_KEY'] = 'Jiowaj213eddDw'  # Change this!

jwt = JWTManager(app)


app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://root:{os.environ['SQL_ROOT_PASSWORD']}@db:3306/certificate_portal"
# the variable to be used for all SQLAlchemy commands
db = SQLAlchemy(app)


class Mentor(db.Model):
    __tablename__ = "mentor"
    mentor_id = db.Column(db.Integer, primary_key=True)
    mentor_fname = db.Column(db.String)
    mentor_lname = db.Column(db.String)


class Student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer, primary_key=True)
    student_fname = db.Column(db.String)
    student_lname = db.Column(db.String)
    student_email = db.Column(db.String)


class Course(db.Model):
    __tablename__ = "course"
    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String)
    course_details = db.Column(db.String)


class Certification(db.Model):
    __tablename__ = "certification"
    certification_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.student_id"))
    course_id = db.Column(db.Integer, db.ForeignKey("course.course_id"))
    mentor_id = db.Column(db.Integer, db.ForeignKey("mentor.mentor_id"))
    certification_code = db.Column(db.String)
    certification_date = db.Column(db.DateTime)

class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.BLOB)
    salt = db.Column(db.BLOB)

@app.route('/')
def home():
    return redirect("https://www.wdss.io/")


@app.route('/token/auth', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        # hash user password\
        if not request.json:
            entered_username = request.form["username"]
            entered_pass = request.form["password"]
        else:
            entered_username = request.json["username"]
            entered_pass = request.json["password"]

        # get username and password from database
        user = User.query.filter_by(username=entered_username).first()
        username = user.username
        password = user.password
        salt = user.salt

        key = hashlib.pbkdf2_hmac(
            'sha256', # The hash digest algorithm for HMAC
            entered_pass.encode('utf-8'), # Convert the password to bytes
            salt, # Provide the salt
            100000 # It is recommended to use at least 100,000 iterations of SHA-256 
        )
        
        # compare the values
        if entered_username != username or key != password:
            error = f'Invalid Credentials. Please try again.'
        else:
            dictToSend = {
                'username': entered_username,
                'password': entered_pass
            }
            access_token = create_access_token(identity=dictToSend['username'])
            refresh_token = create_refresh_token(
                identity=dictToSend['username'])
            # Set the JWT cookies in the response
            resp = jsonify({'login': True, 'access_token': access_token, 'refresh_token': refresh_token})
            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)
            
            return resp, 200
    return render_template('login.html', error=error)


@app.route('/token/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    # Create the new access token
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)

    # Set the JWT access cookie in the response
    resp = jsonify({'refresh': True})
    set_access_cookies(resp, access_token)
    return resp, 200

# Because the JWTs are stored in an httponly cookie now, we cannot
# log the user out by simply deleting the cookie in the frontend.
# We need the backend to send us a response to delete the cookies
# in order to logout. unset_jwt_cookies is a helper function to
# do just that.


@app.route('/token/remove', methods=['POST'])
def logout():
    resp = jsonify({'logout': True})
    unset_jwt_cookies(resp)
    return resp, 200


# test the database connection through this route (for debugging)
@app.route("/api/dbtest")
@jwt_required
def testdb():
    try:
        db.session.query("1").from_statement(text("SELECT 1")).all()
        return "<h1>It works.</h1>"
    except Exception as e:
        # e holds descirption of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = "<h1>Something is broken.</h1>"
        return hed + error_text


def generate_pdf(name, mentor, course, details, cert_id):
    templateLoader = jinja2.FileSystemLoader(searchpath="./")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "templates/htmltemplate.html"
    template = templateEnv.get_template(TEMPLATE_FILE)
    outputText = template.render(
        id=cert_id,
        name=name,
        course_name=course,
        additional_course_details=details,
        date=datetime.date.today(),
        mentor=mentor)
    
    html_file = open('templates/certificate.html', 'w')
    html_file.write(outputText)
    html_file.close()
    
    options = {
        "enable-local-file-access": None,
        "orientation": "Landscape",
        "background": None,
        'margin-top': '0',
        'margin-right': '0',
        'margin-bottom': '0',
        'margin-left': '0',
    }
    try:
        dest = f'static/certificates/wdss_cert_{cert_id}.pdf'
        pdfkit.from_file('templates/certificate.html', dest, options=options)
    
        infile = PdfFileReader(f'static/certificates/wdss_cert_{cert_id}.pdf', 'rb')
        output = PdfFileWriter()
        p = infile.getPage(0)
        output.addPage(p)
        
        with open(f'static/certificates/wdss_cert_{cert_id}.pdf', 'wb') as f:
            output.write(f)
    except Exception as e:
        return str(e)
    return True
# CRUD endpoints


@app.route("/api/crud/<table>", methods=["POST", "GET"])
@jwt_required
def crudTable(table):
    # create a new entry
    if request.method == "POST":
        # no checking - just throw an exception if SQL fails
        if table == "mentor":
            entry = Mentor(
                mentor_fname=request.json["mentor_fname"],
                mentor_lname=request.json["mentor_lname"])
        elif table == "student":
            entry = Student(
                student_fname=request.json["student_fname"],
                student_lname=request.json["student_lname"],
                student_email=request.json["student_email"])
        elif table == "course":
            entry = Course(
                course_name=request.json["course_name"],
                course_details=request.json["course_details"])
        elif table == "certification":
            # don't know when this would be used
            entry = Certification(
                student_id=request.json["student_id"],
                course_id=request.json["course_id"],
                mentor_id=request.json["mentor_id"],
                certification_code=request.json["certification_code"],
                certification_date=request.json["certification_date"])
        else:
            return f"Table {table} does not exist!"
        try:
            db.session.add(entry)
            db.session.commit()
            if table == "mentor":
                entry_id = entry.mentor_id
            elif table == "student":
                entry_id = entry.student_id
            elif table == "course":
                entry_id = entry.course_id
            elif table == "certification":
                entry_id = entry.certification_id
            resp = jsonify(success=True, id=entry_id)
            return resp
        except Exception as e:
            return str(e)

    # get all entries
    if table == "mentor":
        returnArray = Mentor.query.all()
    elif table == "student":
        returnArray = Student.query.all()
    elif table == "course":
        returnArray = Course.query.all()
    elif table == "certification":
        returnArray = Certification.query.all()
    else:
        return f"Table {table} does not exist!"

    return jsonpickle.encode(returnArray)


@app.route("/api/crud/<table>/<iden>", methods=["GET", "PUT", "DELETE"])
@jwt_required
def crudTableId(table, iden):
    if table == "mentor":
        field = Mentor.query.get_or_404(iden)
    elif table == "student":
        field = Student.query.get_or_404(iden)
    elif table == "course":
        field = Course.query.get_or_404(iden)
    elif table == "certification":
        field = Certification.query.get_or_404(iden)
    else:
        return f"Table {table} does not exist!"

    if request.method == "PUT":
        if table == "mentor":
            if "mentor_fname" in request.json:
                field.mentor_fname = request.json["mentor_fname"]
            if "mentor_lname" in request.json:
                field.mentor_lname = request.json["mentor_lname"]

        elif table == "student":
            if "student_fname" in request.json:
                field.student_fname = request.json["student_fname"]
            if "student_lname" in request.json:
                field.student_lname = request.json["student_lname"]

        elif table == "course":
            if "course_name" in request.json:
                field.course_name = request.json["course_name"]
            if "course_details" in request.json:
                field.course_details = request.json["course_details"]

        elif table == "certification":
            # don't know when this would be used
            if "student_id" in request.json:
                field.student_id = request.json["student_id"]
            if "course_id" in request.json:
                field.course_id = request.json["course_id"]
            if "mentor_id" in request.json:
                field.mentor_id = request.json["mentor_id"]
            if "certification_code" in request.json:
                field.certification_code = request.json["certification_code"]
            if "certification_date" in request.json:
                field.certification_date = request.json["certification_date"]

        else:
            return f"Table {table} does not exist!"
        try:
            db.session.commit()
            return redirect(request.url)
        except Exception as e:
            return str(e)

    if request.method == "DELETE":
        try:
            db.session.delete(field)
            db.session.commit()
            return f"Successfully deleted field with id {iden}"
        except Exception as e:
            return str(e)

    return jsonpickle.encode(field)

@app.route('/api/certificate/update', methods=['GET','POST'])
@jwt_required
def update():
    if request.method == "POST":
        cert_id = request.json["certificate_code"]
        cert_curr = Certification.query.filter_by(certification_code=cert_id).first_or_404()
        
        if "student_id" in request.json:
            student_id = request.json["student_id"]
        else:
            student_id = cert_curr.student_id
        
        if "mentor_id" in request.json:
            mentor_id = request.json["mentor_id"]
        else:
            mentor_id = cert_curr.mentor_id            
        
        if "course_id" in request.json:
            course_id = request.json["course_id"]
        else:
            course_id = cert_curr.course_id
        
        params = {
            "name": f"{Student.query.get_or_404(student_id).student_fname} {Student.query.get_or_404(student_id).student_lname}",
            "mentor": f"{Mentor.query.get_or_404(mentor_id).mentor_fname} {Mentor.query.get_or_404(mentor_id).mentor_lname}",
            "course": Course.query.get_or_404(course_id).course_name,
            "desc": Course.query.get_or_404(course_id).course_details,
        }
        

        
        try:
            cert = Certification.query.filter_by(certification_code=cert_id).update(dict(student_id=student_id, course_id=course_id, mentor_id=mentor_id))
            db.session.commit()
            
            x = generate_pdf(params['name'], params['mentor'],
                            params['course'], params['desc'], cert_id)
            
            resp = jsonify(cert_id=cert_id, success=True, msg=x)
            return resp
        except BaseException:
            return f"There was an issue updating your certificate {params} {cert_id}"
    mentors = Mentor.query.all()
    courses = Course.query.all()
    students = Student.query.all()
    return render_template('generate.html',
            mentors=mentors,
            courses=courses,
            students=students)

@app.route('/api/certificate/generate', methods=['GET', 'POST'])
@jwt_required
def generate():
    if request.method == 'POST':
        if not request.json:
            student_id = request.form["student"]
            mentor_id = request.form["mentor"]
            course_id = request.form["course"]
        else:
            student_id = request.json["student_id"]
            mentor_id = request.json["mentor_id"]
            course_id = request.json["course_id"]

        params = {
            "name": f"{Student.query.get_or_404(student_id).student_fname} {Student.query.get_or_404(student_id).student_lname}",
            "mentor": f"{Mentor.query.get_or_404(mentor_id).mentor_fname} {Mentor.query.get_or_404(mentor_id).mentor_lname}",
            "course": Course.query.get_or_404(course_id).course_name,
            "desc": Course.query.get_or_404(course_id).course_details
        }


        cert_id = str(random.randint(00000000, 99999999)).zfill(8)
        entry = Certification(
            student_id=student_id,
            course_id=course_id,
            mentor_id=mentor_id,
            certification_code=cert_id,
            certification_date=datetime.date.today())

        try:
            db.session.add(entry)
            db.session.commit()

            x = generate_pdf(params['name'], params['mentor'],
                         params['course'], params['desc'], cert_id)
            resp = jsonify(cert_id=cert_id, success=True, msg=x)
            return resp
        except BaseException:
            return f"There was an issue creating your certificate {params} {cert_id}"
    mentors = Mentor.query.all()
    courses = Course.query.all()
    students = Student.query.all()
    return render_template('generate.html',
            mentors=mentors,
            courses=courses,
            students=students)


@app.route('/api/htmltemplate')
@jwt_required
def htmltemplate():
    return render_template("htmltemplate.html")


@app.route('/api/preview')
@jwt_required
def preview():
    return render_template("certificate.html")


@app.route('/certificate/<iden>')
def certificate(iden):
    if iden == "00000000":
        return render_template(
                "cert.html",
                iden=url_for(
                    'static',
                    filename=f"certificates/wdss_cert_{iden}.pdf"),
                courseName="Introduction to Python",
                studentName="Ann Example",
                cert_id=iden)

    certInfo = Certification.query.filter_by(certification_code=iden).first()
    if certInfo is None:
        return "<p> Certificate does not exist or was not found. If you believe that this is a mistake, please email hello@warwickdatascience.com </p>"
    courseName = Course.query.get_or_404(certInfo.course_id).course_name
    studentName = f"{Student.query.get_or_404(certInfo.student_id).student_fname} {Student.query.get_or_404(certInfo.student_id).student_lname}"

    return render_template(
        "cert.html",
        iden=url_for(
            'static',
            filename=f"certificates/wdss_cert_{iden}.pdf"),
        courseName=courseName,
        studentName=studentName,
        cert_id=iden)



if __name__ == '__main__':
    app.run()
