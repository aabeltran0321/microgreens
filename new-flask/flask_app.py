from flask import Flask, render_template, request, g, jsonify
import sqlite3
import os
from datetime import datetime

extension = "./"
DATABASE = f'{extension}tupmicrogreens_thresholds.db'
app = Flask(__name__)

parameters = ["pH Level", "ORP", "EC", "Temperature", "Humidity"]
DEVICE_LIST = [
    "solutionA", "solutionB", "phUp", "phDown", "waterPump", "humidifier",
    "ozoneGenerator", "solenoidValve", "fan1", "fan2", "fan3", "light1", "light2", "light3"
]


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

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    name TEXT PRIMARY KEY,
                    state TEXT NOT NULL CHECK(state IN ('ON', 'OFF'))
                )
            ''')
            # Initialize with OFF state if not exists
            for device in DEVICE_LIST:
                cursor.execute("INSERT OR IGNORE INTO devices (name, state) VALUES (?, 'OFF')", (device,))
            db.commit()
def get_sensor_data(parameter):
    conn = sqlite3.connect(DATABASE)  # replace with your actual .db file
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, value FROM logs
        WHERE parameter = ?
        ORDER BY datetime(timestamp) DESC
        LIMIT 10
    """, (parameter,))
    rows = cursor.fetchall()
    conn.close()

    return [{'timestamp': ts, 'value': val} for ts, val in reversed(rows)]  # reverse for oldest to newest
def get_latest(param):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT value FROM logs
        WHERE parameter = ?
        ORDER BY datetime(timestamp) DESC
        LIMIT 1
    """, (param,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "N/A"
def update_machine_mode_tupm(new_mode):
    db = get_db()
    cursor = db.cursor()

    # Optional: ensure there's at least one row to update
    cursor.execute("INSERT INTO machine_mode (mode) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM machine_mode)", (new_mode,))

    # Update the mode with the input string
    cursor.execute("UPDATE machine_mode SET mode = ?", (new_mode,))

    db.commit()

def update_commands_tupm(command):
    db = get_db()
    cursor = db.cursor()

    # Optional: ensure there's at least one row to update
    cursor.execute("INSERT INTO commands (comms) SELECT ? WHERE NOT EXISTS (SELECT 1 FROM commands)", (command,))

    # Update the mode with the input string
    cursor.execute("UPDATE commands SET comms = ?", (command,))

    db.commit()
@app.route('/tupmicrogreens')
def tupm_dashboard():
    data = {
        'humidity': get_latest("Humidity"),
        'orp': get_latest("ORP"),
        'ph': get_latest("pH Level"),
        'temperature': get_latest("Temperature"),
        'ec': get_latest("EC")
    }
    return render_template('dashboard_tupm.html', **data)

@app.route('/tupmicrogreens/algae')
def tupm_algae_status():
    return render_template('algae_tupm.html')

@app.route('/tupmicrogreens/settings', methods = ["GET", "POST"])
def tupm_settings():
    db = get_db()
    cursor = db.cursor()
    result = {}
    if request.method == 'POST':
        update_machine_mode_tupm(request.form.get("mode"))
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
        return jsonify({"message": "Saved!"})

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
    
    cursor.execute("SELECT mode FROM machine_mode LIMIT 1")
    current_mode = cursor.fetchone()[0]
    print(current_mode)

    return render_template('settings_tupm.html', parameters=parameters, result=result, current_mode = current_mode)

@app.route('/tupmicrogreens/controls')
def tupm_controls():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT name, state FROM devices")
        states = dict(c.fetchall())
    return render_template('controls_tupm.html', device_states=states)
@app.route('/tupmicrogreens/api/controls', methods=['GET'])
def tupm_get_device_states():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT name, state FROM devices")
        states = dict(c.fetchall())
    return jsonify(states)

@app.route('/tupmicrogreens/api/machinemode', methods=['GET'])
def tupm_get_machinemode():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT mode FROM machine_mode LIMIT 1")
        current_mode = c.fetchone()[0]
    return jsonify({"machine_mode": current_mode})

@app.route('/tupmicrogreens/api/controls', methods=['POST'])
def tupm_update_device_state():
    data = request.json
    device = data.get('device')
    state = data.get('state')

    if device is None or state not in ['ON', 'OFF']:
        return jsonify({'success': False, 'message': 'Invalid input'}), 400

    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("UPDATE devices SET state = ? WHERE name = ?", (state, device))
        conn.commit()

    return jsonify({'success': True, 'device': device, 'state': state})
@app.route('/tupmicrogreens/about')
def tupm_about():
    return render_template('aboutus_tupm.html')
@app.route('/tupmicrogreens/get_data/<datatype>')
def tupm_get_data(datatype):
    data = get_sensor_data(datatype)
    return jsonify(data)

@app.route('/tupmicrogreens/toggle', methods=['POST'])
def tupm_toggle():
    data = request.json
    device = data.get('device')
    state = data.get('state')

    if device is None or state not in ['ON', 'OFF']:
        return jsonify({'success': False, 'message': 'Invalid device or state'}), 400

    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("UPDATE devices SET state = ? WHERE name = ?", (state, device))
        conn.commit()

    return jsonify({'success': True, 'device': device, 'state': state})


@app.route('/tupmicrogreens/hilo', methods=['POST'])
def get_hilo_tupmicro():
    db = get_db()
    cursor = db.cursor()
    result = {}


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

    return jsonify(result)

@app.route('/tupmicrogreens/log', methods=['POST'])
def log_sensor_data_tupm():
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host="0.0.0.0")
