import streamlit as st
import json
import os
from datetime import datetime

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Hospital Appointment Management System",
    page_icon="🏥",
    layout="wide"
)

# ---------------- HIDE STREAMLIT BRANDING ----------------

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
</style>
""", unsafe_allow_html=True)

# ---------------- FILES ----------------

APPOINTMENTS_FILE = "appointments.json"
USERS_FILE = "users.json"

# ---------------- DATA FUNCTIONS ----------------

def load_appointments():
    if not os.path.exists(APPOINTMENTS_FILE):
        return []

    try:
        with open(APPOINTMENTS_FILE, "r") as file:
            return json.load(file)
    except:
        return []


def save_appointments(appointments):
    with open(APPOINTMENTS_FILE, "w") as file:
        json.dump(appointments, file, indent=4)


def load_users():
    if not os.path.exists(USERS_FILE):
        return []

    try:
        with open(USERS_FILE, "r") as file:
            return json.load(file)
    except:
        return []


def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)


# ---------------- SESSION STATE ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

if "page" not in st.session_state:
    st.session_state.page = "Home"


# ---------------- DOCTORS ----------------

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
# NOT LOGGED IN
# =========================================================

if not st.session_state.logged_in:

    st.title("🏥 Hospital Appointment Management System")

    st.write("Book and manage hospital appointments easily.")

    menu = st.radio(
        "Select Option",
        ["Login", "Register"],
        horizontal=True
    )

    # ---------------- REGISTER ----------------

    if menu == "Register":

        st.header("📝 User Registration")

        name = st.text_input("Full Name")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input(
            "Confirm Password",
            type="password"
        )

        if st.button("Register"):

            if not name or not username or not password:
                st.error("Please fill all fields.")

            elif password != confirm_password:
                st.error("Passwords do not match.")

            else:
                users = load_users()

                username_exists = any(
                    user["username"] == username
                    for user in users
                )

                if username_exists:
                    st.error("Username already exists.")

                else:
                    users.append({
                        "name": name,
                        "username": username,
                        "password": password,
                        "role": "User"
                    })

                    save_users(users)

                    st.success(
                        "Registration successful! Please login."
                    )

    # ---------------- LOGIN ----------------

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

                if username == "admin" and password == "admin123":

                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = "Admin"
                    st.session_state.page = "Dashboard"

                    st.success("Admin login successful!")
                    st.rerun()

                else:
                    st.error("Invalid admin username or password.")

            # USER LOGIN
            else:

                users = load_users()

                valid_user = None

                for user in users:
                    if (
                        user["username"] == username
                        and user["password"] == password
                    ):
                        valid_user = user
                        break

                if valid_user:

                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = "User"
                    st.session_state.page = "Home"

                    st.success("Login successful!")
                    st.rerun()

                else:
                    st.error("Invalid username or password.")


# =========================================================
# LOGGED IN
# =========================================================

else:

    # ---------------- SIDEBAR ----------------

    st.sidebar.title("🏥 Hospital System")

    st.sidebar.write(
        f"Welcome, **{st.session_state.username}**"
    )

    st.sidebar.write(
        f"Role: **{st.session_state.role}**"
    )

    st.sidebar.divider()

    # ---------------- USER MENU ----------------

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

    # ---------------- ADMIN MENU ----------------

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

    st.session_state.page = page

    # ---------------- LOGOUT ----------------

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.page = "Home"

        st.rerun()

    # =====================================================
    # USER HOME
    # =====================================================

    if page == "Home":

        st.title("🏠 Welcome to Hospital Appointment System")

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
            value=st.session_state.username
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
                st.error("Please enter patient name.")

            else:

                appointments = load_appointments()

                appointment = {
                    "username": st.session_state.username,
                    "patient": patient_name,
                    "doctor": selected_doctor,
                    "date": str(appointment_date),
                    "reason": reason,
                    "status": "Booked"
                }

                appointments.append(appointment)

                save_appointments(appointments)

                st.success(
                    "Appointment booked successfully! ✅"
                )

    # =====================================================
    # MY APPOINTMENTS
    # =====================================================

    elif page == "My Appointments":

        st.title("📋 My Appointments")

        appointments = load_appointments()

        my_appointments = [
            appointment
            for appointment in appointments
            if appointment.get("username") ==
            st.session_state.username
        ]

        if my_appointments:

            for index, appointment in enumerate(
                my_appointments,
                start=1
            ):

                st.write(f"### Appointment {index}")

                st.write(
                    f"**Patient:** {appointment.get('patient', '')}"
                )

                st.write(
                    f"**Doctor:** {appointment.get('doctor', '')}"
                )

                st.write(
                    f"**Date:** {appointment.get('date', '')}"
                )

                st.write(
                    f"**Reason:** {appointment.get('reason', '')}"
                )

                st.write(
                    f"**Status:** {appointment.get('status', 'Booked')}"
                )

                st.divider()

        else:
            st.info("No appointments found.")

    # =====================================================
    # CANCEL MY APPOINTMENT
    # =====================================================

    elif page == "Cancel My Appointment":

        st.title("❌ Cancel My Appointment")

        appointments = load_appointments()

        my_appointments = [
            appointment
            for appointment in appointments
            if appointment.get("username") ==
            st.session_state.username
            and appointment.get("status") != "Cancelled"
        ]

        if my_appointments:

            options = []

            for i, appointment in enumerate(
                my_appointments
            ):
                options.append(
                    f"{i + 1}. "
                    f"{appointment.get('doctor')} - "
                    f"{appointment.get('date')}"
                )

            selected = st.selectbox(
                "Select Appointment",
                options
            )

            selected_index = options.index(selected)

            if st.button("Cancel Appointment"):

                appointment_to_cancel = my_appointments[
                    selected_index
                ]

                for appointment in appointments:

                    if appointment is appointment_to_cancel:
                        appointment["status"] = "Cancelled"
                        break

                save_appointments(appointments)

                st.success(
                    "Appointment cancelled successfully."
                )

        else:
            st.info("No active appointments found.")

    # =====================================================
    # DOCTORS
    # =====================================================

    elif page == "Doctors":

        st.title("👨‍⚕️ Available Doctors")

        for doctor in doctors:

            st.subheader(doctor["name"])

            st.write(
                f"**Specialization:** "
                f"{doctor['specialization']}"
            )

            st.write(
                f"**Timing:** {doctor['timing']}"
            )

            st.divider()

    # =====================================================
    # ADMIN DASHBOARD
    # =====================================================

    elif page == "Dashboard":

        st.title("📊 Admin Dashboard")

        appointments = load_appointments()

        total = len(appointments)

        booked = len([
            appointment
            for appointment in appointments
            if appointment.get("status") == "Booked"
        ])

        cancelled = len([
            appointment
            for appointment in appointments
            if appointment.get("status") == "Cancelled"
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

    # =====================================================
    # ADMIN VIEW ALL APPOINTMENTS
    # =====================================================

    elif page == "View All Appointments":

        st.title("📋 All Appointments")

        appointments = load_appointments()

        if appointments:

            for index, appointment in enumerate(
                appointments,
                start=1
            ):

                st.write(
                    f"### Appointment {index}"
                )

                st.write(
                    f"**Patient:** "
                    f"{appointment.get('patient', '')}"
                )

                st.write(
                    f"**Username:** "
                    f"{appointment.get('username', 'Old Record')}"
                )

                st.write(
                    f"**Doctor:** "
                    f"{appointment.get('doctor', '')}"
                )

                st.write(
                    f"**Date:** "
                    f"{appointment.get('date', '')}"
                )

                st.write(
                    f"**Reason:** "
                    f"{appointment.get('reason', '')}"
                )

                st.write(
                    f"**Status:** "
                    f"{appointment.get('status', 'Booked')}"
                )

                st.divider()

        else:
            st.info("No appointments available.")

    # =====================================================
    # ADMIN CANCEL APPOINTMENT
    # =====================================================

    elif page == "Cancel Appointment":

        st.title("❌ Cancel Appointment")

        appointments = load_appointments()

        active_appointments = [
            appointment
            for appointment in appointments
            if appointment.get("status") != "Cancelled"
        ]

        if active_appointments:

            options = []

            for i, appointment in enumerate(
                active_appointments
            ):

                options.append(
                    f"{i + 1}. "
                    f"{appointment.get('patient')} - "
                    f"{appointment.get('doctor')} - "
                    f"{appointment.get('date')}"
                )

            selected = st.selectbox(
                "Select Appointment",
                options
            )

            selected_index = options.index(selected)

            if st.button("Cancel Selected Appointment"):

                appointment_to_cancel = active_appointments[
                    selected_index
                ]

                for appointment in appointments:

                    if appointment is appointment_to_cancel:
                        appointment["status"] = "Cancelled"
                        break

                save_appointments(appointments)

                st.success(
                    "Appointment cancelled successfully."
                )

        else:
            st.info("No active appointments found.")


# ---------------- FOOTER ----------------

st.markdown("---")

st.caption(
    "Hospital Appointment Management System | "
    "Developed using Python, Streamlit and JSON"
)
