from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sgas.db'
app.config['SECRET_KEY'] = 'chave-secreta-sgas-mvp'
db = SQLAlchemy(app)


# Modelos do Banco de Dados
class Familia(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  nome = db.Column(db.String(100), nullable=False)
  cpf = db.Column(db.String(14), unique=True, nullable=False)


class EstoqueItem(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  nome = db.Column(db.String(100), nullable=False)
  quantidade = db.Column(db.Integer, nullable=False)


class Doacao(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  familia_id = db.Column(
      db.Integer, db.ForeignKey('familia.id'), nullable=False
  )
  item_id = db.Column(db.Integer, db.ForeignKey('estoque_item.id'), nullable=False)
  quantidade_entregue = db.Column(db.Integer, nullable=False)
  data_entrega = db.Column(db.DateTime, default=datetime.utcnow)

  familia = db.relationship('Familia', backref=db.backref('doacoes', lazy=True))
  item = db.relationship('EstoqueItem', backref=db.backref('doacoes', lazy=True))


# Rotas da Aplicação (Fluxo de 3 Telas)
@app.route('/')
def index():
  estoque = EstoqueItem.query.all()
  return render_template('index.html', estoque=estoque)


@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
  familias = Familia.query.all()
  itens = EstoqueItem.query.all()

  if request.method == 'POST':
    familia_id = request.form.get('familia_id')
    item_id = request.form.get('item_id')
    qtd = int(request.form.get('quantidade', 0))

    item = EstoqueItem.query.get(item_id)
    if item and item.quantidade >= qtd:
      item.quantidade -= qtd
      nova_doacao = Doacao(
          familia_id=familia_id, item_id=item_id, quantidade_entregue=qtd
      )
      db.session.add(nova_doacao)
      db.session.commit()
      return redirect(url_for('resultado', doacao_id=nova_doacao.id))
    else:
      flash('Erro: Quantidade solicitada maior que o saldo em estoque!', 'error')

  return render_template(
      'form_registro.html', familias=familias, itens=itens
  )


@app.route('/resultado/<int:doacao_id>')
def resultado(doacao_id):
  doacao = Doacao.query.get_or_404(doacao_id)
  return render_template('resultado.html', doacao=doacao)


if __name__ == '__main__':
  with app.app_context():
    db.create_all()
    if not Familia.query.first():
      db.session.add(
          Familia(nome='Maria das Dores Silva', cpf='123.456.789-00')
      )
      db.session.add(EstoqueItem(nome='Cesta Básica Tipo 1', quantidade=15))
      db.session.commit()
  app.run(debug=True)