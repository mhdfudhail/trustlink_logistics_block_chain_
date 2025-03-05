from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from blockchain_utils import Blockchain
import threading
import time
from functools import wraps
import os
import random
import serial

app = Flask(__name__)
app.secret_key = os.urandom(24)

ser = serial.Serial(
    port='COM10',  
    baudrate=9600,        
    timeout=1             
    )

USERS = {
    'a': '123'
}

blockchain = Blockchain('ledger.json')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function 

def generate_mock_sensor_data():
    return {
        "temp": random.uniform(15, 35),            
        "humidity": random.uniform(30, 80),        
        "air_quality": random.uniform(50, 300),    
        "vibration": random.uniform(0, 70),        
        "latitude": random.uniform(35.0, 35.1),    
        "longitude": random.uniform(139.7, 139.8)  
    }
def read_arduino_data():
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        
        values = line.split(',')
        
        if len(values):  
            parsed_values = [float(value) for value in values]
            # print(parsed_values)
            return {
                "temp": parsed_values[0],            
                "humidity": parsed_values[1],        
                "air_quality": parsed_values[2],    
                "vibration": parsed_values[3],        
                "latitude": parsed_values[4],    
                "longitude": parsed_values[5] 
            }
    

def read_sensor_data():
   
    try:
        return read_arduino_data()
        # return generate_mock_sensor_data()
    except Exception as e:
        print(f"Error reading sensors: {str(e)}")
        return None

def background_data_collection():
    while True:     
        sensor_data = read_sensor_data()
        if sensor_data:
            blockchain.add_block(sensor_data)
            latest_data = blockchain.get_all_data()[-1]
            print(f"New block added: {latest_data}")
        time.sleep(10)  # Collect data every 10 seconds

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in USERS and USERS[username] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        
        return 'Invalid credentials'
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/get_data')
@login_required
def get_data():
    data = blockchain.get_all_data()
    return jsonify(data)

@app.route('/get_latest')
@login_required
def get_latest():
    """Returns only the latest sensor readings"""
    data = blockchain.get_all_data()
    return jsonify(data[-1] if data else {})

@app.route('/get_alerts')
@login_required
def get_alerts():
    return jsonify(blockchain.get_alerts())

if __name__ == '__main__':
    try:
        data_thread = threading.Thread(target=background_data_collection, daemon=True)
        data_thread.start()
        app.run(debug=True)
    except Exception as e:
        print(f"Error starting application: {e}")
