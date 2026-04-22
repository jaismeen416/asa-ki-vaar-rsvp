from flask import Flask, render_template, request
from supabase import create_client
import os

app = Flask(__name__)

# 🔴 PASTE YOUR VALUES HERE
SUPABASE_URL = "PASTE_URL_HERE"
SUPABASE_KEY = "PASTE_KEY_HERE"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/rsvp", methods=["POST"])
def rsvp():
    data = {
        "name": request.form.get("name"),
        "attendance": request.form.get("attendance"),
        "phone": request.form.get("phone"),
        "guests": request.form.get("guests"),
        "message": request.form.get("message"),
    }

    supabase.table("rsvps").insert(data).execute()

    return render_template("thankyou.html", name=data["name"])