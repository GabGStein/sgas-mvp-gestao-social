import osgit add main.py
git commit -m "fix(main): import render_template from flask"
git push origin main
from flask import Flask, render_template, request, redirect, url_for # Certifique-se de incluir render_template aqui

# 1. PRIMEIRO: Inicialize a aplicação Flask
app = Flask(__name__)

# 2. SEGUNDO: Configure o caminho do banco (usando /tmp na Vercel)
if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    db_path = '/tmp/sgas.db'
else:
    db_path = 'sgas.db'

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. TERCEIRO: Inicialize o SQLAlchemy e defina suas rotas
db = SQLAlchemy(app)

# Restante do seu código (Modelos, Rotas, etc.)...

# Define o caminho do banco: se estiver na Vercel, usa /tmp, senão usa o diretório local
if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    db_path = '/tmp/sgas.db'
else:
    db_path = 'sgas.db'

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

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
    item_id = db.Column(db.Integer, db.ForeignKey('estoque_item.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)

    familia = db.relationship('Familia', backref=db.backref('doacoes', lazy=True))
    item = db.relationship('EstoqueItem', backref=db.backref('doacoes', lazy=True))


# --- ROTAS ---
@app.route('/')
def index():
    familias = Familia.query.all()
    itens = EstoqueItem.query.all()
    doacoes = Doacao.query.order_by(Doacao.id.desc()).all()
    return render_template(
        'index.html', familias=familias, itens=itens, doacoes=doacoes
    )


@app.route('/registrar', methods=['GET', 'POST'])
def registrar_doacao():
    if request.method == 'POST':
        familia_id = request.form.get('familia_id', type=int)
        item_id = request.form.get('item_id', type=int)
        quantidade = request.form.get('quantidade', type=int)

        item = db.session.get(EstoqueItem, item_id)
        familia = db.session.get(Familia, familia_id)

        if not item or not familia:
            flash('Família ou item não encontrado no sistema.', 'erro')
            return redirect(url_for('registrar_doacao'))

        if not quantidade or quantidade <= 0:
            flash('A quantidade doada deve ser maior que zero.', 'erro')
            return redirect(url_for('registrar_doacao'))

        if item.quantidade < quantidade:
            flash(
                f'Estoque insuficiente! Apenas {item.quantidade} unidades disponíveis para este item.',
                'erro',
            )
            return redirect(url_for('registrar_doacao'))

        # Atualização do estoque e gravação da doação
        item.quantidade -= quantidade
        nova_doacao = Doacao(
            familia_id=familia_id, item_id=item_id, quantidade=quantidade
        )

        db.session.add(nova_doacao)
        db.session.commit()

        # Redireciona para a terceira tela (resultado/confirmação)
        return redirect(url_for('sucesso_doacao', doacao_id=nova_doacao.id))

    familias = Familia.query.all()
    itens = EstoqueItem.query.all()
    return render_template('form_registro.html', familias=familias, itens=itens)


@app.route('/sucesso/<int:doacao_id>')
def sucesso_doacao(doacao_id):
    doacao = db.session.get(Doacao, doacao_id)
    if not doacao:
        flash('Registro de doação não encontrado.', 'erro')
        return redirect(url_for('index'))
    return render_template('resultado.html', doacao=doacao)


if __name__ == '__main__':
    with app.app_context():
        # Cria as tabelas se não existirem
        db.create_all()
        
        # Insere famílias padrão caso a tabela esteja vazia
        if not Familia.query.first():
            db.session.add_all([
                Familia(nome="Família Silva", cpf="123.456.789-01"),
                Familia(nome="Família Santos", cpf="987.654.321-02"),
                Familia(nome="Família Oliveira", cpf="456.789.123-03")
            ])
        
        # Insere itens iniciais no estoque caso a tabela esteja vazia
        if not EstoqueItem.query.first():
            db.session.add_all([
                EstoqueItem(nome="Cesta Básica", quantidade=50),
                EstoqueItem(nome="Kit de Higiene", quantidade=30),
                EstoqueItem(nome="Água Mineral (1.5L)", quantidade=100)
            ])
            
        db.session.commit()
        
    app.run(debug=True)