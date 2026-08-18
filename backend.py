import os
import sqlite3
import smtplib
import threading
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify

PORT = 2000
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-mail@gmail.com"
SENDER_PASSWORD = "app-pw"
RECEIVER_EMAIL = SENDER_EMAIL

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend", "template")
DB_FILE = os.path.join(BASE_DIR, "events.db")

app = Flask(__name__, template_folder=TEMPLATE_DIR)

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                event_date TEXT NOT NULL,
                mail_sent INTEGER DEFAULT 0
            )
        ''')
        conn.commit()

init_db()

def send_email(title, description, event_date_str, relative_day):
    if SENDER_EMAIL == "DEINE_GMAIL_ADRESSE@gmail.com":
        print("[SMTP WARNUNG] Bitte zuerst Gmail-Daten in backend.py konfigurieren!")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = f"⏰ [{relative_day.upper()}] Termin-Erinnerung: {title}"

        body = (f"Hallo!\n\n"
                f"Erinnerung für einen Termin ({relative_day}):\n\n"
                f"📌 Titel: {title}\n"
                f"📅 Datum & Uhrzeit: {event_date_str}\n"
                f"📝 Beschreibung: {description or 'Keine'}\n\n"
                f"Viele Grüße,\nDein Raspberry Pi 5")

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[EMAIL] Erfolgreich gesendet ({relative_day}): {title}")
        return True
    except Exception as e:
        print(f"[EMAIL FEHLER] {e}")
        return False

def midnight_mail_checker():
    while True:
        now = datetime.now()
        next_midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time())
        seconds_until_midnight = (next_midnight - now).total_seconds()

        print(f"[CRON] Nächster E-Mail-Check in {int(seconds_until_midnight // 3600)}h {int((seconds_until_midnight % 3600) // 60)}m (um 00:00 Uhr)")

        time.sleep(seconds_until_midnight)

        try:
            today_date = datetime.now().date()
            tomorrow_date = today_date + timedelta(days=1)

            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM events")
                events = cursor.fetchall()

                for ev in events:
                    ev_dt = datetime.strptime(ev['event_date'], '%Y-%m-%dT%H:%M')
                    ev_date = ev_dt.date()

                    if ev_date == today_date:
                        rel_label = "Heute"
                    elif ev_date == tomorrow_date:
                        rel_label = "Morgen"
                    else:
                        rel_label = None

                    if rel_label:
                        formatted_time = ev_dt.strftime('%d.%m.%Y um %H:%M Uhr')
                        send_email(ev['title'], ev['description'], formatted_time, rel_label)

        except Exception as e:
            print(f"[MAIL CHECKER FEHLER] {e}")

        time.sleep(10)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events', methods=['GET'])
def get_events():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
        rows = cursor.fetchall()

    events = [dict(row) for row in rows]
    return jsonify(events)

@app.route('/api/events', methods=['POST'])
def add_event():
    data = request.json
    with get_db() as conn:
        conn.execute(
            "INSERT INTO events (title, description, event_date) VALUES (?, ?, ?)",
            (data['title'], data['description'], data['event_date'])
        )
        conn.commit()
    return jsonify({"status": "success"})

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.json
    with get_db() as conn:
        conn.execute(
            "UPDATE events SET title = ?, description = ?, event_date = ? WHERE id = ?",
            (data['title'], data['description'], data['event_date'], event_id)
        )
        conn.commit()
    return jsonify({"status": "updated"})

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    with get_db() as conn:
        conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
        conn.commit()
    return jsonify({"status": "deleted"})

if __name__ == '__main__':
    t = threading.Thread(target=midnight_mail_checker, daemon=True)
    t.start()

    app.run(host='0.0.0.0', port=PORT, debug=False)