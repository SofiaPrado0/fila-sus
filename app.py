from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models import db, Senha, get_especialidades, escolher_atendente
import os
from pathlib import Path

app = Flask(__name__)

instance_path = Path(__file__).parent / "instance"
instance_path.mkdir(exist_ok=True) 
db_path = instance_path / "senhas.db"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    try:
        db.create_all()
        print(f"Banco de dados criado com sucesso em: {db_path}")
    except Exception as e:
        print(f"Erro ao criar banco de dados: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        especialidade = request.form['especialidade']
        tipo = request.form['tipo']  

        tipo_letra = 'P' if tipo == '1' else 'N'

        try:
            ultima = (Senha.query
                      .filter_by(especialidade=especialidade, tipo=tipo_letra)
                      .order_by(Senha.numero.desc())
                      .first())
            numero = (ultima.numero + 1) if ultima else 1

            senha = Senha(
                numero=numero,
                tipo=tipo_letra,
                especialidade=especialidade,
                hora_criacao=datetime.now(),
                status='aguardando'
            )
            db.session.add(senha)
            db.session.commit()

            return render_template('index.html', 
                                 senha=senha.codigo, 
                                 especialidade=especialidade,
                                 especialidades=get_especialidades())

        except Exception as e:
            print(f"Erro ao gerar senha: {e}")
            return "Erro ao processar sua solicitação", 500

    senha_chamada = None
    if request.args.get("chamar"):
        senha_chamada = chamar_proxima()

    return render_template('index.html', 
                         senha_chamada=senha_chamada, 
                         especialidades=get_especialidades())

@app.route("/monitor")
def monitor():
    try:
        ultimas = (Senha.query
                   .filter(Senha.status == 'chamada')
                   .order_by(Senha.tipo.desc(), Senha.hora_chamada.desc())
                   .limit(10)
                   .all())
        return render_template("monitor.html", senhas=ultimas)
    except Exception as e:
        print(f"Erro ao acessar monitor: {e}")
        return "Erro ao carregar o monitor", 500

def chamar_proxima():
    try:
        senha = (Senha.query
                 .filter_by(status='aguardando', tipo='P')
                 .order_by(Senha.hora_criacao)
                 .first())

        if not senha:
            senha = (Senha.query
                     .filter_by(status='aguardando', tipo='N')
                     .order_by(Senha.hora_criacao)
                     .first())

        if senha:
            senha.status = 'chamada'
            senha.atendente = escolher_atendente()
            senha.hora_chamada = datetime.now()
            db.session.commit()

            return f"Senha chamada: {senha.codigo} (Especialidade: {senha.especialidade}) - Atendente: {senha.atendente}"

        return "Não há senhas para chamar no momento."
    except Exception as e:
        print(f"Erro ao chamar próxima senha: {e}")
        return "Erro no sistema de chamada", 500

if __name__ == "__main__":
    app.run(debug=True)