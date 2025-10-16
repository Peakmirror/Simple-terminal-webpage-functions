from email.mime.text import MIMEText
from db import get_conn
from services import list_services
import datetime
import calendar
import smtplib

def calendar_appointment(username):
    conn = get_conn()
    cursor = conn.cursor()

    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    month_days = calendar.monthcalendar(year, month)
    available_dates = [day for week in month_days for day in week if day != 0]
    print(f"Available dates in {month}/{year}: {available_dates}")

    service_id = list_services()
    day = int(input("Choose a date: "))
    hour = int(input("Choose an hour (10-18): "))
    email = input("Enter your email: ")
    phone_number = input("Enter your phone number: ")
    cursor.execute("UPDATE users SET email = ?, phone_number = ? WHERE username = ?", (email, phone_number, username))
    if day not in available_dates or hour < 10 or hour > 18:
        print("No bookings available.")
        conn.close()
        return
    else:
        sender = "henritapsi@gmail.com"
        password = "cgbr wbqs mqvk pdda"
        msg = MIMEText(f"Your appointment is booked for {day}/{month}/{year} at {hour}:00.")
        msg["Subject"] = "Appointment Confirmation"
        msg["From"] = sender
        msg["To"] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)
    appointment_time = datetime.datetime(year, month, day, hour).isoformat()

    cursor.execute(
        "INSERT INTO appointments (username, appointment_time, service_id) VALUES (?, ?, ?)",
        (username, appointment_time, service_id)
    )
    conn.commit()
    conn.close()
    print(f"Appointment booked for {appointment_time}.")
