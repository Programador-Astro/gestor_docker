from app import db

class veiculos(db.Model):
    __tablename__ = 'veiculos'

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    placa = db.Column('placa', db.String(10), unique=True, nullable=False)
    modelo = db.Column('modelo', db.String(50), nullable=False)
    ano = db.Column('ano', db.Integer, nullable=False)
    status = db.Column('status', db.Boolean, default=True)
    capacidade = db.Column('capacidade', db.Float, nullable=False)