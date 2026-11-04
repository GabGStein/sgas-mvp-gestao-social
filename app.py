from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-sgas-mvp'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sgas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# --- MODELOS ---
class Familia(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  nome = db.Column(db.String(100), nullable=False)
  cpf = db.Column(db.String(14), unique=True, nullable=False)


class EstoqueItem(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  nome = db.Column(db.String(100), nullable=False)
  quantidade = db.Column(db.Integer, default=0)


class Doacao(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  familia_id = db.Column(db.Integer, db.ForeignKey('familia.id'), nullable=False)
  item_id = db.Column(
      db.Integer, db.ForeignKey('estoque_item.id'), nullable=False
  )
  quantidade = db.Column(db.Integer, nullable=False)

  familia = db.relationship('Familia', backref=db.backref('doacoes', lazy=True))
  item = db.relationship(
      'EstoqueItem', backref=db.backref('doacoes', lazy=True)
  )


# --- ROTAS ---
@app.route('/')
def index():
  familias = Familia.query.all()
  itens = EstoqueItem.query.all()
  doacoes = Doacao.query.order_by(Doacao.id.desc()).all()
  return render_template(
      'index.html', familias=familias, itens=itens, doacoes=doacoes
  )


@app.route('/registrar', methods=['POST'])
def registrar_doacao():
  try:
    familia_id = int(request.form.get('familia_id'))
    item_id = int(request.form.get('item_id'))
    quantidade = int(request.form.get('quantidade'))
  except (TypeError, ValueError):
    flash('Dados de entrada inválidos.', 'erro')
    return redirect(url_for('index'))

  # Refatoração SQLAlchemy 2.0: uso de db.session.get() em vez de query.get()
  item = db.session.get(EstoqueItem, item_id)
  familia = db.session.get(Familia, familia_id)

  if not item or not familia:
    flash('Família ou item não encontrado no sistema.', 'erro')
    return redirect(url_for('index'))

  if quantidade <= 0:
    flash('A quantidade doada deve ser maior que zero.', 'erro')
    return redirect(url_for('index'))

  if item.quantidade < quantidade:
    flash(
        f'Estoque insuficiente! Apenas {item.quantidade} unidades disponíveis'
        ' para este item.',
        'erro',
    )
    return redirect(url_for('index'))

  # Atualização de estoque e registro de doação
  item.quantidade -= quantidade
  nova_doacao = Doacao(
      familia_id=familia_id, item_id=item_id, quantidade=quantidade
  )

  db.session.add(nova_doacao)
  db.session.commit()

  flash(
      f'Sucesso! Registrada a doação de {quantidade} unidade(s) de {item.nome}'
      f' para {familia.nome}. Estoque restante: {item.quantidade} unidades.',
      'sucesso',
  )
  return redirect(url_for('index'))


if __name__ == '__main__':
  with app.app_context():
    db.create_all()
  app.run(debug=True)