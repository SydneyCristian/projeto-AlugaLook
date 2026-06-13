import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from extensao import bd
from controller.auth_controller import bp_auth
from controller.animal_controller import bp_animal
from controller.perfil_controller import bp_perfil
import models.usuario
import models.animal
import models.solicitacao

load_dotenv()


def criar_servidor():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = False

    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
    #CORS(app, origins="*")
    bd.init_app(app)

    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_animal)
    app.register_blueprint(bp_perfil)

    return app


if __name__ == '__main__':
    app = criar_servidor()
    with app.app_context():
        bd.create_all()
    app.run(debug=True)