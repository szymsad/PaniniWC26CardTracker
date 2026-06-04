import sqlite3


DB_NAME = "cards.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS cards (
        card_number INTEGER PRIMARY KEY,
        card_name TEXT NOT NULL,
        category TEXT,
        country TEXT,
        position TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS collection (
        card_number INTEGER PRIMARY KEY,
        quantity INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(card_number) REFERENCES cards(card_number)
    )
    """)

    conn.commit()
    conn.close()


def add_card(card_number: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO collection(card_number, quantity)
    VALUES(?, 1)
    ON CONFLICT(card_number)
    DO UPDATE SET quantity = quantity + 1
    """, (card_number,))

    conn.commit()
    conn.close()


def remove_card(card_number: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE collection
    SET quantity = quantity - 1
    WHERE card_number = ? AND quantity > 0
    """, (card_number,))

    cur.execute("""
    DELETE FROM collection
    WHERE card_number = ? AND quantity <= 0
    """, (card_number,))

    conn.commit()
    conn.close()


def get_card(card_number: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        c.card_number,
        c.card_name,
        c.category,
        col.quantity
    FROM cards c
    LEFT JOIN collection col
        ON c.card_number = col.card_number
    WHERE c.card_number = ?
    """, (card_number,))

    result = cur.fetchone()
    conn.close()

    return result


def get_duplicates():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        c.card_number,
        c.card_name,
        col.quantity
    FROM collection col
    JOIN cards c
        ON c.card_number = col.card_number
    WHERE col.quantity > 1
    ORDER BY c.card_number
    """)

    rows = cur.fetchall()
    conn.close()

    return rows


def get_stats():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT COUNT(*)
    FROM collection
    WHERE quantity > 0
    """)

    owned = cur.fetchone()[0]

    cur.execute("""
            SELECT SUM(collection.quantity)
            FROM collection
            WHERE quantity > 0
    """)
    sum_cards = cur.fetchone()[0]
    total_cards = 630

    conn.close()

    return {
        "owned": owned,
        "missing": total_cards - owned,
        "percentage": round((owned / total_cards) * 100, 2),
        "all cards": sum_cards
    }


def get_missing():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
        c.card_number,
        c.card_name,
        c.country
    FROM cards c
    LEFT JOIN collection col
        ON c.card_number = col.card_number
    WHERE col.quantity IS NULL
       OR col.quantity = 0
    ORDER BY c.card_number
    """)

    rows = cur.fetchall()
    conn.close()

    return rows
