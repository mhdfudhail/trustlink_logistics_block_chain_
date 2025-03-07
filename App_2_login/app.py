# app.py
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from blockchain import Blockchain
import threading
import time
import serial
from functools import wraps
import os
import random

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key
blockchain = Blockchain()

# User credentials (in a real app, use a database and hash the passwords)
USERS = {
    'admin': '123'  # Change this to your desired username/password
}

# Global serial connection
# ser = serial.Serial('COM3', 9600, timeout=1)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def read_dht11():
    try:
        # if ser.in_waiting:
        #     data = ser.readline().decode('utf-8').strip()
        #     temp, humidity = map(float, data.split(','))
        list1 = [1, 2, 3, 4, 5, 6, 7,8,9,10]
        temp=random.choice(list1)
        humidity=random.choice(list1)
        return {"temp": temp, "humidity": humidity}
    
    except Exception as e:
        print(f"Error reading sensor: {str(e)}")
        return None

def background_data_collection():
    while True:
        sensor_data = read_dht11()
        if sensor_data:
            blockchain.add_block(sensor_data)
            print(f"New data added: Temp={sensor_data['temp']}°C, Humidity={sensor_data['humidity']}%")
        time.sleep(1)

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
    return jsonify(blockchain.get_all_data())

if __name__ == '__main__':
    try:
        data_thread = threading.Thread(target=background_data_collection, daemon=True)
        data_thread.start()
        app.run(debug=True)
    finally:
        ser.close()