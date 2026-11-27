import sqlite3

DB_NAME = "myDatabase.db"


def setup_database(cursor: sqlite3.Cursor) -> None:
    cursor.execute("DROP TABLE IF EXISTS users;")
    cursor.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            street_address TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT
        );
        """
    )


def seed_users(cursor: sqlite3.Cursor) -> None:
    sample_users = [
        ("Tony", "Stark", "ironman@stark.com", "555-111-2222", "12345 Main Street", "Malibu", "CA", "98581"),
        ("Carol", "Danvers", "marvel@stark.com", "555-123-2424", "1233 Michigan Ave.", "Boston", "MA", "00248"),
    ]
    cursor.executemany(
        """
        INSERT INTO users (first_name, last_name, email, phone, street_address, city, state, zip_code)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        sample_users,
    )


def display_users(cursor: sqlite3.Cursor) -> None:
    cursor.execute("SELECT id, first_name, last_name, email FROM users;")
    rows = cursor.fetchall()

    print(f"{'ID':<4} {'Name':<20} {'Email':<25}")
    print("-" * 50)
    for user_id, first, last, email in rows:
        print(f"{user_id:<4} {f'{first} {last}':<20} {email:<25}")


def main() -> None:
    print("SQLite Practice - User Directory\n")

    # 'with' automatically commits changes on success and rolls back on errors
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        setup_database(cursor)
        seed_users(cursor)
        display_users(cursor)


if __name__ == "__main__":
    main()
