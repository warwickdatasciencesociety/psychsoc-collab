CREATE DATABASE certificate_portal;
USE certificate_portal;
CREATE TABLE word(word_id INT PRIMARY KEY AUTO_INCREMENT, word NVARCHAR(50));
CREATE TABLE pair(pair_id INT PRIMARY KEY AUTO_INCREMENT, word1 INT, word2 INT, student_fname NVARCHAR(30), student_lname NVARCHAR(30), student_email NVARCHAR(50), FOREIGN KEY(word1) REFERENCES word(word_id), FOREIGN KEY(word2) REFERENCES word(word_id));
