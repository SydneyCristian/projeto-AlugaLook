from repository.solicitacao_repository import SolicitacaoRepository
from models.solicitacao import SolicitacaoAdocao


class SolicitacaoService:

    def __init__(self):

        self.repository = SolicitacaoRepository()


    def criar(
        self,
        animal_id,
        solicitante_id,
        mensagem
    ):

        solicitacao = SolicitacaoAdocao(
            animal_id=animal_id,
            solicitante_id=solicitante_id,
            mensagem=mensagem
        )

        self.repository.criar(solicitacao)
        