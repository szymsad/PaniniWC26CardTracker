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


def get_country(code):
    if code[0] == '(' and code[4] == ')':
        decoded = code[1:4]
        countries_codes = {
            "ALG": "Algeria",
            "ARG": "Argentina",
            "AUS": "Australia",
            "AUT": "Austria",
            "BEL": "Belgium",
            "BRA": "Brazil",
            "CAN": "Canada",
            "CPV": "Cape Verde",
            "COL": "Colombia",
            "CIV": "Cote d'Ivoire",
            "CRO": "Croatia",
            "CUW": "Curacao",
            "CZE": "Czechia",
            "ECU": "Ecuador",
            "EGY": "Egypt",
            "ENG": "England",
            "FRA": "France",
            "GER": "Germany",
            "GHA": "Ghana",
            "HAI": "Haiti",
            "IRN": "Iran",
            "IRQ": "Iraq",
            "JPN": "Japan",
            "JOR": "Jordan",
            "KOR": "South Korea",
            "MAR": "Morocco",
            "MEX": "Mexico",
            "NED": "Netherlands",
            "NOR": "Norway",
            "NZL": "New Zealand",
            "PAN": "Panama",
            "PAR": "Paraguay",
            "POR": "Portugal",
            "QAT": "Qatar",
            "KSA": "Saudi Arabia",
            "SCO": "Scotland",
            "SEN": "Senegal",
            "RSA": "South Africa",
            "ESP": "Spain",
            "SWE": "Sweden",
            "SUI": "Switzerland",
            "TUN": "Tunisia",
            "TUR": "Turkey",
            "USA": "United States",
            "URU": "Uruguay",
            "UZB": "Uzbekistan",

            # Contender nations z checklisty
            "DEN": "Denmark",
            "ITA": "Italy",
            "JAM": "Jamaica",
            "POL": "Poland",
        }
        return countries_codes[decoded]
    else:
        countries = [
            "Algeria",
            "Argentina",
            "Australia",
            "Austria",
            "Belgium",
            "Brazil",
            "Canada",
            "Cape Verde",
            "Colombia",
            "Cote d'Ivoire",
            "Croatia",
            "Curacao",
            "Czechia",
            "Denmark",
            "Ecuador",
            "Egypt",
            "England",
            "France",
            "Germany",
            "Ghana",
            "Haiti",
            "Iran",
            "Iraq",
            "Italy",
            "Jamaica",
            "Japan",
            "Jordan",
            "South Korea",
            "Saudi Arabia",
            "Morocco",
            "Mexico",
            "Netherlands",
            "Norway",
            "New Zealand",
            "Panama",
            "Paraguay",
            "Poland",
            "Portugal",
            "Qatar",
            "Scotland",
            "Senegal",
            "South Africa",
            "Spain",
            "Switzerland",
            "Sweden",
            "Tunisia",
            "Turkey",
            "Uruguay",
            "United States",
            "Uzbekistan"
        ]
        code = code.lower().title()
        if code in countries:
            return code
    return "wrong code/country"

def get_list_country(code):
    conn = get_connection()
    cur = conn.cursor()

    country = get_country(code)

    cur.execute("""
        SELECT
            c.card_number,
            c.card_name,
            c.country,
            col.quantity
        FROM cards c
        JOIN collection col
            ON c.card_number = col.card_number
        WHERE c.country = ?
          AND col.quantity > 0
          AND c.category = "National Team"
        ORDER BY c.card_number
    """, (country,))

    rows = cur.fetchall()
    conn.close()

    return rows
