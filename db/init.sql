CREATE DATABASE psych_collab;
USE psych_collab;
CREATE TABLE word(word_id INT PRIMARY KEY AUTO_INCREMENT, word_name NVARCHAR(50), student_fname NVARCHAR(30), student_lname NVARCHAR(30), student_email NVARCHAR(50));
CREATE TABLE pair(pair_id INT PRIMARY KEY AUTO_INCREMENT, word1 INT, word2 INT, FOREIGN KEY(word1) REFERENCES word(word_id), FOREIGN KEY(word2) REFERENCES word(word_id));
CREATE TABLE admin(admin_id INT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(30), password BLOB, salt BLOB)
