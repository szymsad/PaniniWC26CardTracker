import sqlite3
from contextlib import contextmanager


DB_NAME = "cards.db"

special = {0: "FF", 1: "", 2: "ICON"}

COUNTRIES = {
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
    "KOR": "Korea Republic",
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
    "SUI": "Switzerland",
    "TUN": "Tunisia",
    "USA": "United States",
    "URU": "Uruguay",
    "UZB": "Uzbekistan",
}

_COUNTRY_NAMES = set(COUNTRIES.values())

# Standardowe kolumny zwracane przez większość zapytań o karty
_CARD_COLUMNS = """
    c.card_number,
    c.card_name,
    c.category,
    col.quantity
"""

_CARD_JOIN = """
    FROM cards c
    LEFT JOIN collection col ON c.card_number = col.card_number
"""


@contextmanager
def get_db():
    """Context manager — automatycznie commituje i zamyka połączenie."""
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def get_country(code: str) -> str | None:
    """
    Zwraca pełną nazwę kraju lub None jeśli kod/nazwa są nieprawidłowe.
    Przyjmuje:
      - kod trzyliterowy: 'POL', '(POL)'
      - pełną nazwę: 'Poland'
    """
    code = code.strip()

    if code.startswith("(") and code.endswith(")") and len(code) == 5:
        return COUNTRIES.get(code[1:4])

    if code.upper() in COUNTRIES:
        return COUNTRIES[code.upper()]

    normalized = code.lower().title()
    if normalized in _COUNTRY_NAMES:
        return normalized

    return None


def initialize_database():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                card_number INTEGER PRIMARY KEY,
                card_name   TEXT NOT NULL,
                category    TEXT,
                country     TEXT,
                position    TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS collection (
                card_number INTEGER PRIMARY KEY,
                quantity    INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(card_number) REFERENCES cards(card_number)
            )
        """)


def add_card(card_number: int) -> bool:
    """Zwraca True jeśli karta była nowa (przed dodaniem jej nie było)."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT quantity FROM collection WHERE card_number = ?",
            (card_number,),
        )
        row = cur.fetchone()
        was_new = row is None or row[0] == 0

        cur.execute("""
            INSERT INTO collection(card_number, quantity) VALUES(?, 1)
            ON CONFLICT(card_number) DO UPDATE SET quantity = quantity + 1
        """, (card_number,))

    return was_new


def remove_card(card_number: int):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE collection SET quantity = quantity - 1 WHERE card_number = ? AND quantity > 0",
            (card_number,),
        )
        cur.execute(
            "DELETE FROM collection WHERE card_number = ? AND quantity <= 0",
            (card_number,),
        )


def get_card(card_number: int):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            f"SELECT {_CARD_COLUMNS} {_CARD_JOIN} WHERE c.card_number = ?",
            (card_number,),
        )
        return cur.fetchone()


def get_duplicates():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT {_CARD_COLUMNS}
            FROM collection col
            JOIN cards c ON c.card_number = col.card_number
            WHERE col.quantity > 1
            ORDER BY c.card_number
        """)
        return cur.fetchall()


def get_stats():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM collection WHERE quantity > 0")
        owned = cur.fetchone()[0]

        cur.execute("SELECT SUM(quantity) FROM collection WHERE quantity > 0")
        total_owned = cur.fetchone()[0] or 0

    total_cards = 630
    return {
        "owned": owned,
        "missing": total_cards - owned,
        "percentage": round((owned / total_cards) * 100, 2),
        "all cards": total_owned,
    }


def get_missing():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT {_CARD_COLUMNS}
            {_CARD_JOIN}
            WHERE col.quantity IS NULL OR col.quantity = 0
            ORDER BY c.card_number
        """)
        return cur.fetchall()


def get_owned_cards():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT {_CARD_COLUMNS}
            {_CARD_JOIN}
            WHERE col.quantity > 0
            ORDER BY c.card_number
        """)
        return cur.fetchall()


def get_cards_by_country(code: str):
    country = get_country(code)
    if country is None:
        return 0

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(F"""
            SELECT {_CARD_COLUMNS}
            FROM cards c
            LEFT JOIN collection col ON c.card_number = col.card_number
            WHERE c.country = ? AND c.category = 'National Team'
            ORDER BY c.card_number
        """, (country,))
        return cur.fetchall()


def get_country_stats(code: str):
    country = get_country(code)
    if country is None:
        return 0

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN col.quantity > 0 THEN 1 ELSE 0 END) AS owned
            FROM cards c
            LEFT JOIN collection col ON c.card_number = col.card_number
            WHERE c.country = ? AND c.category = 'National Team'
        """, (country,))
        total, owned = cur.fetchone()

    owned = owned or 0
    if total == 0:
        return None

    return {
        "country": country,
        "owned": owned,
        "missing": total - owned,
        "total": total,
        "percentage": round((owned / total) * 100, 2),
    }