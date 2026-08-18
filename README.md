# 📌 Raspberry Pi 5 Event & Task Manager

A simple dark-mode web app running on Raspberry Pi 5 to manage appointments and To-Dos with 1-day email reminders and red-to-green priority cards.

<p align="center">
  <img src="termin-manager-1.png" alt="Termin Manager Preview" width="600" style="max-width: 100%; height: auto; border-radius: 12px;">
</p>

## ✨ Features
- **Smart UI:** Modern Apple-style dark mode with color-coded priority cards (red to green).
- **Email Reminders:** Automatic email notification sent 1 day before an appointment.
- **Auto-Cleanup:** Completed tasks are automatically deleted every day at midnight (0:00).
- **Full Control:** Easily add, edit, and delete events or To-Dos directly in the web interface.

## 📁 File Structure

- **backend.py** — Flask backend & background tasks
- **start.sh** — Management script (Start/Restart/Kill)
- **events.db / todos.db** — SQLite database (auto-created)
- **app.log** — Background execution log file
- **termin-manager-1.png** — Preview screenshot
- **frontend/template/index.html** — Apple-style Dark Mode Web UI

## 💾 Database & Storage

Instead of raw text files or heavy external database servers, the application uses **SQLite3** (`events.db` / `todos.db`). 

- **Zero-Configuration:** SQLite stores everything inside a single local database file directly in the project directory.
- **Reliability:** Prevents data corruption compared to plain `.txt` files when reading and writing simultaneously.
- **Auto-Initialization:** The database tables are automatically created on the first run of `backend.py`.

## 🔍 Code Insights & Logic

### 🌐 Network & Remote Access via Tailscale
The backend server runs directly on the **Raspberry Pi 5** within a private **Tailscale VPN network**. This architecture allows secure access to the web interface from anywhere without exposing ports to the public internet:

1. **Host System:** The Raspberry Pi 5 hosts the Flask server and SQLite database locally.
2. **Secure Requests:** Any connected client device (e.g., your smartphone) sends HTTP requests through the encrypted Tailscale mesh network.
3. **Background Services:**
   - **Threaded Mail Dispatcher:** Checks upcoming events every minute and triggers SMTP email alerts 24 hours prior.
   - **Midnight Auto-Cleanup:** Automatically purges completed tasks every day at 0:00 midnight.
   - **Nohup Execution:** Managed via `start.sh`, ensuring the backend runs persistently even after closing SSH sessions.
  

## 📸 Code Highlights & Core Components

<p align="center">
  <img src="code-preview-1.png" alt="Backend Threading & Scripting Preview" width="700" style="max-width: 100%; height: auto; border-radius: 10px; border: 1px solid #333;">
</p>

### ⚡ Key Implementations Explained:

* **Multithreaded Background Scheduler (`backend.py`):**
  The email dispatcher runs on an independent Python daemon thread (`threading.Thread(..., daemon=True)`). This ensures that heavy tasks like SMTP socket connections and database polling never block or slow down incoming HTTP API requests from the frontend UI.

* **Process Management & Auto-Healing (`start.sh`):**
  The Shell script dynamically detects active running instances using `pgrep`. If an instance is found, it safely prompts for a restart and terminates the old process ID before launching `nohup`. It captures process execution logs directly into `app.log` and verifies process startup via PID tracking (`$!`).


## 📸 Code Highlights & Core Components

### 1. Multithreaded Background Execution (`backend.py`)
<p align="center">
  <img src="code-preview-1.png" alt="Threading Setup" width="650" style="max-width: 100%; height: auto; border-radius: 10px; border: 1px solid #333;">
</p>

* **Asynchronous Execution:** Launches the email scheduler on an independent Python background thread (`daemon=True`). This guarantees that heavy background operations never block incoming HTTP requests or slow down the web interface UI.

---

### 2. Midnight Timer & Cron Logic (`backend.py`)
<p align="center">
  <img src="code-preview-2.png" alt="Midnight Calculation" width="650" style="max-width: 100%; height: auto; border-radius: 10px; border: 1px solid #333;">
</p>

* **Smart Sleep Calculation:** Instead of querying the database constantly every second, the script dynamically calculates the exact remaining seconds until 0:00 AM (`seconds_until_midnight`) and puts the thread to sleep until the next day triggers.

---

### 3. Persistent Process Launch (`start.sh`)
<p align="center">
  <img src="code-preview-3.png" alt="Nohup Launch" width="650" style="max-width: 100%; height: auto; border-radius: 10px; border: 1px solid #333;">
</p>

* **Persistent Background Hosting:** Executes the Flask application using `nohup` combined with `&`. This keeps the application running continuously on the Raspberry Pi 5 even after closing SSH terminal connections, while redirecting all system logs to `app.log`.
