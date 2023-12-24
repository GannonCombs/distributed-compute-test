import requests
import uuid

device_id = str(uuid.uuid4())
server_url = 'http://localhost:5000'

def register():
    payload = {'device_id': device_id}
    response = requests.post(f'{server_url}/register', json=payload)
    print(response.json())
    return device_id

def deregister():
    payload = {'device_id': device_id}
    response = requests.post(f'{server_url}/deregister', json=payload)
    print(response.json())

def request_data():
    response = requests.get(f'{server_url}/get_data')
    data = response.json()
    return data['numbers']

def perform_computation(device_id, numbers):
    squared_numbers = [number ** 2 for number in numbers]
    response = requests.post(f'{server_url}/compute', json={'device_id': device_id, 'squared_numbers': squared_numbers})
    print(response.json())

if __name__ == '__main__':
    device_id = register()

    numbers = request_data()

    perform_computation(device_id, numbers)

    deregister()
