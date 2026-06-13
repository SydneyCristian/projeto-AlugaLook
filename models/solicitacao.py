from extensao import bd
from datetime import datetime


class SolicitacaoAdocao(bd.Model):

    __tablename__ = "solicitacoes_adocao"

    id = bd.Column(
        bd.Integer,
        primary_key=True
    )

    animal_id = bd.Column(
        bd.Integer,
        bd.ForeignKey("animais.id"),
        nullable=False
    )

    solicitante_id = bd.Column(
        bd.Integer,
        bd.ForeignKey("usuarios.id"),
        nullable=False
    )

    tem_espaco = bd.Column(
        bd.Boolean,
        default=False
    )

    tem_tempo = bd.Column(
        bd.Boolean,
        default=False
    )

    tem_condicoes = bd.Column(
        bd.Boolean,
        default=False
    )

    mensagem = bd.Column(
        bd.Text
    )

    status = bd.Column(
        bd.String(20),
        default="pendente"
    )

    
    vista = bd.Column(
        bd.Boolean,
        default=True
    )

    data_criacao = bd.Column(
        bd.DateTime,
        default=datetime.utcnow
    )

    animal = bd.relationship("Animal", backref="solicitacoes", lazy=True)
    solicitante = bd.relationship("Usuario", backref="solicitacoes", lazy=True)