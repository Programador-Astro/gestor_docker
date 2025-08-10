from app import db

class Clientes(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    codigo_cliente = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    uf = db.Column(db.String(2), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)
    def __repr__(self):
        return f'<Cliente {self.nome}>'
    
class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    codigo_pedido = db.Column(db.String(10), unique=True, nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    data_pedido = db.Column(db.DateTime)
    nome_arquivo_original = db.Column(db.String(255))
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    produtos = db.relationship('PedidoProduto', backref='pedido', lazy=True)


class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    preco = db.Column(db.Numeric(10, 2))
    pedidos = db.relationship('PedidoProduto', backref='produto', lazy=True)

class PedidoProduto(db.Model):
    __tablename__ = 'pedido_produto'
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), primary_key=True)
    quantidade = db.Column(db.Numeric(10,3), nullable=False)