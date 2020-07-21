CREATE DATABASE ftown;
-- CREATE USER 'user_name'@'%' IDENTIFIED BY 'password';
CREATE USER 'database_user'@'%' IDENTIFIED BY 'database_password';
GRANT ALL PRIVILEGES ON ftown.* TO 'database_user'@'%';
