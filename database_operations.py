"""
database_operations.py
Business Logic Layer for the People Directory assignment.

This module owns the SQLite connection, database schema, validation rules,
and all Create, Read, Update, and Delete (CRUD) operations. The GUI should
call these functions instead of writing SQL statements itself.

Academic integrity note: This project was prepared with AI assistance.
Review the code, understand each function, and follow your instructor's
disclosure requirements before submitting.
"""

import re
import sqlite3
from pathlib import Path

# Store the database beside this Python file so the app can be moved as a folder.
DB_NAME = Path(__file__).with_name("people.db")

REQUIRED_FIELDS = {
    "first_name": "First name",
    "last_name": "Last name",
    "email": "Email",
    "street": "Street address",
    "city": "City",
    "state": "State",
    "zipcode": "ZIP code",
    "job_title": "Job title",
}
ALL_FIELDS = tuple(REQUIRED_FIELDS) + ("notes",)


def get_connection():
    """Open and return a SQLite connection with foreign-key support enabled."""
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_database():
    """
    Create the people table when it does not exist.

    All assignment-required fields are NOT NULL. Notes is the only optional
    field. The database is stored in people.db beside this module.
    """
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL CHECK (length(trim(first_name)) > 0),
                last_name  TEXT NOT NULL CHECK (length(trim(last_name)) > 0),
                email      TEXT NOT NULL CHECK (length(trim(email)) > 0),
                street     TEXT NOT NULL CHECK (length(trim(street)) > 0),
                city       TEXT NOT NULL CHECK (length(trim(city)) > 0),
                state      TEXT NOT NULL CHECK (length(trim(state)) > 0),
                zipcode    TEXT NOT NULL CHECK (length(trim(zipcode)) > 0),
                job_title  TEXT NOT NULL CHECK (length(trim(job_title)) > 0),
                notes      TEXT
            )
            """
        )


def validate_person_data(data):
    """
    Validate every required field before an INSERT or UPDATE.

    Returns (True, "") when valid, otherwise (False, helpful_error_message).
    Notes is intentionally excluded because it is the only optional field.
    """
    if not isinstance(data, dict):
        return False, "Person information must be provided as a dictionary."

    missing = [
        label for key, label in REQUIRED_FIELDS.items()
        if not str(data.get(key, "") or "").strip()
    ]
    if missing:
        return False, "Please complete all required fields: " + ", ".join(missing) + "."

    email = str(data.get("email", "")).strip()
    # A practical format check: text before @, a domain, and a domain suffix.
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        return False, "Please enter a valid email address (example: name@example.com)."

    zipcode = str(data.get("zipcode", "")).strip()
    if not re.fullmatch(r"\d{5}(?:-\d{4})?", zipcode):
        return False, "Please enter a valid ZIP code (12345 or 12345-6789)."

    return True, ""


def _clean_person_data(data):
    """Return a new dictionary containing trimmed values for every field."""
    cleaned = {key: str(data.get(key, "") or "").strip() for key in ALL_FIELDS}
    return cleaned


def add_person(data):
    """
    Create a person record after validating all required fields.

    Returns the new row ID. Raises ValueError for invalid input and lets
    database errors propagate to the calling GUI for clear error handling.
    """
    is_valid, message = validate_person_data(data)
    if not is_valid:
        raise ValueError(message)

    person = _clean_person_data(data)
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO people
                (first_name, last_name, email, street, city, state,
                 zipcode, job_title, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            tuple(person[field] for field in ALL_FIELDS),
        )
        return cursor.lastrowid


def get_all_people():
    """
    Read and return every person as a list of dictionaries.

    Results are alphabetized by last name and then first name for a clear list.
    """
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, first_name, last_name, email, street, city, state,
                   zipcode, job_title, notes
            FROM people
            ORDER BY last_name COLLATE NOCASE, first_name COLLATE NOCASE
            """
        ).fetchall()
        return [dict(row) for row in rows]


def get_person_by_id(person_id):
    """
    Read one complete person record by its unique ID.

    Returns a dictionary when found, or None when no matching record exists.
    """
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM people WHERE id = ?", (person_id,)
        ).fetchone()
        return dict(row) if row else None


def update_person(person_id, data):
    """
    Update all editable fields for one existing person after validation.

    Raises ValueError when required information is missing or invalid.
    Returns True when a record was updated, otherwise False.
    """
    is_valid, message = validate_person_data(data)
    if not is_valid:
        raise ValueError(message)

    person = _clean_person_data(data)
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE people
            SET first_name = ?, last_name = ?, email = ?, street = ?,
                city = ?, state = ?, zipcode = ?, job_title = ?, notes = ?
            WHERE id = ?
            """,
            tuple(person[field] for field in ALL_FIELDS) + (person_id,),
        )
        return cursor.rowcount > 0


def delete_person(person_id):
    """
    Delete one person by ID.

    Returns True when a record was deleted, or False if the ID was not found.
    """
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM people WHERE id = ?", (person_id,)
        )
        return cursor.rowcount > 0
