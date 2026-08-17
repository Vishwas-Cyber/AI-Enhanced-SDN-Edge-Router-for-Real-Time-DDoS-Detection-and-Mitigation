from fastapi.testclient import TestClient
from api.main import app

client=TestClient(app)

def test_health():
    assert client.get('/health').status_code==200

def test_login_and_events():
    r=client.post('/auth/login',json={'username':'analyst','password':'change-me-now'})
    assert r.status_code==200
    token=r.json()['access_token']
    assert client.get('/events',headers={'Authorization':f'Bearer {token}'}).status_code==200

def test_unauthorized_topology():
    assert client.get('/topology').status_code==401
