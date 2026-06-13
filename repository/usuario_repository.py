from extensao import bd
from models.usuario import Usuario


class UsuarioRepository:

    def cadastrar(self, usuario):
        bd.session.add(usuario)
        bd.session.commit()
        return usuario

    def buscar_por_email(self, email):
        return Usuario.query.filter_by(email=email).first()

    def buscar_por_id(self, id):
        return Usuario.query.get(id)

    def verificar_login(self, email, senha):
        return Usuario.query.filter_by(email=email, senha=senha).first()

    def atualizar(self, id, nome, email, telefone):
        usuario = Usuario.query.get(id)
        if not usuario:
            return False
        if email and email != usuario.email:
            existente = Usuario.query.filter_by(email=email).first()
            if existente:
                return False
        if nome:
            usuario.nome = nome
        if email:
            usuario.email = email
        if telefone:
            usuario.telefone = telefone
        bd.session.commit()
        return True

    def atualizar_senha(self, id, nova_senha):
        usuario = Usuario.query.get(id)
        if usuario:
            usuario.senha = nova_senha
            bd.session.commit()

    def atualizar_foto(self, id, foto):
        usuario = Usuario.query.get(id)
        if usuario:
            usuario.foto = foto
            bd.session.commit()
            return True
        return False