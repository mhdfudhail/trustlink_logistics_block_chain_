# app.py
from flask import Flask, render_template, jsonify
from App_1.blockchain import Blockchain, read_dht11
import threading
import time

app = Flask(__name__)
blockchain = Blockchain()

def background_data_collection():
    while True:
        sensor_data = read_dht11()
        if sensor_data:
            blockchain.add_block(sensor_data)
        time.sleep(60)  # Collect data every minute

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data')
def get_data():
    return jsonify(blockchain.get_all_data())

if __name__ == '__main__':
    # Start background data collection in a separate thread
    data_thread = threading.Thread(target=background_data_collection, daemon=True)
    data_thread.start()
    app.run(debug=True)