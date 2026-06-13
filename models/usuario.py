from extensao import bd
from flask_login import UserMixin


class Usuario(bd.Model, UserMixin):

    __tablename__ = "usuarios"

    id = bd.Column(
        bd.Integer,
        primary_key=True
    )

    nome = bd.Column(
        bd.String(100),
        nullable=False
    )

    email = bd.Column(
        bd.String(100),
        unique=True
    )

    senha = bd.Column(
        bd.String(100)
    )

    telefone = bd.Column(
        bd.String(20)
    )

    
    foto = bd.Column(bd.Text)

    animais = bd.relationship(
        "Animal",
        backref="usuario",
        lazy=True
    )

    def get_id(self):
        return str(self.id)