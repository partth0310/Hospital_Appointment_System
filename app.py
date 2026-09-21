import streamlit as st
import json
import os

APPOINTMENT_FILE = "appointments.json"
USER_FILE = "users.json"


# ---------------- FILE FUNCTIONS ----------------

def load_appointments():
    if os.path.exists(APPOINTMENT_FILE):
        with open(APPOINTMENT_FILE, "r") as f:
            return json.load(f)
    return []


def save_appointments(data):
    with open(APPOINTMENT_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return []


def save_users(data):
    with open(USER_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Hospital Appointment Management System",
    page_icon="🏥"
)


# ---------------- SESSION STATE ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = ""

if "page" not in st.session_state:
    st.session_state.page = "login"


# ---------------- REGISTER PAGE ----------------

if st.session_state.page == "register" and not st.session_state.logged_in:

    st.title("🏥 Hospital Appointment Management System")
    st.header("📝 User Registration")

    new_username = st.text_input("Create Username")
    new_password = st.text_input("Create Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Create Account"):

        if new_username.strip() == "" or new_password.strip() == "":
            st.error("Please fill all fields.")

        elif new_password != confirm_password:
            st.error("Passwords do not match.")

        else:
            users = load_users()

            exists = any(
                user["username"] == new_username
                for user in users
            )

            if exists:
                st.error("Username already exists.")

            else:
                users.append({
                    "username": new_username,
                    "password": new_password
                })

                save_users(users)

                st.success("Registration successful! Please login.")

                st.session_state.page = "login"
                st.rerun()

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()


# ---------------- LOGIN PAGE ----------------

elif not st.session_state.logged_in:

    st.title("🏥 Hospital Appointment Management System")
    st.subheader("Login")

    login_type = st.radio(
        "Login As",
        ["User", "Admin"]
    )

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        # ADMIN LOGIN
        if login_type == "Admin":

            if username == "admin" and password == "admin123":

                st.session_state.logged_in = True
                st.session_state.username = "admin"
                st.session_state.role = "admin"

                st.success("Admin Login Successful!")
                st.rerun()

            else:
                st.error("Invalid Admin Username or Password.")

        # USER LOGIN
        else:

            users = load_users()

            found = False

            for user in users:

                if (
                    user["username"] == username
                    and user["password"] == password
                ):

                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = "user"

                    found = True
                    break

            if found:
                st.success("User Login Successful!")
                st.rerun()

            else:
                st.error("Invalid Username or Password.")

    st.divider()

    st.subheader("New User?")

    if st.button("Register"):
        st.session_state.page = "register"
        st.rerun()


# ---------------- MAIN APPLICATION ----------------

else:

    st.title("🏥 Hospital Appointment Management System")

    st.write(
        f"Welcome, **{st.session_state.username}**!"
    )

    st.sidebar.header("Hospital Menu")

    # ==================================================
    # ADMIN
    # ==================================================

    if st.session_state.role == "admin":

        menu = st.sidebar.radio(
            "Select Option",
            [
                "Dashboard",
                "View All Appointments",
                "Cancel Appointment",
                "Doctors"
            ]
        )

        if menu == "Dashboard":

            st.header("👨‍💼 Admin Dashboard")

            appointments = load_appointments()

            st.info(
                f"Total Appointments: {len(appointments)}"
            )

        elif menu == "View All Appointments":

            st.header("📋 All Appointments")

            appointments = load_appointments()

            if appointments:
                st.table(appointments)
            else:
                st.warning("No appointments available.")

        elif menu == "Cancel Appointment":

            st.header("❌ Cancel Appointment")

            appointments = load_appointments()

            if not appointments:

                st.warning("No appointments available.")

            else:

                options = [
                    f"{i+1}. {a['patient']} - "
                    f"{a['doctor']} - {a['date']}"
                    for i, a in enumerate(appointments)
                ]

                selected = st.selectbox(
                    "Select Appointment",
                    options
                )

                if st.button("Cancel Appointment"):

                    index = options.index(selected)

                    deleted = appointments.pop(index)

                    save_appointments(appointments)

                    st.success(
                        f"Appointment for "
                        f"{deleted['patient']} "
                        f"cancelled successfully."
                    )

        elif menu == "Doctors":

            st.header("👨‍⚕️ Our Doctors")

            st.write("**Dr. Patil** — General Physician")
            st.write("**Dr. Sharma** — Cardiologist")
            st.write("**Dr. Joshi** — Dermatologist")
            st.write("**Dr. Deshmukh** — Orthopedic Specialist")

    # ==================================================
    # USER
    # ==================================================

    else:

        menu = st.sidebar.radio(
            "Select Option",
            [
                "Home",
                "Book Appointment",
                "My Appointments",
                "Cancel My Appointment",
                "Doctors"
            ]
        )

        if menu == "Home":

            st.header("Welcome to Our Hospital")

            st.info(
                "Manage your hospital appointments easily."
            )

        elif menu == "Book Appointment":

            st.header("📅 Book Appointment")

            patient = st.text_input("Patient Name")

            doctor = st.selectbox(
                "Select Doctor",
                [
                    "Dr. Patil",
                    "Dr. Sharma",
                    "Dr. Joshi",
                    "Dr. Deshmukh"
                ]
            )

            date = st.date_input("Appointment Date")

            if st.button("Book Appointment"):

                if patient.strip() == "":

                    st.error("Please enter patient name.")

                else:

                    appointments = load_appointments()

                    appointments.append({
                        "username": st.session_state.username,
                        "patient": patient,
                        "doctor": doctor,
                        "date": str(date)
                    })

                    save_appointments(appointments)

                    st.success(
                        "✅ Appointment booked successfully!"
                    )

        elif menu == "My Appointments":

            st.header("📋 My Appointments")

            appointments = load_appointments()

            my_appointments = [
                a for a in appointments
                if a.get("username")
                == st.session_state.username
            ]

            if my_appointments:
                st.table(my_appointments)
            else:
                st.warning("You have no appointments.")

        elif menu == "Cancel My Appointment":

            st.header("❌ Cancel My Appointment")

            appointments = load_appointments()

            my_appointments = [
                a for a in appointments
                if a.get("username")
                == st.session_state.username
            ]

            if not my_appointments:

                st.warning(
                    "You have no appointments to cancel."
                )

            else:

                options = [
                    f"{i+1}. {a['patient']} - "
                    f"{a['doctor']} - {a['date']}"
                    for i, a in enumerate(my_appointments)
                ]

                selected = st.selectbox(
                    "Select Appointment",
                    options
                )

                if st.button("Cancel Appointment"):

                    selected_index = options.index(selected)

                    appointment_to_delete = (
                        my_appointments[selected_index]
                    )

                    appointments.remove(
                        appointment_to_delete
                    )

                    save_appointments(appointments)

                    st.success(
                        "Appointment cancelled successfully."
                    )

        elif menu == "Doctors":

            st.header("👨‍⚕️ Our Doctors")

            st.write("**Dr. Patil** — General Physician")
            st.write("**Dr. Sharma** — Cardiologist")
            st.write("**Dr. Joshi** — Dermatologist")
            st.write("**Dr. Deshmukh** — Orthopedic Specialist")

    # ---------------- LOGOUT ----------------

    st.sidebar.divider()

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.session_state.page = "login"

        st.rerun()


st.caption("© 2026 Hospital Appointment Management System")
