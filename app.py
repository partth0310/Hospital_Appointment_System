import streamlit as st
import sqlite3

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Hospital Appointment Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# HIDE STREAMLIT UI
# =========================================================

st.markdown("""
<style>
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

[data-testid="stToolbar"] {
    visibility: hidden;
}

[data-testid="stStatusWidget"] {
    visibility: hidden;
}

[data-testid="stDecoration"] {
    visibility: hidden;
}

.stDeployButton {
    display: none;
}

.viewerBadge_container__1QSob {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE
# =========================================================

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

    conn.commit()
    conn.close()


create_tables()

# =========================================================
# DOCTORS
# =========================================================

doctors = [
    {
        "name": "Dr. Amit Sharma",
        "specialization": "Cardiologist",
        "timing": "10:00 AM - 2:00 PM"
    },
    {
        "name": "Dr. Priya Patil",
        "specialization": "Gynecologist",
        "timing": "11:00 AM - 3:00 PM"
    },
    {
        "name": "Dr. Rahul Deshmukh",
        "specialization": "General Physician",
        "timing": "9:00 AM - 1:00 PM"
    },
    {
        "name": "Dr. Sneha Joshi",
        "specialization": "Dermatologist",
        "timing": "2:00 PM - 6:00 PM"
    }
]

# =========================================================
# DATABASE FUNCTIONS
# =========================================================

def register_user(name, username, password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (name, username, password, role)
            VALUES (?, ?, ?, ?)
        """, (name, username, password, "User"))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def get_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, username, role
        FROM users
        WHERE username = ? AND password = ?
    """, (username, password))

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
        SELECT id, username, patient, doctor, date, reason, status
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
        SET status = 'Cancelled'
        WHERE id = ?
    """, (appointment_id,))

    conn.commit()
    conn.close()


# =========================================================
# SESSION STATE
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

if "name" not in st.session_state:
    st.session_state.name = ""

# =========================================================
# LOGIN / REGISTER
# =========================================================

if not st.session_state.logged_in:

    st.title("🏥 Hospital Appointment Management System")

    st.write(
        "Book and manage hospital appointments easily."
    )

    menu = st.radio(
        "Select Option",
        ["Login", "Register"],
        horizontal=True
    )

    # -----------------------------------------------------
    # REGISTER
    # -----------------------------------------------------

    if menu == "Register":

        st.header("📝 User Registration")

        name = st.text_input("Full Name")
        username = st.text_input("Username")
        password = st.text_input(
            "Password",
            type="password"
        )
        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        if st.button("Register"):

            if not name or not username or not password:
                st.error("Please fill all fields.")

            elif password != confirm_password:
                st.error("Passwords do not match.")

            elif register_user(
                name,
                username,
                password
            ):
                st.success(
                    "Registration successful! Please login."
                )

            else:
                st.error("Username already exists.")

    # -----------------------------------------------------
    # LOGIN
    # -----------------------------------------------------

    else:

        st.header("🔐 Login")

        login_type = st.radio(
            "Login As",
            ["User", "Admin"],
            horizontal=True
        )

        username = st.text_input("Username")

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            # ADMIN LOGIN
            if login_type == "Admin":

                if (
                    username == "admin"
                    and password == "admin123"
                ):

                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.name = "Administrator"
                    st.session_state.role = "Admin"

                    st.success(
                        "Admin login successful!"
                    )

                    st.rerun()

                else:
                    st.error(
                        "Invalid admin username or password."
                    )

            # USER LOGIN
            else:

                user = get_user(
                    username,
                    password
                )

                if user:

                    st.session_state.logged_in = True
                    st.session_state.name = user[0]
                    st.session_state.username = user[1]
                    st.session_state.role = user[2]

                    st.success(
                        "Login successful!"
                    )

                    st.rerun()

                else:
                    st.error(
                        "Invalid username or password."
                    )

# =========================================================
# LOGGED IN
# =========================================================

