import streamlit as st
import sqlite3

# =========================
# PAGE SETTINGS
# =========================

st.set_page_config(
    page_title="Hospital Appointment Management System",
    page_icon="🏥",
    layout="wide"
)

# =========================
# DATABASE
# =========================

DATABASE_NAME = "hospital.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            patient TEXT NOT NULL,
            doctor TEXT NOT NULL,
            date TEXT NOT NULL,
            reason TEXT,
            status TEXT NOT NULL
        )
    """)

    # Default admin account
    cursor.execute("""
        SELECT * FROM users WHERE username = ?
    """, ("admin",))

    admin = cursor.fetchone()

    if not admin:
        cursor.execute("""
            INSERT INTO users
            (name, username, password, role)
            VALUES (?, ?, ?, ?)
        """, (
            "Administrator",
            "admin",
            "admin123",
            "Admin"
        ))

    conn.commit()
    conn.close()


create_tables()

# =========================
# DOCTORS
# =========================

doctors = [
    {
        "name": "Dr. Amit Sharma",
        "specialization": "Cardiologist",
        "time": "10:00 AM - 2:00 PM"
    },
    {
        "name": "Dr. Priya Patil",
        "specialization": "Gynecologist",
        "time": "11:00 AM - 3:00 PM"
    },
    {
        "name": "Dr. Rahul Deshmukh",
        "specialization": "General Physician",
        "time": "9:00 AM - 1:00 PM"
    },
    {
        "name": "Dr. Sneha Joshi",
        "specialization": "Dermatologist",
        "time": "2:00 PM - 6:00 PM"
    }
]

doctor_names = [doctor["name"] for doctor in doctors]

# =========================
# DATABASE FUNCTIONS
# =========================

def register_user(name, username, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users
            (name, username, password, role)
            VALUES (?, ?, ?, ?)
        """, (name, username, password, "User"))

        conn.commit()
        return True, "Registration successful!"

    except sqlite3.IntegrityError:
        return False, "Username already exists."

    finally:
        conn.close()


def get_user(username, password, role):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE username = ?
        AND password = ?
        AND role = ?
    """, (username, password, role))

    user = cursor.fetchone()

    conn.close()

    return user


def add_appointment(username, patient, doctor, date, reason):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO appointments
        (username, patient, doctor, date, reason, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        username,
        patient,
        doctor,
        date,
        reason,
        "Booked"
    ))

    conn.commit()
    conn.close()


def get_all_appointments():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, patient, doctor, date, reason, status
        FROM appointments
        ORDER BY id DESC
    """)

    appointments = cursor.fetchall()

    conn.close()

    return appointments


def get_user_appointments(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, patient, doctor, date, reason, status
        FROM appointments
        WHERE username = ?
        ORDER BY id DESC
    """, (username,))

    appointments = cursor.fetchall()

    conn.close()

    return appointments


def cancel_appointment(appointment_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE appointments
        SET status = ?
        WHERE id = ?
    """, ("Cancelled", appointment_id))

    conn.commit()
    conn.close()


# =========================
# SESSION STATE
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "name" not in st.session_state:
    st.session_state.name = ""

if "role" not in st.session_state:
    st.session_state.role = ""

if "page" not in st.session_state:
    st.session_state.page = "Home"


# =========================
# LOGIN / REGISTER
# =========================

if not st.session_state.logged_in:

    st.title("🏥 Hospital Appointment Management System")

    st.write("### Welcome to Hospital Appointment Management System")

    st.divider()

    login_tab, register_tab = st.tabs([
        "🔐 Login",
        "📝 Register"
    ])

    # =========================
    # LOGIN
    # =========================

    with login_tab:

        st.subheader("Login")

        role = st.selectbox(
            "Select Role",
            ["User", "Admin"]
        )

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            type="primary",
            use_container_width=True
        ):

            user = get_user(
                username,
                password,
                role
            )

            if user:

                st.session_state.logged_in = True
                st.session_state.username = user[2]
                st.session_state.name = user[1]
                st.session_state.role = user[4]
                st.session_state.page = "Home"

                st.success("Login successful!")

                st.rerun()

            else:

                st.error(
                    "Invalid username, password or role."
                )

    # =========================
    # REGISTER
    # =========================

    with register_tab:

        st.subheader("Create New Account")

        name = st.text_input(
            "Full Name",
            key="register_name"
        )

        username = st.text_input(
            "Username",
            key="register_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="register_confirm"
        )

        if st.button(
            "Register",
            type="primary",
            use_container_width=True
        ):

            if not name or not username or not password:

                st.warning(
                    "Please fill all required fields."
                )

            elif password != confirm_password:

                st.error(
                    "Passwords do not match."
                )

            else:

                success, message = register_user(
                    name,
                    username,
                    password
                )

                if success:
                    st.success(message)
                    st.info(
                        "Now go to Login and login with your account."
                    )
                else:
                    st.error(message)


