import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="password123"
)
my_cursor = mydb.cursor()
my_cursor.execute("CREATE DATABASE our_bank")
my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)