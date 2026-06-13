from repository.animal_repository import AnimalRepository
from models.animal import Animal


class AnimalService:

    def __init__(self):

        self.repository = AnimalRepository()


    def cadastrar(self, dados, usuario_id):

        animal = Animal(
            nome=dados["nome"],
            especie=dados["especie"],
            raca=dados["raca"],
            idade=dados["idade"],
            descricao=dados["descricao"],
            usuario_id=usuario_id
        )

        return self.repository.cadastrar(animal)


    def listar(self):

        return self.repository.listar()