else:

    # =====================================================
    # SIDEBAR
    # =====================================================

    st.sidebar.title("🏥 Hospital System")

    st.sidebar.write(
        f"Welcome, **{st.session_state.name}**"
    )

    st.sidebar.write(
        f"Role: **{st.session_state.role}**"
    )

    st.sidebar.divider()

    # USER MENU
    if st.session_state.role == "User":

        page = st.sidebar.radio(
            "Menu",
            [
                "Home",
                "Book Appointment",
                "My Appointments",
                "Cancel My Appointment",
                "Doctors"
            ]
        )

    # ADMIN MENU
    else:

        page = st.sidebar.radio(
            "Menu",
            [
                "Dashboard",
                "View All Appointments",
                "Cancel Appointment",
                "Doctors"
            ]
        )

    # LOGOUT
    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.name = ""
        st.session_state.role = ""

        st.rerun()

    # =====================================================
    # USER HOME
    # =====================================================

    if page == "Home":

        st.title(
            "🏠 Welcome to Hospital Appointment System"
        )

        st.write(
            "Manage your hospital appointments easily."
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.info("📅 Book Appointment")

        with col2:
            st.info("👨‍⚕️ View Doctors")

        with col3:
            st.info("📋 Manage Appointments")

    # =====================================================
    # BOOK APPOINTMENT
    # =====================================================

    elif page == "Book Appointment":

        st.title("📅 Book Appointment")

        patient_name = st.text_input(
            "Patient Name",
            value=st.session_state.name
        )

        doctor_names = [
            doctor["name"]
            for doctor in doctors
        ]

        selected_doctor = st.selectbox(
            "Select Doctor",
            doctor_names
        )

        appointment_date = st.date_input(
            "Appointment Date"
        )

        reason = st.text_area(
            "Reason for Appointment"
        )

        if st.button("Book Appointment"):

            if not patient_name:
                st.error(
                    "Please enter patient name."
                )

            else:

                add_appointment(
                    st.session_state.username,
                    patient_name,
                    selected_doctor,
                    str(appointment_date),
                    reason
                )

                st.success(
                    "Appointment booked successfully! ✅"
                )

    # =====================================================
    # MY APPOINTMENTS
    # =====================================================

    elif page == "My Appointments":

        st.title("📋 My Appointments")

        appointments = get_user_appointments(
            st.session_state.username
        )

        if appointments:

            for index, appointment in enumerate(
                appointments,
                start=1
            ):

                (
                    appointment_id,
                    username,
                    patient,
                    doctor,
                    date,
                    reason,
                    status
                ) = appointment

                st.write(
                    f"### Appointment {index}"
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

                st.write(
                    f"**Status:** {status}"
                )

                st.divider()

        else:

            st.info(
                "No appointments found."
            )

    # =====================================================
    # USER CANCEL
    # =====================================================

    elif page == "Cancel My Appointment":

        st.title("❌ Cancel My Appointment")

        appointments = get_user_appointments(
            st.session_state.username
        )

        active_appointments = [
            appointment
            for appointment in appointments
            if appointment[6] != "Cancelled"
        ]

        if active_appointments:

            options = []

            for appointment in active_appointments:

                options.append(
                    f"{appointment[2]} - "
                    f"{appointment[3]} - "
                    f"{appointment[4]}"
                )

            selected = st.selectbox(
                "Select Appointment",
                options
            )

            selected_index = options.index(
                selected
            )

            selected_appointment = (
                active_appointments[selected_index]
            )

            if st.button("Cancel Appointment"):

                cancel_appointment(
                    selected_appointment[0]
                )

                st.success(
                    "Appointment cancelled successfully."
                )

                st.rerun()

        else:

            st.info(
                "No active appointments found."
            )

    # =====================================================
    # DOCTORS
    # =====================================================

    elif page == "Doctors":

        st.title("👨‍⚕️ Available Doctors")

        for doctor in doctors:

            st.subheader(
                doctor["name"]
            )

            st.write(
                f"**Specialization:** "
                f"{doctor['specialization']}"
            )

            st.write(
                f"**Timing:** "
                f"{doctor['timing']}"
            )

            st.divider()

    # =====================================================
    # ADMIN DASHBOARD
    # =====================================================

    elif page == "Dashboard":

        st.title("📊 Admin Dashboard")

        appointments = get_all_appointments()

        total = len(appointments)

        booked = len([
            appointment
            for appointment in appointments
            if appointment[6] == "Booked"
        ])

        cancelled = len([
            appointment
            for appointment in appointments
            if appointment[6] == "Cancelled"
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

        st.divider()

        st.subheader(
            "📋 Appointment Details"
        )

        if appointments:

            for appointment in appointments:

                (
                    appointment_id,
                    username,
                    patient,
                    doctor,
                    date,
                    reason,
                    status
                ) = appointment

                st.write(
                    f"### Appointment ID: {appointment_id}"
                )

                st.write(
                    f"**Patient:** {patient}"
                )

                st.write(
                    f"**Username:** {username}"
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

                st.write(
                    f"**Status:** {status}"
                )

                if status != "Cancelled":

                    if st.button(
                        "❌ Cancel This Appointment",
                        key=f"dashboard_{appointment_id}"
                    ):

                        cancel_appointment(
                            appointment_id
                        )

                        st.success(
                            "Appointment cancelled successfully."
                        )

                        st.rerun()

                else:

                    st.info(
                        "This appointment is already cancelled."
                    )

                st.divider()

        else:

            st.info(
                "No appointments available."
            )

    # =====================================================
    # ADMIN VIEW ALL
    # =====================================================

    elif page == "View All Appointments":

        st.title("📋 All Appointments")

        appointments = get_all_appointments()

        if appointments:

            for appointment in appointments:

                (
                    appointment_id,
                    username,
                    patient,
                    doctor,
                    date,
                    reason,
                    status
                ) = appointment

                st.write(
                    f"### Appointment ID: {appointment_id}"
                )

                st.write(
                    f"**Patient:** {patient}"
                )

                st.write(
                    f"**Username:** {username}"
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

                st.write(
                    f"**Status:** {status}"
                )

                st.divider()

        else:

            st.info(
                "No appointments available."
            )

    # =====================================================
    # ADMIN CANCEL
    # =====================================================

    elif page == "Cancel Appointment":

        st.title("❌ Cancel Appointment")

        appointments = get_all_appointments()

        active_appointments = [
            appointment
            for appointment in appointments
            if appointment[6] != "Cancelled"
        ]

        if active_appointments:

            options = []

            for appointment in active_appointments:

                options.append(
                    f"{appointment[2]} - "
                    f"{appointment[3]} - "
                    f"{appointment[4]}"
                )

            selected = st.selectbox(
                "Select Appointment",
                options
            )

            selected_index = options.index(
                selected
            )

            selected_appointment = (
                active_appointments[selected_index]
            )

            if st.button(
                "Cancel Selected Appointment"
            ):

                cancel_appointment(
                    selected_appointment[0]
                )

                st.success(
                    "Appointment cancelled successfully."
                )

                st.rerun()

        else:

            st.info(
                "No active appointments found."
            )

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "Hospital Appointment Management System | "
    "Developed using Python, Streamlit and SQLite Database"
)