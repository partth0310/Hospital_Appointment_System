import json
import os
import sqlite3

DATABASE_NAME = "hospital.db"
USERS_FILE = "users.json"
APPOINTMENTS_FILE = "appointments.json"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def load_json(filename):
    if not os.path.exists(filename):
        return []

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, OSError):
        return []


def migrate_users():
    users = load_json(USERS_FILE)

    conn = get_connection()
    cursor = conn.cursor()

    for user in users:
        name = user.get("name", "")
        username = user.get("username", "")
        password = user.get("password", "")
        role = user.get("role", "User")

        if not username:
            continue

        cursor.execute(
            """
            SELECT id FROM users
            WHERE username = ?
            """,
            (username,)
        )

        existing_user = cursor.fetchone()

        if existing_user is None:
            cursor.execute(
                """
                INSERT INTO users
                (name, username, password, role)
                VALUES (?, ?, ?, ?)
                """,
                (name, username, password, role)
            )

    conn.commit()
    conn.close()

    return len(users)


def migrate_appointments():
    appointments = load_json(APPOINTMENTS_FILE)

    conn = get_connection()
    cursor = conn.cursor()

    for appointment in appointments:
        username = appointment.get("username", "")
        patient = appointment.get("patient", "")
        doctor = appointment.get("doctor", "")
        date = appointment.get("date", "")
        reason = appointment.get("reason", "")
        status = appointment.get("status", "Booked")

        if not patient or not doctor or not date:
            continue

        cursor.execute(
            """
            SELECT id FROM appointments
            WHERE username = ?
              AND patient = ?
              AND doctor = ?
              AND date = ?
              AND reason = ?
              AND status = ?
            """,
            (
                username,
                patient,
                doctor,
                date,
                reason,
                status
            )
        )

        existing_appointment = cursor.fetchone()

        if existing_appointment is None:
            cursor.execute(
                """
                INSERT INTO appointments
                (username, patient, doctor, date, reason, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    username,
                    patient,
                    doctor,
                    date,
                    reason,
                    status
                )
            )

    conn.commit()
    conn.close()

    return len(appointments)


if __name__ == "__main__":
    print("Starting data migration...")

    migrate_users()
    migrate_appointments()

    print("Users data migrated successfully!")
    print("Appointments data migrated successfully!")
    print("Migration completed successfully!")