from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_mail import Mail

db = SQLAlchemy()
cors = CORS()
login_manager = LoginManager()  
jwtmanager  = JWTManager()
migrate = Migrate()
mail = Mail()