from flask import Flask, request, jsonify
import json

app = Flask(__name__)

devices = {}

@app.route('/register', methods=['POST'])
def register_device():
    device_data = request.json
    device_id = device_data['device_id']
    devices[device_id] = device_data
    return json.dumps({'result': 'success', 'device_id': device_id}), 200

@app.route('/deregister', methods=['POST'])
def deregister_device():
    device_data = request.json
    device_id = device_data['device_id']
    if device_id in devices:
        del devices[device_id]
        return json.dumps({'result': 'success', 'device_id': device_id}), 200
    else:
        return json.dumps({'result': 'error', 'message': 'device_id not found'}), 404
    
@app.route('/get_data', methods=['GET'])
def get_data():
    #This would be passed to the http_server from the computer needing computation.
    numbers = [1, 2, 3, 4, 5]
    return jsonify({'numbers': numbers})

@app.route('/compute', methods=['POST'])
def perform_computation():
    device_id = request.json['device_id']
    squared_numbers = request.json['squared_numbers']
    print(f"Received squared numbers from device {device_id}: {squared_numbers}")
    return jsonify({'status': 'success', 'message': 'Squared numbers received.'})


if __name__ == '__main__':
    app.run()
