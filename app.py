import streamlit as st
import json
import os

FILE = "appointments.json"

def load_appointments():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return []

def save_appointments(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

st.set_page_config(
    page_title="Hospital Appointment Management System",
    page_icon="🏥"
)

st.title("🏥 Hospital Appointment Management System")
st.write("Welcome to our Hospital Appointment Portal")

st.sidebar.header("Hospital Menu")

menu = st.sidebar.radio(
    "Select Option",
    ["Home", "Book Appointment", "View Appointments",
     "Cancel Appointment", "Doctors"]
)

if menu == "Home":
    st.header("Welcome to Our Hospital")
    st.info("Manage your hospital appointments easily.")

elif menu == "Book Appointment":
    st.header("📅 Book Appointment")

    patient = st.text_input("Patient Name")

    doctor = st.selectbox(
        "Select Doctor",
        ["Dr. Patil", "Dr. Sharma", "Dr. Joshi", "Dr. Deshmukh"]
    )

    date = st.date_input("Appointment Date")

    if st.button("Book Appointment"):
        if patient.strip() == "":
            st.error("Please enter patient name.")
        else:
            appointments = load_appointments()

            appointments.append({
                "patient": patient,
                "doctor": doctor,
                "date": str(date)
            })

            save_appointments(appointments)

            st.success("✅ Appointment booked successfully!")

elif menu == "View Appointments":
    st.header("📋 Appointments")

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
            f"{i+1}. {a['patient']} - {a['doctor']} - {a['date']}"
            for i, a in enumerate(appointments)
        ]

        selected = st.selectbox("Select Appointment", options)

        if st.button("Cancel Appointment"):
            index = options.index(selected)
            deleted = appointments.pop(index)
            save_appointments(appointments)

            st.success(
                f"Appointment for {deleted['patient']} cancelled successfully."
            )

elif menu == "Doctors":
    st.header("👨‍⚕️ Our Doctors")

    st.write("**Dr. Patil** — General Physician")
    st.write("**Dr. Sharma** — Cardiologist")
    st.write("**Dr. Joshi** — Dermatologist")
    st.write("**Dr. Deshmukh** — Orthopedic Specialist")

st.caption("© 2026 Hospital Appointment Management System")