from . import db

class Word(db.Model):
    __tablename__ = "word"
    word_id = db.Column(db.Integer, primary_key=True)
    word_name = db.Column(db.String)
    student_fname = db.Column(db.String)
    student_lname = db.Column(db.String)
    student_email = db.Column(db.String)
    verified = db.Column(db.Integer)

class Pair(db.Model):
    __tablename__ = "pair"
    pair_id = db.Column(db.Integer, primary_key=True)
    word1 = db.Column(db.Integer, db.ForeignKey("word.word_id"))
    word2 = db.Column(db.Integer, db.ForeignKey("word.word_id"))
    is_left = db.Column(db.Boolean)

class Admin(db.Model):
    __tablename__ = "admin"
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.BLOB)
    salt = db.Column(db.BLOB)
