from flask import Flask, render_template, request, g, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DATABASE = 'thresholds.db'

parameters = ["pH Level", "ORP", "EC", "Temperature", "Humidity"]

# --- DB helpers ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db:
        db.close()

def init_db():
    if not os.path.exists(DATABASE):
        with app.app_context():
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
                CREATE TABLE thresholds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parameter TEXT,
                    low REAL,
                    high REAL,
                    timestamp TEXT
                )
            ''')
            # Logs table
            cursor.execute('''
                CREATE TABLE logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parameter TEXT,
                    value REAL,
                    timestamp TEXT
                )
            ''')

            db.commit()

# --- Routes ---
@app.route('/tupmicrogreens', methods=['GET', 'POST'])
def set_thresholds():
    db = get_db()
    cursor = db.cursor()
    result = {}

    if request.method == 'POST':
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for param in parameters:
            key = param.lower().replace(" ", "_")
            low = request.form.get(f"{key}_low")
            high = request.form.get(f"{key}_high")

            cursor.execute('''
                INSERT INTO thresholds (parameter, low, high, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (param, low, high, timestamp))
        db.commit()

    # Fetch the latest thresholds for each parameter
    for param in parameters:
        cursor.execute('''
            SELECT low, high FROM thresholds
            WHERE parameter = ?
            ORDER BY id DESC LIMIT 1
        ''', (param,))
        row = cursor.fetchone()
        result[param] = {
            'low': row[0] if row else '',
            'high': row[1] if row else ''
        }

    return render_template('tupmu_index.html', parameters=parameters, result=result)

@app.route('/tupmicrogreens/log', methods=['POST'])
def log_sensor_data():
    data = request.get_json()
    parameter = data.get('parameter')
    value = data.get('value')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO logs (parameter, value, timestamp)
        VALUES (?, ?, ?)
    ''', (parameter, value, timestamp))
    db.commit()

    return jsonify({"message": "Logged successfully"}), 200


@app.route('/tupmicrogreens/logs/<parameter>')
def get_logs(parameter):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT timestamp, value FROM logs
        WHERE parameter = ?
        ORDER BY timestamp ASC
    ''', (parameter,))
    rows = cursor.fetchall()
    data = [{'timestamp': r[0], 'value': r[1]} for r in rows]
    return jsonify(data)

    
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
