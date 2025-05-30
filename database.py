import sqlite3

def init_db():
    con = sqlite3.connect("marketplace.db")  # besser mit .db
    cursor = con.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user (
        ID INTEGER PRIMARY KEY,
        name VARCHAR(20),
        surname VARCHAR(20),
        email VARCHAR(40) UNIQUE,
        password VARCHAR(30),
        street VARCHAR(30),
        street_number INTEGER,
        number VARCHAR(20),
        role VARCHAR(10),
        created_at DATETIME
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data (
        ID INTEGER PRIMARY KEY,
        user_id INTEGER,
        title VARCHAR(20),
        info VARCHAR(40),
        category VARCHAR(30),
        picture VARCHAR(30), 
        created_at DATETIME,
        updated_at DATETIME,
        FOREIGN KEY (user_id) REFERENCES user(ID)
    )
    """)

    con.commit()
    con.close()
