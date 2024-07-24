import json
import requests
import pandas as pd
from openpyxl import Workbook
import os

with open('collection.json', 'r') as file:
    collection = json.load(file)

response_dir = 'responses'
if not os.path.exists(response_dir):
    os.makedirs(response_dir)

def send_request(item):
    request_info = item['request']
    method = request_info['method']
    url = request_info['url']
    headers = {header['key']: header['value'] for header in request_info['header']}
    auth = request_info.get('auth', {})
    if auth and auth['type'] == 'bearer':
        headers['Authorization'] = f"Bearer {auth['bearer']['token']}"
    
    body = request_info.get('body', {}).get('raw', None)
    if body:
        body = json.loads(body)
    
    response = requests.request(method, url, headers=headers, json=body)
    return response

response_statistics = []

for item in collection['item']:
    response = send_request(item)
    
    response_file = os.path.join(response_dir, f"{item['name']}.json")
    with open(response_file, 'w') as file:
        file.write(response.text)
    
    response_statistics.append({
        'Request Name': item['name'],
        'URL': item['request']['url'],
        'Status Code': response.status_code,
        'Response Time (ms)': response.elapsed.total_seconds() * 1000
    })

df = pd.DataFrame(response_statistics)

excel_file = 'response_statistics.xlsx'
df.to_excel(excel_file, index=False)

print(f"Responses saved in {response_dir}")
print(f"Response statistics saved in {excel_file}")