# =========================
# LOGGED-IN USER
# =========================

else:

    # =========================
    # HEADER
    # =========================

    st.title("🏥 Hospital Appointment Management System")

    st.write(
        f"Welcome, **{st.session_state.name}** 👋"
    )

    st.write(
        f"Role: **{st.session_state.role}**"
    )

    st.divider()

    # =========================
    # FRONT PAGE NAVIGATION
    # =========================

    if st.session_state.role == "User":

        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            if st.button(
                "🏠 Home",
                use_container_width=True
            ):
                st.session_state.page = "Home"
                st.rerun()

        with col2:
            if st.button(
                "📅 Book",
                use_container_width=True
            ):
                st.session_state.page = "Book Appointment"
                st.rerun()

        with col3:
            if st.button(
                "📋 My Appointments",
                use_container_width=True
            ):
                st.session_state.page = "My Appointments"
                st.rerun()

        with col4:
            if st.button(
                "❌ Cancel",
                use_container_width=True
            ):
                st.session_state.page = "Cancel My Appointment"
                st.rerun()

        with col5:
            if st.button(
                "👨‍⚕️ Doctors",
                use_container_width=True
            ):
                st.session_state.page = "Doctors"
                st.rerun()

        with col6:
            if st.button(
                "🚪 Logout",
                use_container_width=True
            ):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.name = ""
                st.session_state.role = ""
                st.session_state.page = "Home"
                st.rerun()

    else:

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            if st.button(
                "🏠 Dashboard",
                use_container_width=True
            ):
                st.session_state.page = "Dashboard"
                st.rerun()

        with col2:
            if st.button(
                "📋 All Appointments",
                use_container_width=True
            ):
                st.session_state.page = "View All Appointments"
                st.rerun()

        with col3:
            if st.button(
                "❌ Cancel Appointment",
                use_container_width=True
            ):
                st.session_state.page = "Cancel Appointment"
                st.rerun()

        with col4:
            if st.button(
                "👨‍⚕️ Doctors",
                use_container_width=True
            ):
                st.session_state.page = "Doctors"
                st.rerun()

        with col5:
            if st.button(
                "🚪 Logout",
                use_container_width=True
            ):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.name = ""
                st.session_state.role = ""
                st.session_state.page = "Home"
                st.rerun()

    st.divider()

    # =========================
    # USER HOME
    # =========================

    if (
        st.session_state.role == "User"
        and st.session_state.page == "Home"
    ):

        st.header("🏠 Home")

        st.success(
            "Welcome to Hospital Appointment Management System!"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Doctors Available",
                len(doctors)
            )

        with col2:
            appointments = get_user_appointments(
                st.session_state.username
            )

            st.metric(
                "My Appointments",
                len(appointments)
            )

        with col3:
            st.metric(
                "System Status",
                "Active"
            )

        st.info(
            "Use the buttons above to book, view or cancel appointments."
        )

    # =========================
    # BOOK APPOINTMENT
    # =========================

    elif (
        st.session_state.role == "User"
        and st.session_state.page == "Book Appointment"
    ):

        st.header("📅 Book Appointment")

        patient = st.text_input(
            "Patient Name"
        )

        doctor = st.selectbox(
            "Select Doctor",
            doctor_names
        )

        date = st.date_input(
            "Appointment Date"
        )

        reason = st.text_area(
            "Reason for Appointment"
        )

        if st.button(
            "Book Appointment",
            type="primary"
        ):

            if not patient:

                st.warning(
                    "Please enter patient name."
                )

            else:

                add_appointment(
                    st.session_state.username,
                    patient,
                    doctor,
                    str(date),
                    reason
                )

                st.success(
                    "Appointment booked successfully! ✅"
                )

    # =========================
    # MY APPOINTMENTS
    # =========================

    elif (
        st.session_state.role == "User"
        and st.session_state.page == "My Appointments"
    ):

        st.header("📋 My Appointments")

        appointments = get_user_appointments(
            st.session_state.username
        )

        if appointments:

            for appointment in appointments:

                appointment_id = appointment[0]
                patient = appointment[1]
                doctor = appointment[2]
                date = appointment[3]
                reason = appointment[4]
                status = appointment[5]

                with st.container(border=True):

                    st.write(
                        f"### Appointment #{appointment_id}"
                    )

                    st.write(
                        f"**Patient:** {patient}"
                    )

                    st.write(
                        f"**Doctor:** {doctor}"
                    )

                    st.write(
                        f"**Date:** {date}"
                    )

                    st.write(
                        f"**Reason:** {reason}"
                    )

                    if status == "Booked":
                        st.success(
                            f"Status: {status}"
                        )
                    else:
                        st.error(
                            f"Status: {status}"
                        )

        else:

            st.info(
                "No appointments found."
            )

    # =========================
    # USER CANCEL
    # =========================

    elif (
        st.session_state.role == "User"
        and st.session_state.page == "Cancel My Appointment"
    ):

        st.header("❌ Cancel My Appointment")

        appointments = get_user_appointments(
            st.session_state.username
        )

        active_appointments = [
            appointment
            for appointment in appointments
            if appointment[5] == "Booked"
        ]

        if active_appointments:

            options = {
                f"#{a[0]} - {a[1]} - {a[2]} - {a[3]}":
                a[0]
                for a in active_appointments
            }

            selected = st.selectbox(
                "Select Appointment",
                list(options.keys())
            )

            if st.button(
                "Cancel Appointment",
                type="primary"
            ):

                cancel_appointment(
                    options[selected]
                )

                st.success(
                    "Appointment cancelled successfully! ✅"
                )

                st.rerun()

        else:

            st.info(
                "No active appointments available for cancellation."
            )

    # =========================
    # DOCTORS
    # =========================

    elif st.session_state.page == "Doctors":

        st.header("👨‍⚕️ Our Doctors")

        for doctor in doctors:

            with st.container(border=True):

                st.subheader(
                    doctor["name"]
                )

                st.write(
                    f"**Specialization:** {doctor['specialization']}"
                )

                st.write(
                    f"**Available Time:** {doctor['time']}"
                )

    # =========================
    # ADMIN DASHBOARD
    # =========================

    elif (
        st.session_state.role == "Admin"
        and st.session_state.page == "Dashboard"
    ):

        st.header("📊 Admin Dashboard")

        appointments = get_all_appointments()

        total = len(appointments)

        booked = len([
            a for a in appointments
            if a[6] == "Booked"
        ])

        cancelled = len([
            a for a in appointments
            if a[6] == "Cancelled"
        ])

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Appointments",
                total
            )

        with col2:
            st.metric(
                "Booked",
                booked
            )

        with col3:
            st.metric(
                "Cancelled",
                cancelled
            )

        st.success(
            "Admin Dashboard is working successfully."
        )

    # =========================
    # ADMIN VIEW ALL
    # =========================

    elif (
        st.session_state.role == "Admin"
        and st.session_state.page == "View All Appointments"
    ):

        st.header("📋 All Appointments")

        appointments = get_all_appointments()

        if appointments:

            for appointment in appointments:

                appointment_id = appointment[0]
                username = appointment[1]
                patient = appointment[2]
                doctor = appointment[3]
                date = appointment[4]
                reason = appointment[5]
                status = appointment[6]

                with st.container(border=True):

                    st.write(
                        f"### Appointment #{appointment_id}"
                    )

                    st.write(
                        f"**Username:** {username}"
                    )

                    st.write(
                        f"**Patient:** {patient}"
                    )

                    st.write(
                        f"**Doctor:** {doctor}"
                    )

                    st.write(
                        f"**Date:** {date}"
                    )

                    st.write(
                        f"**Reason:** {reason}"
                    )

                    if status == "Booked":
                        st.success(
                            f"Status: {status}"
                        )
                    else:
                        st.error(
                            f"Status: {status}"
                        )

        else:

            st.info(
                "No appointments found."
            )

    # =========================
    # ADMIN CANCEL
    # =========================

    elif (
        st.session_state.role == "Admin"
        and st.session_state.page == "Cancel Appointment"
    ):

        st.header("❌ Cancel Appointment")

        appointments = get_all_appointments()

        active_appointments = [
            appointment
            for appointment in appointments
            if appointment[6] == "Booked"
        ]

        if active_appointments:

            options = {
                f"#{a[0]} - {a[2]} - {a[3]} - {a[4]}":
                a[0]
                for a in active_appointments
            }

            selected = st.selectbox(
                "Select Appointment",
                list(options.keys())
            )

            if st.button(
                "Cancel Appointment",
                type="primary"
            ):

                cancel_appointment(
                    options[selected]
                )

                st.success(
                    "Appointment cancelled successfully! ✅"
                )

                st.rerun()

        else:

            st.info(
                "No active appointments available for cancellation."
            )


# =========================
# FOOTER
# =========================

st.divider()

st.caption(
    "Hospital Appointment Management System | "
    "Developed using Python, Streamlit and SQLite Database"
)
