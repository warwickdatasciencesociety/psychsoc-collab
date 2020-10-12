import mysql.connector
import os
import sys
import hashlib
from dotenv import load_dotenv

load_dotenv()

choice = input("WARNING: WILL OVERWRITE ANY SAVED DATA ARE YOU SURE YOU WANT TO RUN? [y/n]")
if choice == "y":
    confirm = input("ARE YOU SURE? [y/n]")
    if confirm == "y":
        print("proceeding")
    else:
        sys.exit(0)
else:
    sys.exit(0)
mydb = mysql.connector.connect(
    host="127.00.00.1",
    port="32000",
    user="root",
    password="root"
)

mycursor = mydb.cursor()


mycursor.execute("SHOW DATABASES")
flag = False
for x in mycursor:
    if 'psych_collab' in x:
        flag = True


if not flag:
    mycursor.execute("CREATE DATABASE psych_collab")





mycursor.execute("USE psych_collab")
mycursor.execute("SET FOREIGN_KEY_CHECKS = 0")
mycursor.execute("DROP TABLE IF EXISTS word")
mycursor.execute("DROP TABLE IF EXISTS pair")
mycursor.execute("DROP TABLE IF EXISTS admin")
mycursor.execute("SET FOREIGN_KEY_CHECKS = 1")
mycursor.execute(
    "CREATE TABLE word(word_id INT PRIMARY KEY AUTO_INCREMENT, word_name NVARCHAR(50), student_fname NVARCHAR(30), student_lname NVARCHAR(30), student_email NVARCHAR(50));"
    )
mycursor.execute("CREATE TABLE pair(pair_id INT PRIMARY KEY AUTO_INCREMENT, word1 INT, word2 INT, FOREIGN KEY(word1) REFERENCES word(word_id), FOREIGN KEY(word2) REFERENCES word(word_id));")
mycursor.execute(
    "CREATE TABLE admin(admin_id INT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(30), password BLOB, salt BLOB)")

mycursor.execute("SHOW TABLES")

for x in mycursor:
    print(x)

# USERS
sql = "INSERT INTO admin (username, password, salt) VALUES (%s, %s, %s)"
password = "root"
salt = os.urandom(32)
print(salt)
key = hashlib.pbkdf2_hmac(
    'sha256',  # The hash digest algorithm for HMAC
    password.encode('utf-8'),  # Convert the password to bytes
    salt,  # Provide the salt
    100000  # It is recommended to use at least 100,000 iterations of SHA-256
)
# print(key.decode('utf-8'))
val = ("admin", key, salt)
mycursor.execute(sql, val)
mydb.commit()

sql = "INSERT INTO word (word_name, student_fname, student_lname, student_email) VALUES (%s, %s, %s, %s)"
for i in range(6):
    val = (str(i), str(i), str(i), str(i))
    mycursor.execute(sql, val)

mydb.commit()

