import os
from app.api import app
from fastapi.testclient import TestClient

# Configure base path from environment or default in config
os.environ.setdefault('FINDER_BASE_PATH', r'C:\Recordings')

client = TestClient(app)

r = client.get('/health')
print('HEALTH', r.status_code, r.json())

r = client.get('/search', params={'numero': '11999999999', 'month': '2025-01'})
print('SEARCH', r.status_code, r.json().get('count'), 'items')

items = r.json().get('items', [])
if items:
    p = items[0]['path']
    r2 = client.get('/download', params={'path': p})
    print('DOWNLOAD', r2.status_code, len(r2.content))
else:
    print('DOWNLOAD skipped: no items')
