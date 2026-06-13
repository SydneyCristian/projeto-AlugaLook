from extensao import bd
from models.animal import Animal


class AnimalRepository:

    def cadastrar(self, nome, especie, raca, idade, descricao, usuario_id, foto=None):
        animal = Animal(
            nome=nome,
            especie=especie,
            raca=raca,
            idade=idade,
            descricao=descricao,
            foto=foto,
            status='disponivel',
            usuario_id=usuario_id
        )
        bd.session.add(animal)
        bd.session.commit()
        return animal

    def listar_animais(self):
        return Animal.query.all()

    def listar_por_dono(self, usuario_id):
        return Animal.query.filter_by(usuario_id=usuario_id).all()

    def buscar_por_id(self, id):
        return Animal.query.get(id)

    def atualizar(self, id, nome, especie, raca, idade, descricao, foto=None):
        animal = Animal.query.get(id)
        if not animal:
            return False
        animal.nome = nome or animal.nome
        animal.especie = especie or animal.especie
        animal.raca = raca or animal.raca
        animal.idade = idade or animal.idade
        animal.descricao = descricao or animal.descricao
        
        if foto is not None:
            animal.foto = foto
        bd.session.commit()
        return True

    def deletar(self, animal_ou_id):
        if isinstance(animal_ou_id, int):
            animal = Animal.query.get(animal_ou_id)
        else:
            animal = animal_ou_id
        if animal:
            bd.session.delete(animal)
            bd.session.commit()