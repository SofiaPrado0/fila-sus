from flask import *
import random

app = Flask(__name__)

# Dados principais
especialidades = {
    'Clínica Geral': list(range(1, 61)),
    'Ginecologia': list(range(1, 41)),
    'Pediatria': list(range(1, 41)),
    'Geriatria': list(range(1, 41)),
    'Ortopedia': list(range(1, 41))
}

fila_preferencial = {esp: [] for esp in especialidades}
fila_normal = {esp: [] for esp in especialidades}

atendentes = ["Atendente 1", "Atendente 2"]
turno = 0

# Lista para monitor (últimas senhas chamadas)
ultimas_senhas = []

@app.route("/", methods=["GET", "POST"])
def index():
    global turno

    if request.method == "POST":
        especialidade = request.form['especialidade']
        tipo = int(request.form['tipo'])

        if especialidades[especialidade]:
            numero_senha = especialidades[especialidade].pop(0)
            tipo_senha = "P" if tipo == 1 else "N"
            senha_usuario = f"{tipo_senha}{numero_senha:03d}"

            if tipo == 1:
                fila_preferencial[especialidade].append(senha_usuario)
            else:
                fila_normal[especialidade].append(senha_usuario)

            return render_template('index.html', senha=senha_usuario, especialidade=especialidade)

        else:
            return render_template('index.html', mensagem="Não há mais senhas disponíveis para essa especialidade.")

    senha_chamada = None
    if request.args.get("chamar"):
        senha_chamada = chamar_proxima_senha()

    return render_template("index.html", senha_chamada=senha_chamada)

@app.route("/monitor")
def monitor():
    return render_template("monitor.html", senhas=ultimas_senhas)

def chamar_proxima_senha():
    global turno

    for esp in especialidades:
        if fila_preferencial[esp]:
            senha = fila_preferencial[esp].pop(0)
            tipo = "Preferencial"
        elif fila_normal[esp]:
            senha = fila_normal[esp].pop(0)
            tipo = "Normal"
        else:
            continue

        atendente = atendentes[turno % 2]
        turno += 1

        registro = {
            "senha": senha,
            "especialidade": esp,
            "tipo": tipo,
            "atendente": atendente
        }

        ultimas_senhas.insert(0, registro)  # adiciona no início
        ultimas_senhas[:] = ultimas_senhas[:10]  # mantém só os 10 últimos

        return f"Senha chamada: {senha} (Especialidade: {esp}) - Atendente: {atendente}"

    return "Não há senhas para chamar no momento."

if __name__ == "__main__":
    app.run(debug=True)
