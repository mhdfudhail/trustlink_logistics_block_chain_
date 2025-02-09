import json
import hashlib
import datetime
import os
from typing import Dict, Any

class SmartContract:
    def __init__(self):
        
        self.temp_range = (0, 50)        # 0°C to 50°C
        self.humidity_range = (0, 100)    # 0% to 100%
        self.air_quality_range = (0, 500) # AQI scale
        self.vibration_range = (0, 100)   # Vibration level in mm/s
        self.latitude_range = (-90, 90)   # Valid latitude range
        self.longitude_range = (-180, 180) # Valid longitude range
        
    def validate_data(self, data: Dict[str, float]) -> bool:
        
        validations = {
            'temp': lambda x: self.temp_range[0] <= x <= self.temp_range[1],
            'humidity': lambda x: self.humidity_range[0] <= x <= self.humidity_range[1],
            'air_quality': lambda x: self.air_quality_range[0] <= x <= self.air_quality_range[1],
            'vibration': lambda x: self.vibration_range[0] <= x <= self.vibration_range[1],
            'latitude': lambda x: self.latitude_range[0] <= x <= self.latitude_range[1],
            'longitude': lambda x: self.longitude_range[0] <= x <= self.longitude_range[1]
        }
        
        return all(
            validations[key](data[key])
            for key in validations
            if key in data
        )
    
    def execute(self, data: Dict[str, float]) -> Dict[str, Any]:
        
        if not self.validate_data(data):
            raise ValueError("Data validation failed")
            
        result = {
            'data': data,
            'timestamp': datetime.datetime.now().isoformat(),
            'status': self.get_status(data),
            'alerts': self.check_alerts(data)
        }
        return result
    
    def get_status(self, data: Dict[str, float]) -> str:
        
        alerts = []
        
        # Temperature and Humidity checks
        if data.get('temp', 0) > 30 and data.get('humidity', 0) > 70:
            alerts.append("High temperature and humidity")
        elif data.get('temp', 0) < 10:
            alerts.append("Low temperature")
        
        # Air Quality checks
        if data.get('air_quality', 0) > 300:
            alerts.append("Hazardous air quality")
        elif data.get('air_quality', 0) > 150:
            alerts.append("Unhealthy air quality")
        
        # Vibration checks
        if data.get('vibration', 0) > 80:
            alerts.append("Dangerous vibration levels")
        elif data.get('vibration', 0) > 50:
            alerts.append("High vibration")
        
        return "WARNING: " + "; ".join(alerts) if alerts else "Normal conditions"
    
    def check_alerts(self, data: Dict[str, float]) -> list:
        """Generates detailed alerts based on all sensor data"""
        alerts = []
        
        # Temperature alerts
        if data.get('temp', 0) > 35:
            alerts.append("Critical temperature level")
        
        # Humidity alerts
        if data.get('humidity', 0) > 90:
            alerts.append("Critical humidity level")
        
        # Air Quality alerts
        if data.get('air_quality', 0) > 400:
            alerts.append("Emergency: Severe air pollution")
        
        # Vibration alerts
        if data.get('vibration', 0) > 90:
            alerts.append("Emergency: Critical vibration levels")

            # if data.get('vibration', 0) > 90:
            # alerts.append("Emergency: Critical vibration levels")
            
        # Location-based alerts (example: if location changes significantly)
        if all(k in data for k in ['latitude', 'longitude']):
            if abs(data['latitude']) > 85 or abs(data['longitude']) > 175:
                alerts.append("Warning: Near polar/international date line region")
        
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
        
        return [{
            "timestamp": block.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "data": block.data,
            "hash": block.hash
        } for block in self.chain]

    def get_alerts(self) -> list:
        
        alerts = []
        for block in self.chain[-10:]:
            if block.data.get('alerts'):
                alerts.append({
                    'timestamp': block.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    'alerts': block.data['alerts']
                })
        return alerts