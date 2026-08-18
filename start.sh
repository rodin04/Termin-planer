#!/bin/bash

PORT=2000
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_FILE="$SCRIPT_DIR/backend.py"

PID=$(pgrep -f "python3 $BACKEND_FILE")

if [ -n "$PID" ]; then
    echo "⚠️  Das System läuft bereits mit PID: $PID"
    read -p "Möchtest du es neu starten? (y/n): " choice
    case "$choice" in
        y|Y )
            echo "🛑 Beende alten Prozess..."
            kill -9 $PID
            sleep 1
            ;;
        * )
            echo "Abbruch. Nichts verändert."
            exit 0
            ;;
    esac
fi

python3 -m pip install flask --quiet 2>/dev/null

echo "🚀 Starte Termin-App im Hintergrund auf Port $PORT..."

nohup python3 "$BACKEND_FILE" > "$SCRIPT_DIR/app.log" 2>&1 &

NEW_PID=$!
sleep 1

if ps -p $NEW_PID > /dev/null; then
    echo "✅ Erfolgreich gestartet!"
    echo "🌐 Erreichbar im Browser unter: http://$(hostname -I | awk '{print $1}'):$PORT"
    echo "📄 Logs einsehbar mit: tail -f $SCRIPT_DIR/app.log"
else
    echo "❌ Fehler beim Starten. Prüfe app.log"
fi