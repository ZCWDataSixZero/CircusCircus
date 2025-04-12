-- Create sample users
CREATE DATABASE IF NOT EXISTS flaskdb;
CREATE USER 'flaskuser'@'%' IDENTIFIED BY 'flaskpass';
GRANT ALL PRIVILEGES ON flaskdb.* TO 'flaskuser'@'%';

