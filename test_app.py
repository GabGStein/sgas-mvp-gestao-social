import pytest
from app import app, db, EstoqueItem, Familia


@pytest.fixture
def client():
  app.config['TESTING'] = True
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
  with app.test_client() as client:
    with app.app_context():
      db.create_all()
      fam = Familia(nome='João Teste', cpf='000.000.000-00')
      item = EstoqueItem(nome='Arroz 5kg', quantidade=10)
      db.session.add(fam)
      db.session.add(item)
      db.session.commit()
    yield client
    with app.app_context():
      db.drop_all()


def test_index_route(client):
  response = client.get('/')
  assert response.status_code == 200
  assert b'Painel Operacional' in response.data


def test_registrar_doacao_fluxo(client):
    response = client.post(
        '/registrar',
        data={'familia_id': 1, 'item_id': 1, 'quantidade': 2},
        follow_redirects=True,
    )
    assert response.status_code == 200
    # Verifica se a página retornada contém o termo relativo à doação ou sucesso
    assert b'doacao' in response.data.lower() or b'sucesso' in response.data.lower() or b'cadastr' in response.data.lower()