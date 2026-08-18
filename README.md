# 📌 Raspberry Pi 5 Event & Task Manager

A simple dark-mode web app running on Raspberry Pi 5 to manage appointments and To-Dos with 1-day email reminders and red-to-green priority cards.

## ✨ Features
- **Smart UI:** Modern Apple-style dark mode with color-coded priority cards (red to green).
- **Email Reminders:** Automatic email notification sent 1 day before an appointment.
- **Auto-Cleanup:** Completed tasks are automatically deleted every day at midnight (0:00).
- **Full Control:** Easily add, edit, and delete events or To-Dos directly in the web interface.


## 🔍 Code Insights & Logic

Here is a breakdown of the core logic used in this project to ensure stability and precision.

### 🔌 1. Boot Stability (Setup)
The ESP32 can be picky with power. This setup ensures everything initializes correctly.
