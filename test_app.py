import pytest
from main import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_registrar_doacao_fluxo(client):
    response = client.post(
        '/registrar',
        data={'familia_id': 1, 'item_id': 1, 'quantidade': 2},
        follow_redirects=True,
    )
    assert response.status_code == 200