# blockchain_ledger.py
import json
import hashlib
import datetime
import os
from typing import Dict, Any

class SmartContract:
    def __init__(self):
        # Define acceptable ranges for temperature and humidity
        self.temp_range = (0, 50)  # 0°C to 50°C
        self.humidity_range = (0, 100)  # 0% to 100%
        
    def validate_data(self, data: Dict[str, float]) -> bool:
        """Validates if the sensor data is within acceptable ranges"""
        temp = data.get('temp')
        humidity = data.get('humidity')
        
        if temp is None or humidity is None:
            return False
            
        return (self.temp_range[0] <= temp <= self.temp_range[1] and
                self.humidity_range[0] <= humidity <= self.humidity_range[1])
    
    def execute(self, data: Dict[str, float]) -> Dict[str, Any]:
        """Executes smart contract logic on the data"""
        if not self.validate_data(data):
            raise ValueError("Data validation failed")
            
        # Add metadata and analysis
        result = {
            'data': data,
            'timestamp': datetime.datetime.now().isoformat(),
            'status': self.get_status(data),
            'alerts': self.check_alerts(data)
        }
        return result
    
    def get_status(self, data: Dict[str, float]) -> str:
        """Determines the environmental status based on the data"""
        temp = data['temp']
        humidity = data['humidity']
        
        if temp > 30 and humidity > 70:
            return "WARNING: High temperature and humidity"
        elif temp < 10:
            return "WARNING: Low temperature"
        elif humidity > 80:
            return "WARNING: High humidity"
        return "Normal conditions"
    
    def check_alerts(self, data: Dict[str, float]) -> list:
        """Generates alerts based on the data"""
        alerts = []
        if data['temp'] > 35:
            alerts.append("Critical temperature level")
        if data['humidity'] > 90:
            alerts.append("Critical humidity level")
        return alerts

class Block:
    def __init__(self, timestamp, data, previous_hash):
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        data_string = json.dumps(self.data, sort_keys=True)
        hash_string = (str(self.timestamp) + 
                      data_string + 
                      self.previous_hash + 
                      str(self.nonce))
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def mine_block(self, difficulty: int):
        while self.hash[:difficulty] != '0' * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    def __init__(self, ledger_file: str = 'blockchain_ledger.json'):
        self.chain = []
        self.difficulty = 2
        self.smart_contract = SmartContract()
        self.ledger_file = ledger_file
        self.load_chain()
        
        if not self.chain:
            self.chain = [self.create_genesis_block()]
            self.save_chain()

    def create_genesis_block(self) -> Block:
        genesis_data = self.smart_contract.execute({
            'temp': 20.0,
            'humidity': 50.0
        })
        return Block(datetime.datetime.now(), genesis_data, "0")

    def load_chain(self):
        """Loads blockchain from the ledger file"""
        if os.path.exists(self.ledger_file):
            try:
                with open(self.ledger_file, 'r') as file:
                    chain_data = json.load(file)
                    self.chain = [
                        Block(
                            datetime.datetime.fromisoformat(block['timestamp']),
                            block['data'],
                            block['previous_hash']
                        ) for block in chain_data
                    ]
                    # Recalculate hashes to ensure integrity
                    for block in self.chain:
                        block.hash = block.calculate_hash()
            except Exception as e:
                print(f"Error loading blockchain: {e}")
                self.chain = []

    def save_chain(self):
        """Saves blockchain to the ledger file"""
        chain_data = [
            {
                'timestamp': block.timestamp.isoformat(),
                'data': block.data,
                'previous_hash': block.previous_hash,
                'hash': block.hash,
                'nonce': block.nonce
            } for block in self.chain
        ]
        with open(self.ledger_file, 'w') as file:
            json.dump(chain_data, file, indent=2)

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, data: Dict[str, float]):
        """Adds a new block to the chain after executing smart contract"""
        try:
            # Execute smart contract on the data
            contract_result = self.smart_contract.execute(data)
            
            # Create and mine new block
            previous_block = self.get_latest_block()
            new_block = Block(
                datetime.datetime.now(),
                contract_result,
                previous_block.hash
            )
            new_block.mine_block(self.difficulty)
            
            # Add block to chain and save
            self.chain.append(new_block)
            self.save_chain()
            
            return True
        except Exception as e:
            print(f"Error adding block: {e}")
            return False

    def is_chain_valid(self) -> bool:
        """Validates the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # Verify current block's hash
            if current_block.hash != current_block.calculate_hash():
                return False

            # Verify chain linkage
            if current_block.previous_hash != previous_block.hash:
                return False

            # Verify data through smart contract
            try:
                self.smart_contract.validate_data(current_block.data['data'])
            except:
                return False

        return True

    def get_all_data(self) -> list:
        """Returns all blockchain data for the API"""
        return [{
            "timestamp": block.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "data": block.data,
            "hash": block.hash
        } for block in self.chain]

    def get_alerts(self) -> list:
        """Returns all active alerts from the last 10 blocks"""
        alerts = []
        for block in self.chain[-10:]:
            if block.data.get('alerts'):
                alerts.append({
                    'timestamp': block.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    'alerts': block.data['alerts']
                })
        return alerts