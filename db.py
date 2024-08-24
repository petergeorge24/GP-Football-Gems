import sqlite3

conn  =  sqlite3.connect("users.sqlite")

cursor = conn.cursor()

sql_query = """
    CREATE TABLE User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name text unique,
    password text not null,
    height double not null,
    weight double not null,
    age integer not null,
    gender text not null,
    prefeardFoot text not null
    )
"""

cursor.execute(sql_query)

sql_query = """
    CREATE TABLE Challenge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    result double,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES User (id)
    )
"""

# cursor.execute(sql_query)