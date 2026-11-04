# SGAS — Sistema de Gestão e Apoio Social (MVP)

O **SGAS** é uma solução web monolítica desenvolvida em Flask, SQLAlchemy e Tailwind CSS para otimizar a distribuição de mantimentos, controle de estoque e registro de atendimentos em instituições e associações comunitárias.

---

## 🚀 Tecnologias Utilizadas

- **Backend:** Python 3.11+, Flask, Flask-SQLAlchemy
- **Frontend:** HTML5, Tailwind CSS, Jinja2 Templates
- **Acessibilidade:** Padrões WCAG 2.1 AA (Alto contraste, alvos de toque ≥ 44x44px, rótulos persistentes e redundância de estados)
- **Testes & CI:** Pytest, GitHub Actions

---

## 📋 Funcionalidades do MVP (Fluxo de 3 Telas)

1. **Tela 1 — Entrada Principal (Dashboard):** Visão geral de métricas de estoque e acesso ao fluxo prioritário de doações.
2. **Tela 2 — Formulário de Registro:** Form de baixa de estoque e vinculação com famílias cadastradas, com validação no servidor.
3. **Tela 3 — Alertas, Histórico e Validação:** Notificação visual/acessível de confirmação de entrega e consulta de histórico recente.

---

## 🛠️ Como Executar o Projeto Localmente

```bash
# 1. Clonar o repositório
git clone [https://github.com/GabGStein/sgas-mvp-gestao-social.git](https://github.com/GabGStein/sgas-mvp-gestao-social.git)

# 2. Acessar o diretório
cd sgas-mvp-gestao-social

# 3. Criar e ativar ambiente virtual
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# 4. Instalar as dependências
pip install -r requirements.txt

# 5. Executar a aplicação
python app.py
