CREATE DATABASE psych_collab;
USE psych_collab;
CREATE TABLE word(word_id INT PRIMARY KEY AUTO_INCREMENT, word_name NVARCHAR(50), student_fname NVARCHAR(30), student_lname NVARCHAR(30), student_email NVARCHAR(50), occurrences INT, verified BIT);
CREATE TABLE pair(pair_id INT PRIMARY KEY AUTO_INCREMENT, word1 INT, word2 INT, is_left BIT, FOREIGN KEY(word1) REFERENCES word(word_id), FOREIGN KEY(word2) REFERENCES word(word_id));
CREATE TABLE admin(admin_id INT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(30), password BLOB, salt BLOB)
INSERT INTO word(word_name, student_email, occurences, verified) VALUES ('Love', 'hello@wdss.io', 1, 1)
INSERT INTO word(word_name, student_email, occurences, verified) VALUES ('Dinosaur', 'hello@wdss.io', 1, 1)
INSERT INTO word(word_name, student_email, occurences, verified) VALUES ('Poop', 'hello@wdss.io', 1, 1)
INSERT INTO word(word_name, student_email, occurences, verified) VALUES ('Memes', 'hello@wdss.io', 1, 1)
INSERT INTO word(word_name, student_email, occurences, verified) VALUES ('Supercalifragilisticexpialidocious', 'hello@wdss.io', 1, 1)
INSERT INTO word(word_name, student_email, occurences, verified) VALUES ('War', 'hello@wdss.io', 1, 1)
INSERT INTO word(word_name, student_email, occurences, verified) VALUES ('God', 'hello@wdss.io', 1, 1)
INSERT INTO word(word_name, student_email, occurences, verified) VALUES ('Death', 'hello@wdss.io', 1, 1)
INSERT INTO word(word_name, student_email, occurences, verified) VALUES ('Pizza', 'hello@wdss.io', 1, 1)
INSERT INTO word(word_name, student_email, occurences, verified) VALUES ('Coincidence', 'hello@wdss.io', 1, 1)
