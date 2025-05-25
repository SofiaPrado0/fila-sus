from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

turno = 0
atendentes = ["Atendente 1", "Atendente 2"]

class Senha(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(1), nullable=False)  # P ou N
    especialidade = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='aguardando') 
    atendente = db.Column(db.String(50), nullable=True)
    hora_criacao = db.Column(db.DateTime, default=datetime.now)
    hora_chamada = db.Column(db.DateTime, nullable=True) 

    @property
    def codigo(self):
        return f"{self.tipo}{self.numero:03d}"

    @property
    def tempo_espera(self):
        if self.hora_chamada:
            return (self.hora_chamada - self.hora_criacao).total_seconds() // 60
        return None

    def __repr__(self):
        return f'<Senha {self.codigo} - {self.especialidade}>'

def escolher_atendente():
    global turno
    atendente = atendentes[turno % len(atendentes)]
    turno += 1
    return atendente

def get_especialidades():
    return ['Clínica Geral', 'Ginecologia', 'Pediatria', 'Geriatria', 'Ortopedia']