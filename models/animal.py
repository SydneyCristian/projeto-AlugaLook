from extensao import bd


class Animal(bd.Model):
    __tablename__ = "animais"

    id = bd.Column(bd.Integer, primary_key=True)

    nome = bd.Column(bd.String(100), nullable=False)
    especie = bd.Column(bd.String(100), nullable=False)
    raca = bd.Column(bd.String(100))
    idade = bd.Column(bd.Integer)
    descricao = bd.Column(bd.String(255))
    foto = bd.Column(bd.Text)

    status = bd.Column(
        bd.String(20),
        default="disponivel"
    )

    usuario_id = bd.Column(
        bd.Integer,
        bd.ForeignKey("usuarios.id")
    )

    def __repr__(self):
        return f"<Animal {self.nome}>"