
import os
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy


# ==========================================
# CONFIGURAÇÃO DA APLICAÇÃO
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

# No Vercel, utilizar /tmp.
# Localmente, utilizar o banco na pasta do projeto.
IS_VERCEL = bool(os.environ.get("VERCEL"))

if IS_VERCEL:
    DB_PATH = "/tmp/sgas.db"
else:
    DB_PATH = str(BASE_DIR / "sgas.db")


app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "chave-secreta-sgas-mvp"
)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{DB_PATH}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ==========================================
# MODELOS
# ==========================================

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
    familia_id = db.Column(
        db.Integer,
        db.ForeignKey("familia.id"),
        nullable=False
    )
    item_id = db.Column(
        db.Integer,
        db.ForeignKey("estoque_item.id"),
        nullable=False
    )
    quantidade = db.Column(db.Integer, nullable=False)

    familia = db.relationship(
        "Familia",
        backref=db.backref("doacoes", lazy=True)
    )

    item = db.relationship(
        "EstoqueItem",
        backref=db.backref("doacoes", lazy=True)
    )


# ==========================================
# INICIALIZAÇÃO DO BANCO
# ==========================================

def inicializar_banco():
    with app.app_context():

        db.create_all()

        # Famílias iniciais
        if not Familia.query.first():
            db.session.add_all([
                Familia(
                    nome="Família Silva",
                    cpf="123.456.789-01"
                ),
                Familia(
                    nome="Família Santos",
                    cpf="987.654.321-02"
                ),
                Familia(
                    nome="Família Oliveira",
                    cpf="456.789.123-03"
                )
            ])

        # Itens iniciais
        if not EstoqueItem.query.first():
            db.session.add_all([
                EstoqueItem(
                    nome="Cesta Básica",
                    quantidade=50
                ),
                EstoqueItem(
                    nome="Kit de Higiene",
                    quantidade=30
                ),
                EstoqueItem(
                    nome="Água Mineral (1.5L)",
                    quantidade=100
                )
            ])

        db.session.commit()


# Inicializa quando o Vercel importa a aplicação
inicializar_banco()


# ==========================================
# ROTAS
# ==========================================

@app.route("/")
def index():

    familias = Familia.query.all()
    itens = EstoqueItem.query.all()
    doacoes = Doacao.query.order_by(
        Doacao.id.desc()
    ).all()

    return render_template(
        "index.html",
        familias=familias,
        itens=itens,
        doacoes=doacoes
    )


@app.route("/registrar", methods=["GET", "POST"])
def registrar_doacao():

    if request.method == "POST":

        familia_id = request.form.get(
            "familia_id",
            type=int
        )

        item_id = request.form.get(
            "item_id",
            type=int
        )

        quantidade = request.form.get(
            "quantidade",
            type=int
        )

        item = db.session.get(EstoqueItem, item_id)
        familia = db.session.get(Familia, familia_id)

        if not item or not familia:
            flash(
                "Família ou item não encontrado no sistema.",
                "erro"
            )
            return redirect(url_for("registrar_doacao"))

        if not quantidade or quantidade <= 0:
            flash(
                "A quantidade doada deve ser maior que zero.",
                "erro"
            )
            return redirect(url_for("registrar_doacao"))

        if item.quantidade < quantidade:
            flash(
                f"Estoque insuficiente! Apenas "
                f"{item.quantidade} unidades disponíveis "
                "para este item.",
                "erro"
            )
            return redirect(url_for("registrar_doacao"))

        # Atualização do estoque
        item.quantidade -= quantidade

        # Registro da doação
        nova_doacao = Doacao(
            familia_id=familia_id,
            item_id=item_id,
            quantidade=quantidade
        )

        db.session.add(nova_doacao)
        db.session.commit()

        return redirect(
            url_for(
                "sucesso_doacao",
                doacao_id=nova_doacao.id
            )
        )

    familias = Familia.query.all()
    itens = EstoqueItem.query.all()

    return render_template(
        "form_registro.html",
        familias=familias,
        itens=itens
    )


@app.route("/sucesso/<int:doacao_id>")
def sucesso_doacao(doacao_id):

    doacao = db.session.get(Doacao, doacao_id)

    if not doacao:
        flash(
            "Registro de doação não encontrado.",
            "erro"
        )
        return redirect(url_for("index"))

    return render_template(
        "resultado.html",
        doacao=doacao
    )


# ==========================================
# EXECUÇÃO LOCAL
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
