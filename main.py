import requests
uid = input('Enter ur UID: ')

url = f'https://enka.network/api/uid/{uid}/'

response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f'Error: {response.status_code}')