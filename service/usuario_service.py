from repository.usuario_repository import UsuarioRepository
from models.usuario import Usuario


class UsuarioService:

    def __init__(self):
        self.repository = UsuarioRepository()

    def cadastrar(self, dados):
        usuario = Usuario(
            nome=dados["nome"],
            email=dados["email"],
            senha=dados["senha"],
            telefone=dados["telefone"]
        )
        self.repository.cadastrar(usuario)

    def login(self, email, senha):
        return self.repository.verificar_login(email, senha)