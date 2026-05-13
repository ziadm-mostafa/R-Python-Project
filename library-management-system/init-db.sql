IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'library_db')
BEGIN
    CREATE DATABASE library_db;
END