# Importações
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

# Configurando o site
app = Flask(__name__)
app.config['SECRET_KEY'] = '843d8e919bc5f85bbd74baced0fafa95'
if os.getenv('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///SiteBatePapo.db'

# Criar banco de dados
database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'É necessário fazer o login antes de acessar essa página'
login_manager.login_message_category = 'alert-info'


# Importando as páginas do site para criar a conexão
from sitebatepapo import paginas