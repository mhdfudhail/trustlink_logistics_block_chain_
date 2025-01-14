# blockchain.py
import datetime
import hashlib
import json
# import serial
import random

class Block:
    def __init__(self, timestamp, data, previous_hash):
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
        

    def calculate_hash(self):
        data_string = json.dumps(self.data, sort_keys=True)
        hash_string = str(self.timestamp) + data_string + self.previous_hash + str(self.nonce)
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        while self.hash[:difficulty] != '0' * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 2

    def create_genesis_block(self):
        return Block(datetime.datetime.now(), {"temp": 0, "humidity": 0}, "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        previous_block = self.get_latest_block()
        new_block = Block(datetime.datetime.now(), data, previous_block.hash)
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def get_all_data(self):
        return [{"timestamp": block.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "data": block.data,
                "hash": block.hash} for block in self.chain]

# Serial reading function
def read_dht11():
    # Initialize serial connection (adjust COM port as needed)
    # ser = serial.Serial('COM8', 9600)
    try:
        # data = ser.readline().decode('utf-8').strip()
        # temp, humidity = map(float, data.split(','))
        list1 = [1, 2, 3, 4, 5, 6, 7,8,9,10]
        # list1 = [1, 2, 3, 4, 5, 6, 7,8,9,10]
        # print(random.choice(list1))
        temp=random.choice(list1)
        humidity=random.choice(list1)
        return {"temp": temp, "humidity": temp}
    except:
        return None
    finally:
        # ser.close()
        print("collected!")