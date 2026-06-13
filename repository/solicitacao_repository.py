from extensao import bd
from models.solicitacao import SolicitacaoAdocao
from models.animal import Animal


class SolicitacaoRepository:

    def listar_minhas_solicitacoes(self, usuario_id):
        return (
            SolicitacaoAdocao.query
            .filter_by(solicitante_id=usuario_id)
            .all()
        )

    def listar_pendentes_do_dono(self, usuario_id):
        return (
            SolicitacaoAdocao.query
            .join(Animal, Animal.id == SolicitacaoAdocao.animal_id)
            .filter(
                Animal.usuario_id == usuario_id,
                SolicitacaoAdocao.status == "pendente"
            )
            .all()
        )

    def listar_aprovadas_do_dono(self, usuario_id):
        return (
            SolicitacaoAdocao.query
            .join(Animal, Animal.id == SolicitacaoAdocao.animal_id)
            .filter(
                Animal.usuario_id == usuario_id,
                SolicitacaoAdocao.status == "aprovada"
            )
            .all()
        )

    def listar_notificacoes(self, usuario_id):
        return (
            SolicitacaoAdocao.query
            .filter(
                SolicitacaoAdocao.solicitante_id == usuario_id,
                SolicitacaoAdocao.vista == False,
                SolicitacaoAdocao.status.in_(["aprovada", "recusada"])
            )
            .all()
        )

    def marcar_notificacoes_vistas(self, usuario_id):
        
        SolicitacaoAdocao.query.filter(
            SolicitacaoAdocao.solicitante_id == usuario_id,
            SolicitacaoAdocao.vista == False
        ).update({SolicitacaoAdocao.vista: True})
        bd.session.commit()

    def buscar_por_animal_e_solicitante(self, animal_id, solicitante_id):
        return SolicitacaoAdocao.query.filter_by(
            animal_id=animal_id,
            solicitante_id=solicitante_id
        ).first()

    def cadastrar(self, solicitacao):
        bd.session.add(solicitacao)
        bd.session.commit()
        return solicitacao

    def buscar_por_id(self, id):
        return SolicitacaoAdocao.query.get(id)

    def atualizar(self):
        bd.session.commit()

    def deletar(self, solicitacao):
        bd.session.delete(solicitacao)
        bd.session.commit()

    def criar(self, animal_id, solicitante_id, tem_espaco, tem_tempo, tem_condicoes, mensagem):
        solicitacao = SolicitacaoAdocao(
            animal_id=animal_id,
            solicitante_id=solicitante_id,
            tem_espaco=tem_espaco,
            tem_tempo=tem_tempo,
            tem_condicoes=tem_condicoes,
            mensagem=mensagem,
            status="pendente",
            vista=True
        )
        bd.session.add(solicitacao)
        bd.session.commit()
        return True, "Solicitação enviada com sucesso"

    def aprovar(self, id, usuario_id):
        solicitacao = SolicitacaoAdocao.query.get(id)
        if not solicitacao:
            return False, "Solicitação não encontrada"
        if solicitacao.animal.usuario_id != usuario_id:
            return False, "Sem permissão"
        solicitacao.status = "aprovada"
        solicitacao.vista = False  
        solicitacao.animal.status = "adotado"
        bd.session.commit()
        return True, "Solicitação aprovada!"

    def recusar(self, id, usuario_id):
        solicitacao = SolicitacaoAdocao.query.get(id)
        if not solicitacao:
            return False, "Solicitação não encontrada"
        if solicitacao.animal.usuario_id != usuario_id:
            return False, "Sem permissão"
        solicitacao.status = "recusada"
        solicitacao.vista = False  
        bd.session.commit()
        return True, "Solicitação recusada."