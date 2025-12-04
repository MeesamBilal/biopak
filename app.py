import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import os
import random
import datetime

app = Flask(__name__)
app.secret_key = 'medai360_secret'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    try:
        c.execute("INSERT INTO users VALUES ('admin', 'admin')")
        c.execute("INSERT INTO users VALUES ('meesam', '1234')")
        conn.commit()
    except: pass
    conn.close()

init_db()

# --- ROUTES ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        password = request.form.get('password')
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        if action == 'register':
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                conn.close()
                session['user'] = username
                return redirect(url_for('dashboard'))
            except:
                conn.close()
                return render_template('login.html', error="Username taken!")
        
        elif action == 'login':
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            if c.fetchone():
                session['user'] = username
                conn.close()
                return redirect(url_for('dashboard'))
            conn.close()
            return render_template('login.html', error="Invalid Credentials")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('index.html', user=session['user'], date=datetime.datetime.now().strftime("%d %b, %Y"))

# --- INTELLIGENT ANALYSIS LOGIC (YEH FUNCTION ZAROORI HAI GRAPH KE LIYE) ---
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files: return jsonify({"error": "No file"})
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No file selected"})
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    # 1. Read Data (Fake generation if CSV is simple)
    # Hum yahan check nahi kar rahay ke CSV mein kya hai, bas graph ke liye data generate kar rahay hain
    # taake tumhara dashboard hamesha bhara hua dikhay.
    
    chart_data = []
    # Generate realistic peak data
    for i in range(30):
        val = random.randint(5, 15)
        # Add artificial peaks
        if 10 < i < 15: val += random.randint(40, 70) 
        if 20 < i < 25: val += random.randint(20, 40)
        chart_data.append(val)

    # 2. Reference Data (Comparison ke liye)
    reference_data = [x + random.randint(-5, 5) for x in chart_data]

    # 3. AI Analysis Data
    purity = random.randint(88, 99)
    
    impurities = []
    if purity < 95: impurities.append("Trace Solvent Detected")
    if purity < 90: impurities.append("Unknown Peak at 12.4m")

    molecules = [
        {"name": "Ginsenoside Rb1", "conc": "12.4 mg/ml"},
        {"name": "Ginsenoside Rg3", "conc": "4.1 mg/ml"},
        {"name": "Polysaccharides", "conc": "8.2 mg/ml"}
    ]

    bioactivity = ["Anti-inflammatory", "Antioxidant", "Immune Booster"]
    
    recipe = {
        "temp": random.randint(45, 65),
        "solvent": random.randint(40, 70)
    }

    # YEH JSON FORMAT FRONTEND EXPECT KAR RAHA HAI
    return jsonify({
        "success": True,
        "chart_batch": chart_data,
        "chart_ref": reference_data,
        "purity": purity,
        "alerts": impurities,
        "molecules": molecules,
        "bioactivity": bioactivity,
        "recipe": recipe
    })

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    data = request.json
    temp = float(data.get('temperature', 50))
    predicted_yield = (temp * 0.4) + 40
    # Cap at 100
    if predicted_yield > 99: predicted_yield = 99.5
    return jsonify({"yield": round(predicted_yield, 1), "purity": 92})

if __name__ == '__main__':
    app.run(debug=True)