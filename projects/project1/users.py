# Author:Rg
# Project 1: Persistent SQLite User Directory

import sqlite3

DB_NAME = "users.db"


def setup_database(cursor: sqlite3.Cursor) -> None:
    """Create the user table if it does not exist and seed 5 initial Marvel records once."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user (
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            street_address TEXT,
            city TEXT,
            state TEXT,
            zipcode TEXT
        );
        """
    )

    cursor.execute("SELECT COUNT(*) FROM user;")
    if cursor.fetchone()[0] == 0:
        initial_users = [
            ("Tony", "Stark", "ironman@stark.com", "555-111-2222", "10880 Malibu Point", "Malibu", "CA", "90265"),
            ("Carol", "Danvers", "marvel@stark.com", "555-123-2424", "1233 Michigan Ave", "Boston", "MA", "02115"),
            ("Steve", "Rogers", "cap@avengers.org", "555-234-5678", "569 Leaman Place", "Brooklyn", "NY", "11201"),
            ("Natasha", "Romanoff", "widow@shield.gov", "555-345-6789", "412 Potomac Pkwy", "Arlington", "VA", "22201"),
            ("Peter", "Parker", "spidey@queens.edu", "555-456-7890", "20 Ingram Street", "Forest Hills", "NY", "11375"),
        ]
        cursor.executemany(
            """
            INSERT INTO user (
                first_name, last_name, email, phone, street_address, city, state, zipcode
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            initial_users,
        )


def report_all_names(cursor: sqlite3.Cursor) -> None:
    """Report 1: Display rowid and full names for all users."""
    cursor.execute("SELECT rowid, first_name, last_name FROM user ORDER BY rowid;")
    rows = cursor.fetchall()

    print(f"\n{'ID':<4} {'Full Name':<25}")
    print("-" * 30)
    for row_id, first, last in rows:
        print(f"{row_id:<4} {f'{first} {last}':<25}")
    print()


def report_contact_info(cursor: sqlite3.Cursor) -> None:
    """Report 2: Display full names, email addresses, and phone numbers."""
    cursor.execute("SELECT first_name, last_name, email, phone FROM user ORDER BY last_name;")
    rows = cursor.fetchall()

    print(f"\n{'Name':<22} {'Email':<25} {'Phone':<15}")
    print("-" * 64)
    for first, last, email, phone in rows:
        print(f"{f'{first} {last}':<22} {email:<25} {phone:<15}")
    print()


def report_mailing_addresses(cursor: sqlite3.Cursor) -> None:
    """Report 3: Display full names and complete mailing addresses."""
    cursor.execute(
        """
        SELECT first_name, last_name, street_address, city, state, zipcode
        FROM user
        ORDER BY state, city;
        """
    )
    rows = cursor.fetchall()

    print(f"\n{'Name':<22} {'Mailing Address':<45}")
    print("-" * 68)
    for first, last, street, city, state, zipcode in rows:
        full_address = f"{street}, {city}, {state} {zipcode}"
        print(f"{f'{first} {last}':<22} {full_address:<45}")
    print()


def add_user(conn: sqlite3.Connection, cursor: sqlite3.Cursor) -> None:
    """Prompt for new user fields and save persistently using parameterized SQL."""
    print("\nAdd New USER")
    print("-" * 20)
    first_name = input("Enter first name: ").strip()
    last_name = input("Enter last name: ").strip()
    email = input("Enter email address: ").strip()
    phone = input("Enter phone number: ").strip()
    street_address = input("Enter street address: ").strip()
    city = input("Enter city: ").strip()
    state = input("Enter 2-digit state abbreviation: ").strip().upper()
    zipcode = input("Enter zipcode: ").strip()

    cursor.execute(
        """
        INSERT INTO user (
            first_name, last_name, email, phone, street_address, city, state, zipcode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (first_name, last_name, email, phone, street_address, city, state, zipcode),
    )
    conn.commit()
    print(f"\n{first_name} {last_name} has been entered into the USER table.\n")


def display_menu() -> None:
    print("* * * MENU * * *")
    print("1 - List all NAMES in the user table")
    print("2 - List NAMES and email/phone for all users")
    print("3 - List NAMES and mailing addresses for all users")
    print("4 - Add new User")
    print("5 - Exit the program")


def main() -> None:
    print("SQLSuperlite App - MARVEL User Directory\n")

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        setup_database(cursor)
        conn.commit()

        while True:
            display_menu()
            choice = input("\nYour choice: ").strip()

            if choice == "1":
                report_all_names(cursor)
            elif choice == "2":
                report_contact_info(cursor)
            elif choice == "3":
                report_mailing_addresses(cursor)
            elif choice == "4":
                add_user(conn, cursor)
            elif choice == "5":
                print("\nThank you for using SQLSuperlite App.")
                break
            else:
                print("\nInvalid choice. Please enter a number from 1 to 5.\n")


if __name__ == "__main__":
    main()
