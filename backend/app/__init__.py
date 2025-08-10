from flask import Flask, jsonify
from .extensions import mail, cors, db, migrate, login_manager, jwtmanager
from .models import users, clientes, veiculos
from .blueprints import register_blueprints
def create_app():
    app = Flask(__name__)
    
    #Inicialização das dependências
    app.config.from_object('app.config.Config')
    cors.init_app(app, origins="*")
    db.init_app(app)
    migrate.init_app(app, db)   
    login_manager.init_app(app)
    mail.init_app(app)
    jwtmanager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id): 
        return users.Usuario.query.get(int(user_id))
    @app.route('/', methods=['GET'])
    def index():
        return "OK"

    with app.app_context():
        db.create_all()

    register_blueprints(app)
    return app


