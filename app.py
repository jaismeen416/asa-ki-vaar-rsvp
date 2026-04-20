from flask import Flask, render_template, request, abort
import csv
import os
from datetime import datetime
import resend

app = Flask(__name__)

# Change this to your private dashboard link part
DASHBOARD_SECRET = "OurRSVP"

# Change this to the email where YOU want RSVP alerts
NOTIFY_EMAIL = "jaismeen416@gmail.com"

# Resend API key comes from terminal or deployment environment
resend.api_key = os.environ.get("RESEND_API_KEY")

CSV_FILE = "rsvps.csv"


def ensure_csv_exists():
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "timestamp",
                "name",
                "attendance",
                "guests",
                "phone",
                "message"
            ])


def save_rsvp(data):
    ensure_csv_exists()
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            data["timestamp"],
            data["name"],
            data["attendance"],
            data["guests"],
            data["phone"],
            data["message"]
        ])


def load_rsvps():
    ensure_csv_exists()
    rows = []
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows.append(row)
    return rows


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/rsvp", methods=["POST"])
def rsvp():
    name = request.form.get("name", "").strip()
    attendance = request.form.get("attendance", "").strip()
    guests = request.form.get("guests", "").strip()
    phone = request.form.get("phone", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not attendance:
        return "Missing required fields", 400

    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "name": name,
        "attendance": attendance,
        "guests": guests if guests else "1",
        "phone": phone,
        "message": message
    }

    save_rsvp(data)

    # Optional email alert
    try:
        if resend.api_key and NOTIFY_EMAIL != "jaismeen416@gmail.com":
            resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": [NOTIFY_EMAIL],
                "subject": f"Asa Ki Vaar RSVP - {name} - {attendance}",
                "html": f"""
                    <h2>New RSVP Received</h2>
                    <p><strong>Name:</strong> {name}</p>
                    <p><strong>Attendance:</strong> {attendance}</p>
                    <p><strong>Guests:</strong> {data['guests']}</p>
                    <p><strong>Phone:</strong> {phone if phone else '-'}</p>
                    <p><strong>Message:</strong> {message if message else '-'}</p>
                    <p><strong>Submitted:</strong> {data['timestamp']}</p>
                """
            })
    except Exception as e:
        print("Email failed:", e)

    return render_template("thankyou.html", name=name, attendance=attendance)


@app.route("/dashboard/<secret>")
def dashboard(secret):
    if secret != DASHBOARD_SECRET:
        abort(404)

    rsvps = load_rsvps()

    total_rsvps = len(rsvps)
    attending = sum(1 for r in rsvps if r["attendance"] == "Yes")
    not_attending = sum(1 for r in rsvps if r["attendance"] == "No")
    maybe = sum(1 for r in rsvps if r["attendance"] == "Maybe")

    total_guests = 0
    for r in rsvps:
        value = (r.get("guests") or "").replace("+", "").strip()
        try:
            total_guests += int(value)
        except:
            pass

    return render_template(
        "dashboard.html",
        rsvps=reversed(rsvps),
        total_rsvps=total_rsvps,
        attending=attending,
        not_attending=not_attending,
        maybe=maybe,
        total_guests=total_guests,
        dashboard_secret=DASHBOARD_SECRET
    )


if __name__ == "__main__":
    ensure_csv_exists()
    app.run(debug=True)